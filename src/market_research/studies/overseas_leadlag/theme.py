"""Retrospective semiconductor theme increments; never a daily forecast."""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .models import DOMESTIC, paired_summary, predict, purged_train
from .proxy import simulate
from .run import prepare, targets
from .timing import align_external, load_daily, validate_prices

BASELINE = DOMESTIC + ['spx']
SCHEMA = 'overseas_theme_evidence.v1'


def beta_residual(train, test):
    """Fit intercept and SPX beta exclusively in the training window."""
    x = np.column_stack([np.ones(len(train)), train.spx])
    coefficients = np.linalg.lstsq(x, train.theme, rcond=None)[0]
    z = np.column_stack([np.ones(len(test)), test.spx])
    return train.theme.to_numpy() - x @ coefficients, test.theme.to_numpy() - z @ coefficients


def walk_forward_theme(frame, start_year=2020):
    clean = frame.dropna(subset=BASELINE + ['theme', 'y', 'label_end_utc']).copy()
    forecasts, folds = [], []
    for year in range(start_year, int(clean.date.dt.year.max()) + 1):
        test = clean[clean.date.dt.year == year].copy()
        if test.empty:
            continue
        train = purged_train(clean, test.decision_utc.iloc[0]).copy()
        if len(train) < 252:
            continue
        train['theme_beta_residual'], test['theme_beta_residual'] = beta_residual(train, test)
        test['global'] = predict(train, test, BASELINE)
        test['theme_residual'] = predict(train, test, BASELINE + ['theme_beta_residual'])
        test['fold'] = year
        forecasts.append(test)
        folds.append({'year': year, 'train_n': len(train), 'test_n': len(test),
                      'last_training_label_utc': str(train.label_end_utc.max()),
                      'test_first_decision_utc': str(test.decision_utc.iloc[0])})
    if not forecasts:
        raise ValueError('No folds with 252 training rows')
    return pd.concat(forecasts, ignore_index=True), folds


def validate_evidence(value):
    """Reject incomplete, untraceable or forecast-shaped publication artifacts."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    public_fields = {'schema_version', 'study_id', 'generated_at_utc', 'source_revision',
                     'decision_time_local', 'decision_timezone', 'evidence_status',
                     'historical_pit_certified', 'sample_start', 'sample_end',
                     'source_sha256', 'sources', 'comparisons', 'limitations'}
    require(set(value) <= public_fields, 'Unknown public fields')
    require(value.get('schema_version') == SCHEMA, 'Unsupported schema')
    require(value.get('evidence_status') == 'retrospective_exploratory', 'Not retrospective')
    require(value.get('historical_pit_certified') is False, 'PIT must remain uncertified')
    require(value.get('decision_time_local') == '08:45', 'Wrong decision cutoff')
    require(value.get('decision_timezone') == 'Asia/Shanghai', 'Wrong decision zone')
    require(bool(re.fullmatch('[0-9a-f]{40}', value.get('source_revision', ''))), 'Invalid revision')
    require(bool(value.get('study_id')), 'Missing study ID')
    stamp = datetime.fromisoformat(value['generated_at_utc'])
    require(stamp.utcoffset() is not None and stamp.utcoffset().total_seconds() == 0,
            'Generation time must be UTC')
    require(date.fromisoformat(value['sample_start']) <= date.fromisoformat(value['sample_end']),
            'Invalid sample interval')
    hashes = value.get('source_sha256', {})
    require(bool(hashes), 'Missing hashes')
    require(all(re.fullmatch('[0-9a-f]{64}', h) for h in hashes.values()), 'Invalid hash')
    sources = value.get('sources', {})
    require(set(sources) == set(hashes), 'Source IDs differ')
    for key, source in sources.items():
        require(set(source) <= {'url', 'sha256'}, 'Unknown source fields')
        require(source['sha256'] == hashes[key], 'Source hash mismatch')
        require(source['url'].startswith(('https://', 'http://')), 'Missing source URL')
    require(bool(value.get('limitations')), 'Missing limitations')
    require(bool(value.get('comparisons')), 'Missing comparisons')
    ids = set()
    for row in value['comparisons']:
        require(set(row) <= {'evidence_id', 'source_ids', 'target', 'outcome', 'lag_sessions',
                             'n', 'baseline', 'augmented', 'mse_gain', 'mse_gain_ci95',
                             'first', 'last', 'baseline_rmse_bp', 'augmented_rmse_bp',
                             'baseline_hit', 'augmented_hit'}, 'Unknown comparison fields')
        require(bool(row.get('evidence_id')) and row['evidence_id'] not in ids, 'Duplicate evidence')
        ids.add(row['evidence_id'])
        require(bool(row.get('source_ids')) and set(row['source_ids']) <= set(hashes),
                'Unknown evidence sources')
        require(all(isinstance(row.get(k), str) and row[k] for k in
                    ['target', 'outcome', 'baseline', 'augmented']), 'Missing model identity')
        require(type(row.get('n')) is int and row['n'] > 0, 'Invalid sample count')
        require(type(row.get('lag_sessions')) is int and row['lag_sessions'] >= 0, 'Invalid lag')
        ci = row.get('mse_gain_ci95', [])
        require(len(ci) == 2 and np.isfinite([row.get('mse_gain'), *ci]).all()
                and ci[0] <= ci[1], 'Invalid uncertainty')
    return value


def export_evidence(value, destination):
    public_keys = ['schema_version', 'study_id', 'source_revision', 'generated_at_utc',
                   'decision_time_local', 'decision_timezone', 'evidence_status',
                   'historical_pit_certified', 'sample_start', 'sample_end',
                   'source_sha256', 'limitations']
    public = {key: value[key] for key in public_keys}
    public['sources'] = {key: {field: source[field] for field in ['url', 'sha256']}
                         for key, source in value['sources'].items()}
    comparison_keys = ['evidence_id', 'source_ids', 'target', 'outcome', 'lag_sessions', 'n',
                       'baseline', 'augmented', 'mse_gain', 'mse_gain_ci95', 'first', 'last',
                       'baseline_rmse_bp', 'augmented_rmse_bp', 'baseline_hit', 'augmented_hit']
    public['comparisons'] = [{key: row[key] for key in comparison_keys if key in row}
                             for row in value['comparisons']]
    validate_evidence(public)
    # Detailed diagnostics stay in the external research directory.
    destination.write_text(json.dumps(public, indent=2, allow_nan=False) + '\n')


def committed_revision(repository):
    status = subprocess.check_output(
        ['git', 'status', '--porcelain', '--untracked-files=all'], cwd=repository, text=True)
    if status.strip():
        raise ValueError('Experiment requires a clean committed checkout')
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repository, text=True).strip()


def run(manifest_path, output):
    """Manifest references reviewed existing files; it never downloads raw inputs."""
    manifest_bytes = manifest_path.read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    manifest = json.loads(manifest_bytes)
    if manifest.get('reviewed') is not True:
        raise ValueError('Input manifest must explicitly be reviewed')
    repository = Path(__file__).resolve().parents[4]
    revision = committed_revision(repository)
    if output.resolve().is_relative_to(repository):
        raise ValueError('Research output must stay outside source repository')
    sources, hashes = {}, {}
    for key, source in manifest['sources'].items():
        path = Path(source['path'])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != source['sha256']:
            raise ValueError(f'Input hash mismatch: {key}')
        hashes[key] = digest
        sources[key] = {'url': source['url'], 'sha256': digest}
    # Hash every consumed file; forbid an incomplete provenance manifest.
    index_root, extra_root = Path(manifest['index_inputs']), Path(manifest['extra_inputs'])
    needed = [index_root / f'{x}_tushare_daily.csv' for x in ['hsi', 'n225', 'ks11', 'spx', '000300_sh']]
    needed += [index_root / '801081_si_sw_daily.csv']
    needed += [extra_root / f'{x}_fxcm_fx_daily.csv' for x in ['usdcnh', 'usdjpy', 'eurusd']]
    needed += [extra_root / f'{x}_sh_fund_{kind}.csv' for x in ['510300', '512480'] for kind in ['daily', 'adj']]
    needed += [Path(manifest['theme_input'])]
    supplied = {Path(s['path']).resolve() for s in manifest['sources'].values()}
    if any(p.resolve() not in supplied for p in needed):
        raise ValueError('Manifest must hash every consumed input')
    data, controls, quality = targets(index_root, extra_root)
    semiconductor = load_daily(Path(manifest['theme_input']))
    validate_prices(semiconductor, ['close'])
    output.mkdir(parents=True, exist_ok=False)
    comparisons, annual, fold_rows, costs, audits = [], [], [], [], []
    for name in ['sw_semiconductor', '512480']:
        target = data[name]
        for lag in [0, 1]:
            base, audit = prepare(target, data['csi300'], controls, lag)
            aligned, theme_audit = align_external(target, {'theme': (semiconductor, 'spx', 'close')}, lag)
            base['theme'] = aligned.theme
            audits.extend([audit, theme_audit])
            for outcome in (['next_tradable_open'] if name == '512480' else ['gap', 'post_open']):
                frame = base.copy()
                if outcome == 'gap':
                    previous = target.pre_close if 'pre_close' in target else target.close.shift(1)
                    frame['y'] = target.open / previous - 1
                    end, hour, minute = target.date, 9, 30
                elif outcome == 'post_open':
                    frame['y'] = target.close / target.open - 1
                    end, hour, minute = target.date, 15, 0
                else:
                    frame['y'] = target.adjusted_open.shift(-1) / target.adjusted_open - 1
                    frame['exit_raw_open'] = target.open.shift(-1)
                    frame['exit_pre_close'] = target.auction_reference.shift(-1)
                    end, hour, minute = target.date.shift(-1), 9, 30
                frame['label_end_utc'] = (end.dt.tz_localize('Asia/Shanghai') + pd.Timedelta(hours=hour, minutes=minute)).dt.tz_convert('UTC')
                forecast, folds = walk_forward_theme(frame, manifest.get('start_year', 2020))
                identity = {'target': name, 'outcome': outcome, 'lag_sessions': lag}
                evidence_id = f'{name}.{outcome}.lag{lag}'
                comparison = {**identity, **paired_summary(forecast, 'global', 'theme_residual'),
                              'evidence_id': evidence_id, 'source_ids': sorted(hashes)}
                comparisons.append(comparison)
                annual.extend([{**identity, 'year': int(year), **paired_summary(group, 'global', 'theme_residual')}
                               for year, group in forecast.groupby('fold')])
                fold_rows.extend([{**identity, **fold} for fold in folds])
                forecast.to_csv(output / f'{evidence_id}.csv', index=False)
                if outcome == 'next_tradable_open':
                    replay = frame[frame.date.between(forecast.date.min(), forecast.date.max())].dropna(subset=['y', 'exit_raw_open', 'exit_pre_close'])
                    for model in ['global', 'theme_residual']:
                        prediction = dict(zip(forecast.date, forecast[model]))
                        for rt in [0, 5, 10, 20, 40]:
                            result, _ = simulate(replay, prediction, rt / 2)
                            costs.append({**identity, 'model': model, 'round_trip_bp': rt, **result})
    payload = {'schema_version': SCHEMA, 'study_id': manifest['study_id'],
               'source_revision': revision,
               'generated_at_utc': datetime.now(timezone.utc).isoformat(),
               'decision_time_local': '08:45', 'decision_timezone': 'Asia/Shanghai',
               'evidence_status': 'retrospective_exploratory', 'historical_pit_certified': False,
               'sample_start': min(x['first'] for x in comparisons),
               'sample_end': max(x['last'] for x in comparisons),
               'source_sha256': hashes, 'sources': sources, 'comparisons': comparisons,
               'annual': annual, 'folds': fold_rows, 'costs': costs, 'input_quality': quality,
               'limitations': ['Assumed daily-close availability; no historical retrieval vintages.',
                               'Previously inspected years; not an untouched holdout.',
                               'Extant ETF selection and opening-price fill proxies; no capacity proof.',
                               'Descriptive block-bootstrap intervals; no multiple-testing correction.',
                               'One-session delay is sensitivity analysis, not verified provider latency.']}
    if committed_revision(repository) != revision:
        raise ValueError('Source revision changed during experiment')
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != manifest_hash:
        raise ValueError('Input manifest changed during experiment')
    for key, source in manifest['sources'].items():
        if hashlib.sha256(Path(source['path']).read_bytes()).hexdigest() != hashes[key]:
            raise ValueError(f'Input changed during experiment: {key}')
    payload['input_manifest_sha256'] = manifest_hash
    pd.concat(audits, ignore_index=True).to_csv(output / 'assumed_availability_rows.csv', index=False)
    (output / 'research_diagnostics.json').write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    export_evidence(payload, output / 'overseas_theme_evidence.v1.json')
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.manifest, args.output)


if __name__ == '__main__':
    main()
