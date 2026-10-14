"""Prepare matched baseline/risk inputs without narrowing the selection universe."""
from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
from pathlib import Path
import os

import pandas as pd

from market_research.microcap_execution import load_clean_panel
from market_research.studies.ashare_execution_costs.minute import build_targets
from market_research.studies.ashare_execution_costs.risk_guards import build_risk_targets
from market_research.studies.ashare_execution_costs.risk_sources import load_risk_events

EXPECTED_SYMBOLS = {'600321.SH', '002621.SZ', '000982.SZ', '600836.SH'}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def verify_parent_inputs(parent, fingerprints):
    for name, digest in fingerprints.items():
        if Path(name).name != name:
            raise ValueError('invalid prepared input filename')
        if sha(parent / name) != digest:
            raise ValueError(f'parent prepared input hash mismatch: {name}')


def verify_source_leaves(paths, fingerprints):
    actual = {key: sha(path) for key, path in paths.items()}
    for key, digest in actual.items():
        if digest != fingerprints[key]:
            raise ValueError(f'consumed source leaf hash mismatch: {key}')
    return actual


def validate_output_paths(parent, outputs):
    paths = [parent, *outputs]
    if len(set(paths)) != len(paths) or any(
        left in right.parents or right in left.parents
        for index, left in enumerate(paths) for right in paths[index + 1:]
    ):
        raise ValueError('comparison outputs must be distinct and nonoverlapping')
    for path in outputs:
        if path.exists() and any(path.iterdir()):
            raise FileExistsError('comparison output must be new or empty')


def validate_selected_symbols(selected, original):
    if selected - original:
        raise ValueError('risk targets require execution evidence outside original scope')


def verify_selected_panel(full_panel, original_panel, original_symbols):
    selected = full_panel.loc[full_panel.ts_code.isin(original_symbols)]
    if set(selected.columns) != set(original_panel.columns):
        raise ValueError('original selected panel columns differ')
    keys = ['trade_date', 'ts_code']
    pd.testing.assert_frame_equal(
        selected.loc[:, original_panel.columns].sort_values(keys).reset_index(drop=True),
        original_panel.sort_values(keys).reset_index(drop=True), check_exact=True,
    )


def prepare(args):
    parent = args.base_prepared.resolve()
    receipt = json.loads((parent / 'inputs.json').read_text())
    verify_parent_inputs(parent, receipt['input_sha256'])
    if len(receipt['input_sha256']) != 10:
        raise ValueError('expected original ten prepared inputs')
    outputs = [args.baseline_output.resolve(), args.risk_output.resolve()]
    validate_output_paths(parent, outputs)
    current_path = args.data_root / 'metadata/current_assets/a_share_current.json'
    current = json.loads(current_path.read_text())
    assets = current['assets']
    def asset(key):
        return Path(assets[key]['resolved_path'])
    sources = {'daily': asset('daily_clean') / 'manifest.yml',
               'namechange': asset('namechange'), 'instruments': asset('instruments'),
               'trade_cal': asset('trade_cal')}
    fingerprints = verify_source_leaves(sources, receipt['source_manifest_sha256'])
    calendar = pd.read_parquet(asset('trade_cal'))
    sessions = sorted(calendar.loc[
        calendar.exchange.eq('SSE') & calendar.is_open.eq(1)
        & calendar.cal_date.astype(str).between(receipt['start'], receipt['end']),
        'cal_date'].astype(str).unique())
    # Always reload the complete panel. The original daily-panel file retains only
    # execution symbols and cannot supply replacement candidates correctly.
    panel = load_clean_panel(asset('daily_clean'), asset('instruments'),
                             receipt['start'], receipt['end'])
    if sorted(panel.trade_date.astype(str).unique()) != sessions:
        raise ValueError('full panel differs from authoritative trading sessions')
    original_symbols = set(json.loads((parent / 'symbols.json').read_text()))
    verify_selected_panel(panel, pd.read_parquet(parent / 'daily-panel.parquet'), original_symbols)
    names = pd.read_parquet(asset('namechange'))
    baseline = build_targets(panel, count=receipt['count'], namechange=names)
    baseline['entry_time'] += pd.Timedelta(minutes=1)
    pd.testing.assert_frame_equal(baseline, pd.read_parquet(parent / 'targets-daily.parquet'),
                                  check_exact=True)
    events, source_audit = load_risk_events(args.source_packet, sessions,
                                          expected_symbols=EXPECTED_SYMBOLS)
    risk, audit = build_risk_targets(panel, count=receipt['count'], minimum_close=1.0,
                                    namechange=names, risk_events=events)
    risk['entry_time'] += pd.Timedelta(minutes=1)
    validate_selected_symbols(set(risk.symbol), original_symbols)
    implementations = {'preparation': sha(Path(__file__)),
                       'baseline_targets': sha(Path(inspect.getfile(build_targets))),
                       'risk_targets': sha(Path(inspect.getfile(build_risk_targets))),
                       'risk_sources': sha(Path(inspect.getfile(load_risk_events)))}
    lineage = {'parent_prepared_path': str(parent),
               'parent_receipt_sha256': sha(parent / 'inputs.json'),
               'parent_input_sha256': receipt['input_sha256'],
               'consumed_source_leaf_sha256': fingerprints,
               'current_metadata_sha256': sha(current_path),
               'current_metadata_policy': 'consumed_leaves_exact_parent_match',
               'full_panel_rows': len(panel), 'full_panel_symbols': panel.ts_code.nunique(),
               'baseline_targets_exact_parent_match': True,
               'original_selected_panel_exact_match': True,
               'historical_full_universe_bytes_verified': False,
               'historical_full_universe_limit': 'original preparation did not archive full universe bytes; selected rows and targets match exactly',
               'implementation_sha256': implementations}
    for role, output, targets in zip(('baseline', 'risk'), outputs, (baseline, risk), strict=True):
        output.mkdir(parents=True, exist_ok=True)
        for filename in receipt['input_sha256']:
            os.link(parent / filename, output / filename)
        full_panel_path = output / 'full-selection-panel.parquet'
        if role == 'baseline':
            panel.to_parquet(full_panel_path, index=False)
            lineage['full_selection_panel_sha256'] = sha(full_panel_path)
        else:
            os.link(outputs[0] / full_panel_path.name, full_panel_path)
        if role == 'risk':
            (output / 'targets-daily.parquet').unlink()
            targets.to_parquet(output / 'targets-daily.parquet', index=False)
        fresh = copy.deepcopy(receipt)
        fresh['risk_comparison'] = {
            'role': role, 'source_packet_path': str(args.source_packet.resolve()),
            'source_packet_sha256': sha(args.source_packet),
            'authorized_scenarios': ['fees_1m', 'fees_10m'],
            'selected_symbols': sorted(targets.symbol.unique()),
            'execution_evidence_symbols': sorted(original_symbols),
            'minimum_close': 1.0 if role == 'risk' else None,
            'source_audit': source_audit, 'lineage': lineage,
            'selection_audit': audit if role == 'risk' else None,
        }
        fresh['variants']['daily'].update(targets=len(targets), symbols=targets.symbol.nunique())
        fresh['input_sha256'] = {name: sha(output / name) for name in [*receipt['input_sha256'], 'full-selection-panel.parquet']}
        write_json(output / 'inputs.json', fresh)
        print(role, output, len(targets), targets.symbol.nunique(), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('data-root', 'base-prepared', 'source-packet', 'baseline-output', 'risk-output'):
        parser.add_argument('--' + name, type=Path, required=True)
    prepare(parser.parse_args())


if __name__ == '__main__':
    main()
