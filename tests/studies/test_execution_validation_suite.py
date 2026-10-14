"""Strict execution profile and immutable ledger provenance regressions."""
import importlib.util
from pathlib import Path

import pytest

pytest.importorskip('portfolio_backtester.minute_execution')

SPEC = importlib.util.spec_from_file_location('validation_suite', Path(__file__).parents[2] / 'scripts/run_execution_validation_suite.py')
suite = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(suite)


def profile():
    return dict(scenario='baseline_1m', initial_cash=1e6, participation_rate=.05,
                buy_fee_bp=1., sell_fee_bp=6., lot_size=100, release_slices=1,
                execution_minutes=330, latency_minutes=1, commission_minimum_cny=0., sell_tax_bp=5.)


@pytest.mark.parametrize('key,value', [('initial_cash', float('nan')), ('initial_cash', True),
    ('participation_rate', .11), ('latency_minutes', True), ('release_slices', 1.5), ('release_slices', True), ('lot_size', 10), ('buy_fee_bp', 0)])
def test_invalid_profiles_fail_closed(key, value):
    row = profile()
    row[key] = value
    with pytest.raises(ValueError):
        suite.validate_profiles([row])


def test_profiles_require_full_explicit_config_and_safe_unique_ids():
    row = profile()
    assert suite.validate_profiles([row])[0][0] == row['scenario']
    with pytest.raises(ValueError):
        suite.validate_profiles([row, row])
    del row['latency_minutes']
    with pytest.raises(ValueError):
        suite.validate_profiles([row])


def test_output_verification_rejects_tampering(tmp_path):
    output = tmp_path / 'daily.parquet'
    output.write_bytes(b'original')
    for name in suite.REQUIRED_OUTPUTS - {'daily.parquet'}:
        (tmp_path / name).write_bytes(b'original')
    receipt = {'output_sha256': {name: suite.sha(tmp_path / name) for name in suite.REQUIRED_OUTPUTS}}
    suite.verify_outputs(tmp_path, receipt)
    output.write_bytes(b'tampered')
    with pytest.raises(ValueError):
        suite.verify_outputs(tmp_path, receipt)


def test_matching_fingerprint_excludes_audit_but_binds_execution_bytes(tmp_path):
    for name in ('bars.parquet', 'corporate-actions.json', 'targets-daily.parquet'):
        (tmp_path / name).write_bytes(name.encode())
    config = profile()
    config.pop('scenario')
    original = suite.matching_fingerprint(tmp_path, config, [], {'engine': 'abc'})
    (tmp_path / 'selection-panel.parquet').write_bytes(b'unrelated audit')
    assert suite.matching_fingerprint(tmp_path, config, [], {'engine': 'abc'}) == original
    assert suite.matching_fingerprint(tmp_path, config, [{'value_per_share': 0}], {'engine': 'abc'}) != original
    assert suite.matching_fingerprint(tmp_path, config, [], {'engine': 'def'}) != original
    config['initial_cash'] *= 10
    assert suite.matching_fingerprint(tmp_path, config, [], {'engine': 'abc'}) != original
    config['initial_cash'] /= 10
    (tmp_path / 'targets-daily.parquet').write_bytes(b'changed order')
    assert suite.matching_fingerprint(tmp_path, config, [], {'engine': 'abc'}) != original


def test_reuse_source_input_receipt_and_valuation_are_verified(tmp_path):
    prepared = tmp_path / 'prepared'
    candidate = prepared / 'scenario'
    candidate.mkdir(parents=True)
    for name in ('bars.parquet', 'corporate-actions.json', 'targets-daily.parquet'):
        (prepared / name).write_bytes(name.encode())
    inputs = {'input_sha256': {name: suite.sha(prepared / name) for name in
        ('bars.parquet', 'corporate-actions.json', 'targets-daily.parquet')}}
    suite.write_json(prepared / 'inputs.json', inputs)
    config = profile()
    config.pop('scenario')
    implementation = {'engine': 'abc'}
    receipt = dict(config=config, inputs_sha256=suite.sha(prepared / 'inputs.json'),
        input_sha256=inputs['input_sha256'], valuation_rows=[],
        simulation_fingerprint=suite.matching_fingerprint(prepared, config, [], implementation))
    suite.verify_reuse_source(candidate, receipt, implementation)
    (prepared / 'targets-daily.parquet').write_bytes(b'changed')
    with pytest.raises(ValueError):
        suite.verify_reuse_source(candidate, receipt, implementation)


def test_execute_reuse_and_resume_require_actual_ledger_integrity(tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    import pandas as pd

    monkeypatch.setitem(sys.modules, 'market_research.studies.ashare_execution_costs.preflight',
                        SimpleNamespace(audit_prepared=lambda *args, **kwargs: {'status': 'passed'}))
    monkeypatch.setattr(suite, 'implementation_hashes', lambda: {'engine': 'formal-engine'})
    first = tmp_path / 'first'
    first.mkdir()
    bars = pd.DataFrame([dict(symbol='600000.SH', time=pd.Timestamp('2025-01-02 09:33', tz='Asia/Shanghai'),
        interval_start=pd.Timestamp('2025-01-02 09:31', tz='Asia/Shanghai'), open=10., high=10., low=10.,
        close=10., up_limit=11., down_limit=9., volume=10000., amount=100000., tradable=True)])
    bars.to_parquet(first / 'bars.parquet', index=False)
    pd.DataFrame([dict(symbol='600000.SH', decision_time=pd.Timestamp('2025-01-01 20:02', tz='Asia/Shanghai'),
        entry_time=pd.Timestamp('2025-01-02 09:32', tz='Asia/Shanghai'), weight=1.)]).to_parquet(
            first / 'targets-daily.parquet', index=False)
    suite.write_json(first / 'corporate-actions.json', [])
    suite.write_json(first / 'unverified-corporate-actions.json', [])
    suite.write_json(first / 'protocol.json', {'profiles': [profile()]})
    inputs = dict(experiment_study={'valuation_events': None, 'authorized_profiles': [profile()],
        'protocol_sha256': suite.sha(first / 'protocol.json')}, input_sha256={
        path.name: suite.sha(path) for path in first.iterdir()})
    suite.write_json(first / 'inputs.json', inputs)
    suite.execute(first, [profile()])
    receipt = __import__('json').loads((first / 'baseline_1m/receipt.json').read_text())
    assert receipt['execution_method'] == 'formal_provider_simulation'
    second = tmp_path / 'second'
    second.mkdir()
    import shutil
    for path in first.iterdir():
        if path.is_file() and path.name != 'validation-summary.proposed.json':
            shutil.copyfile(path, second / path.name)
    monkeypatch.setattr(suite, 'simulate_minute_execution', lambda *a, **k: pytest.fail('reused ledger must not simulate'))
    report = suite.execute(second, [profile()], reuse_candidates=[first / 'baseline_1m'])
    assert report['complete'] is False and report['published'] is False
    receipt = __import__('json').loads((second / 'baseline_1m/receipt.json').read_text())
    assert receipt['execution_method'] == 'verified_ledger_reuse'
    suite.execute(second, [profile()])
    with (second / 'baseline_1m/daily.parquet').open('ab') as stream:
        stream.write(b'tampered')
    with pytest.raises(ValueError, match='output hash'):
        suite.execute(second, [profile()])


def test_profiles_bound_to_hashed_protocol_and_authorized_roster(tmp_path):
    suite.write_json(tmp_path / 'protocol.json', {'profiles': [profile()]})
    inputs = {'input_sha256': {'protocol.json': suite.sha(tmp_path / 'protocol.json')},
              'experiment_study': {'protocol_sha256': suite.sha(tmp_path / 'protocol.json'),
                                   'authorized_profiles': [profile()]}}
    suite.validate_profile_binding(tmp_path, inputs, [profile()])
    changed = profile()
    changed['initial_cash'] *= 10
    with pytest.raises(ValueError):
        suite.validate_profile_binding(tmp_path, inputs, [changed])
    renamed = dict(profile(), scenario='invented')
    with pytest.raises(ValueError):
        suite.validate_profile_binding(tmp_path, inputs, [renamed])
    forged = dict(inputs, experiment_study=dict(inputs['experiment_study'], authorized_profiles=[changed]))
    with pytest.raises(ValueError):
        suite.validate_profile_binding(tmp_path, forged, [changed])
    (tmp_path / 'protocol.json').write_text('{}')
    with pytest.raises(ValueError):
        suite.validate_profile_binding(tmp_path, inputs, [profile()])


def test_output_verification_rejects_truncated_or_extra_manifests(tmp_path):
    required = {'daily.parquet', 'orders.parquet', 'fills.parquet', 'holdings.parquet',
                'valuation-ledger.parquet', 'shortfall.parquet'}
    for name in required | {'unregistered.json'}:
        (tmp_path / name).write_bytes(b'ledger')
    hashes = {name: suite.sha(tmp_path / name) for name in required}
    suite.verify_outputs(tmp_path, {'output_sha256': hashes})
    truncated = dict(hashes)
    truncated.pop('fills.parquet')
    with pytest.raises(ValueError, match='roster'):
        suite.verify_outputs(tmp_path, {'output_sha256': truncated})
    extra = dict(hashes, **{'unregistered.json': suite.sha(tmp_path / 'unregistered.json')})
    with pytest.raises(ValueError, match='roster'):
        suite.verify_outputs(tmp_path, {'output_sha256': extra})
