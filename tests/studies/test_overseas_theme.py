import numpy as np
import pandas as pd
import pytest

from market_research.studies.overseas_leadlag import theme


def test_beta_is_fitted_only_on_training_rows():
    train = pd.DataFrame({'spx': [0., 1., 2.], 'theme': [1., 3., 5.]})
    test = pd.DataFrame({'spx': [3.], 'theme': [100.]})
    residual_train, residual_test = theme.beta_residual(train, test)
    assert np.allclose(residual_train, 0)
    assert residual_test[0] == pytest.approx(93)


def test_contract_rejects_forecast_and_empty_provenance():
    with pytest.raises(ValueError):
        theme.validate_evidence({'schema_version': 'overseas_theme_evidence.v1'})


def test_walk_forward_purges_labels_and_keeps_negative_results():
    dates = pd.bdate_range('2018-01-01', '2021-02-01')
    rng = np.random.default_rng(2)
    f = pd.DataFrame({'date': dates})
    f['decision_utc'] = (f.date.dt.tz_localize('Asia/Shanghai') + pd.Timedelta(hours=8, minutes=45)).dt.tz_convert('UTC')
    f['label_end_utc'] = f.decision_utc + pd.Timedelta(days=3)
    for col in theme.BASELINE + ['theme', 'y']:
        f[col] = rng.normal(size=len(f))
    predictions, folds = theme.walk_forward_theme(f, 2020)
    assert len(predictions) > 250
    assert all(pd.Timestamp(x['last_training_label_utc']) < pd.Timestamp(x['test_first_decision_utc']) for x in folds)
    assert {'global', 'theme_residual'} <= set(predictions)


def evidence():
    return {'schema_version': 'overseas_theme_evidence.v1', 'study_id': 'fixture',
            'generated_at_utc': '2026-10-29T00:00:00+00:00', 'source_revision': 'a' * 40,
            'decision_time_local': '08:45', 'decision_timezone': 'Asia/Shanghai',
            'evidence_status': 'retrospective_exploratory', 'historical_pit_certified': False,
            'sample_start': '2020-01-01', 'sample_end': '2021-01-01',
            'source_sha256': {'sox': 'b' * 64},
            'sources': {'sox': {'url': 'https://example.org/sox', 'sha256': 'b' * 64}},
            'comparisons': [{'evidence_id': 'gap.lag0', 'source_ids': ['sox'],
                             'target': 'semiconductor', 'outcome': 'gap', 'lag_sessions': 0,
                             'n': 250, 'baseline': 'global', 'augmented': 'theme_residual',
                             'mse_gain': -0.1, 'mse_gain_ci95': [-0.3, 0.05]}],
            'limitations': ['Test fixture, not research evidence.']}


def test_export_preserves_negative_evidence_and_provenance(tmp_path):
    import json
    value = evidence()
    destination = tmp_path / 'evidence.json'
    theme.export_evidence(value, destination)
    restored = json.loads(destination.read_text())
    assert restored['comparisons'][0]['mse_gain'] == -0.1
    assert restored['source_sha256']['sox'] == 'b' * 64


@pytest.mark.parametrize('mutation', ['hash', 'source', 'nan', 'reversed', 'pit', 'duplicate'])
def test_contract_rejects_broken_evidence_linkage(mutation):
    value = evidence()
    if mutation == 'hash':
        value['sources']['sox']['sha256'] = 'c' * 64
    elif mutation == 'source':
        value['comparisons'][0]['source_ids'] = ['missing']
    elif mutation == 'nan':
        value['comparisons'][0]['mse_gain'] = float('nan')
    elif mutation == 'reversed':
        value['sample_end'] = '2019-01-01'
    elif mutation == 'pit':
        value['historical_pit_certified'] = True
    else:
        value['comparisons'] *= 2
    with pytest.raises(ValueError):
        theme.validate_evidence(value)


def test_manifest_refuses_unreviewed_inputs_without_creating_output(tmp_path):
    path = tmp_path / 'manifest.json'
    path.write_text('{"reviewed": false}')
    output = tmp_path / 'output'
    with pytest.raises(ValueError, match='reviewed'):
        theme.run(path, output)
    assert not output.exists()


def test_public_export_excludes_raw_paths_and_unreviewed_fields(tmp_path):
    import json
    value = evidence()
    value['raw_bars'] = [{'close': 123}]
    value['sources']['sox']['path'] = '/private/raw.csv'
    value['comparisons'][0]['private_prediction'] = 1
    destination = tmp_path / 'public.json'
    theme.export_evidence(value, destination)
    restored = json.loads(destination.read_text())
    assert 'raw_bars' not in restored
    assert 'path' not in restored['sources']['sox']
    assert 'private_prediction' not in restored['comparisons'][0]


def test_reviewed_manifest_runs_all_targets_and_cost_scenarios(tmp_path, monkeypatch):
    import hashlib
    import json
    # Synthetic fixture isolates Git metadata; production uses real clean-source checks.
    monkeypatch.setattr(theme, 'committed_revision', lambda repository: 'a' * 40)
    dates = pd.bdate_range('2018-01-01', '2020-04-01')
    rng = np.random.default_rng(15)
    root = tmp_path / 'inputs'
    root.mkdir()
    files = [f'{x}_tushare_daily.csv' for x in ['hsi', 'n225', 'ks11', 'spx', '000300_sh']]
    files += ['801081_si_sw_daily.csv', 'theme.csv']
    files += [f'{x}_fxcm_fx_daily.csv' for x in ['usdcnh', 'usdjpy', 'eurusd']]
    files += [f'{x}_sh_fund_{kind}.csv' for x in ['510300', '512480'] for kind in ['daily', 'adj']]
    sources = {}
    for name in files:
        close = 100 * np.exp(np.cumsum(rng.normal(0, .005, len(dates))))
        bars = pd.DataFrame({'trade_date': dates.strftime('%Y%m%d'), 'close': close,
                             'open': close * np.exp(rng.normal(0, .002, len(dates))),
                             'pre_close': np.r_[100, close[:-1]], 'amount': 1e8,
                             'bid_close': close, 'ask_close': close + .01, 'adj_factor': 1.})
        if not name.endswith('_adj.csv'):
            bars = bars.drop(columns='adj_factor')
        path = root / name
        bars.to_csv(path, index=False)
        sources[name] = {'path': str(path), 'url': 'https://example.org/fixture',
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest = {'reviewed': True, 'study_id': 'synthetic-test-only',
                'index_inputs': str(root), 'extra_inputs': str(root),
                'theme_input': str(root / 'theme.csv'), 'sources': sources}
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(manifest))
    result = theme.run(path, tmp_path / 'results')
    assert len(result['comparisons']) == 6
    assert len(result['costs']) == 20
    assert {x['outcome'] for x in result['comparisons']} == {'gap', 'post_open', 'next_tradable_open'}
    assert {x['lag_sessions'] for x in result['comparisons']} == {0, 1}
    audit = pd.read_csv(tmp_path / 'results' / 'assumed_availability_rows.csv')
    assert not (pd.to_datetime(audit.assumed_available_utc, utc=True) > pd.to_datetime(audit.decision_utc, utc=True)).any()
    assert (tmp_path / 'results' / 'research_diagnostics.json').exists()


@pytest.mark.parametrize('location', ['top', 'comparison', 'source'])
def test_validator_rejects_unknown_public_fields(location):
    value = evidence()
    if location == 'top':
        value['private'] = 1
    elif location == 'comparison':
        value['comparisons'][0]['private'] = 1
    else:
        value['sources']['sox']['private'] = 1
    with pytest.raises(ValueError, match='Unknown'):
        theme.validate_evidence(value)


def test_dirty_source_cannot_claim_committed_revision(monkeypatch, tmp_path):
    monkeypatch.setattr(theme.subprocess, 'check_output', lambda *a, **k: '?? src/new.py\n')
    with pytest.raises(ValueError, match='clean committed checkout'):
        theme.committed_revision(tmp_path)
