import hashlib
import json

import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.preflight import audit_prepared


def freeze(root, receipt):
    receipt['input_sha256'] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.iterdir() if p.name != 'inputs.json'
    }
    (root / 'inputs.json').write_text(json.dumps(receipt))


@pytest.fixture
def prepared(tmp_path):
    symbols = [f'600{i:03d}.SH' for i in range(40)]
    (tmp_path / 'symbols.json').write_text(json.dumps(symbols))
    for name in ['corporate-actions.json', 'unverified-corporate-actions.json']:
        (tmp_path / name).write_text('[]')
    panel = pd.DataFrame([dict(ts_code=s, trade_date=d, close=10.)
                          for d in ['20240102', '20240103'] for s in symbols])
    panel.to_parquet(tmp_path / 'daily-panel.parquet')
    bars = pd.DataFrame([dict(symbol=s, time=pd.Timestamp('2024-01-03 15:01', tz='Asia/Shanghai'),
                             interval_start=pd.Timestamp('2024-01-03 14:59', tz='Asia/Shanghai'),
                             open=10., high=10., low=10., close=10., up_limit=11., down_limit=9.,
                             volume=100., amount=1000., tradable=False) for s in symbols])
    # Include an actual observed session on both dates.
    prior = bars.copy()
    prior['time'] -= pd.Timedelta(days=1)
    prior['interval_start'] -= pd.Timedelta(days=1)
    pd.concat([prior, bars]).to_parquet(tmp_path / 'bars.parquet')
    targets = pd.DataFrame([dict(symbol=s, decision_time=pd.Timestamp('2024-01-02 20:02', tz='Asia/Shanghai'),
                                 entry_time=pd.Timestamp('2024-01-03 09:32', tz='Asia/Shanghai'), weight=.025)
                            for s in symbols])
    targets.to_parquet(tmp_path / 'targets-daily.parquet')
    receipt = dict(start='20240102', end='20240103', sessions=2, count=40,
                   variants={'daily': {'rebalance_sessions': 1, 'targets': 40, 'symbols': 40}},
                   adjustment_event_audit={'unexplained_changes': 0},
                   corporate_action_audit={'unverified_events': 0},
                   source_manifest_sha256={'daily': 'a'*64}, revision_safe=False,
                   pit_class='reconstructed_pit')
    freeze(tmp_path, receipt)
    return tmp_path, receipt


def test_valid_preflight_does_not_certify_pit_or_fills(prepared):
    root, _ = prepared
    report = audit_prepared(root)
    assert report['status'] == 'passed'
    assert report['revision_safe'] is False
    assert report['fill_eligibility_proven'] is False
    assert report['complete_nav_proven'] is False
    json.dumps(report, allow_nan=False)


def test_rejects_tampered_parquet_before_reading(prepared):
    root, _ = prepared
    with (root / 'bars.parquet').open('ab') as stream:
        stream.write(b'tampered')
    with pytest.raises(ValueError, match='hash mismatch'):
        audit_prepared(root)


@pytest.mark.parametrize('change,match', [
    ('future', 'causal'), ('naive', 'timezone'), ('duplicate', 'duplicate'),
    ('zero', 'price'), ('session', 'session'), ('scope', 'symbol'),
])
def test_rejects_semantically_invalid_hashed_data(prepared, change, match):
    root, receipt = prepared
    name = 'targets-daily.parquet' if change == 'future' else 'bars.parquet'
    frame = pd.read_parquet(root / name)
    if change == 'future':
        frame['decision_time'] = frame.entry_time + pd.Timedelta(minutes=1)
    elif change == 'naive':
        frame['time'] = frame.time.dt.tz_localize(None)
    elif change == 'duplicate':
        frame = pd.concat([frame, frame.iloc[:1]])
    elif change == 'zero':
        frame.loc[0, 'close'] = 0.
    elif change == 'session':
        frame['time'] += pd.Timedelta(days=7)
    elif change == 'scope':
        frame.loc[0, 'symbol'] = '688001.SH'
    frame.to_parquet(root / name)
    freeze(root, receipt)
    with pytest.raises(ValueError, match=match):
        audit_prepared(root)


def test_rejects_duplicate_json_keys(prepared):
    root, _ = prepared
    (root / 'inputs.json').write_text('{"input_sha256":{},"input_sha256":{}}')
    with pytest.raises(ValueError, match='duplicate JSON'):
        audit_prepared(root)


def test_rejects_filename_escape(prepared):
    root, receipt = prepared
    receipt['input_sha256']['../escape'] = '0'*64
    (root / 'inputs.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='filename'):
        audit_prepared(root)


def test_requires_hashed_bars(prepared):
    root, receipt = prepared
    del receipt['input_sha256']['bars.parquet']
    (root / 'inputs.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match='missing'):
        audit_prepared(root)


def test_corporate_action_availability_is_causal(prepared):
    root, receipt = prepared
    (root / 'corporate-actions.json').write_text(json.dumps([dict(
        event_id='e', symbol='600000.SH', available_date='20240104', record_date='20240102',
        ex_date='20240103', cash_pay_date='20240103', stock_tradable_date=None,
        cash_per_share=.1, stock_per_share=0., withholding_rate=0.)]))
    freeze(root, receipt)
    with pytest.raises(ValueError, match='corporate.*causal'):
        audit_prepared(root)


def test_missing_individual_books_does_not_prove_complete_nav(prepared):
    root, receipt = prepared
    bars = pd.read_parquet(root / 'bars.parquet')
    bars = bars.loc[~(bars.symbol.eq('600000.SH') & bars.time.dt.day.eq(3))]
    bars.to_parquet(root / 'bars.parquet')
    freeze(root, receipt)
    report = audit_prepared(root)
    assert report['checks']['missing_symbol_session_books'] == 1
    assert report['complete_nav_proven'] is False
    assert any('held-inventory' in warning for warning in report['warnings'])


def test_experiment_requires_complete_selection_universe(prepared):
    root, receipt = prepared
    receipt['experiment_study'] = {'implementation_sha256': {'runner': 'f'*64}}
    freeze(root, receipt)
    with pytest.raises(ValueError, match='complete universe'):
        audit_prepared(root)


def test_retained_universe_binds_target_decision_day(prepared):
    root, receipt = prepared
    panel = pd.read_parquet(root / 'daily-panel.parquet')
    panel = panel.loc[~(panel.ts_code.eq('600000.SH') & panel.trade_date.eq('20240102'))]
    panel.to_parquet(root / 'full-selection-panel.parquet')
    freeze(root, receipt)
    with pytest.raises(ValueError, match='full selection panel'):
        audit_prepared(root)


def test_unverified_event_is_reported_as_per_run_gate(prepared):
    root, receipt = prepared
    (root / 'unverified-corporate-actions.json').write_text(json.dumps([
        dict(symbol='600000.SH', ex_date='20240103', record_dates=['20240102'], reason='unknown')]))
    receipt['corporate_action_audit']['unverified_events'] = 1
    freeze(root, receipt)
    report = audit_prepared(root)
    assert report['checks']['unverified_corporate_events'] == 1
    assert any('ownership validation' in warning for warning in report['warnings'])


def test_factor_packet_requires_every_reference_hash_binding(prepared):
    root, receipt = prepared
    source = root.parent / 'source.json'
    source.write_text('{}')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    packet = dict(daily_manifest_sha256='a'*64, dividend_sha256='b'*64,
                  diagnostic={'path': 'missing.parquet', 'sha256': 'c'*64})
    (root / 'factor-evidence.json').write_text(json.dumps(packet))
    receipt['source_manifest_sha256']['dividends'] = 'b'*64
    receipt['adjustment_event_audit'].update(
        evidence_manifest_sha256=hashlib.sha256((root / 'factor-evidence.json').read_bytes()).hexdigest(),
        evidence_files_sha256={str(source): digest})
    freeze(root, receipt)
    with pytest.raises(ValueError, match='reference.*binding'):
        audit_prepared(root)


def source_calendar(prepared):
    root, receipt = prepared
    calendar = root.parent / (root.name + '-calendar.parquet')
    pd.DataFrame(dict(exchange=['SSE', 'SSE'], is_open=[1, 1],
                      cal_date=['20240102', '20240103'])).to_parquet(calendar)
    pd.read_parquet(root / 'daily-panel.parquet').to_parquet(root / 'full-selection-panel.parquet')
    (root / 'session-dates.json').write_text(json.dumps(['20240102', '20240103']))
    receipt['experiment_study'] = dict(source_refs=[dict(name='trade_cal', path=str(calendar),
                                                        sha256=hashlib.sha256(calendar.read_bytes()).hexdigest())])
    freeze(root, receipt)
    return calendar


def test_source_ref_bytes_are_verified(prepared):
    calendar = source_calendar(prepared)
    calendar.write_bytes(calendar.read_bytes() + b'tamper')
    with pytest.raises(ValueError, match='source reference hash mismatch'):
        audit_prepared(prepared[0])


def test_rehashed_calendar_still_must_match_sessions(prepared):
    calendar = source_calendar(prepared)
    root, receipt = prepared
    frame = pd.read_parquet(calendar)
    frame.loc[0, 'is_open'] = 0
    frame.to_parquet(calendar)
    receipt['experiment_study']['source_refs'][0]['sha256'] = hashlib.sha256(calendar.read_bytes()).hexdigest()
    freeze(root, receipt)
    with pytest.raises(ValueError, match='authoritative.*calendar'):
        audit_prepared(root)


def test_hashed_session_dates_must_match_panel(prepared):
    source_calendar(prepared)
    root, receipt = prepared
    (root / 'session-dates.json').write_text('["20240102"]')
    freeze(root, receipt)
    with pytest.raises(ValueError, match='declared session calendar'):
        audit_prepared(root)


def test_authoritative_calendar_report_omits_private_paths(prepared):
    calendar = source_calendar(prepared)
    report = audit_prepared(prepared[0])
    assert report['checks']['source_references_verified'] == 1
    assert report['checks']['authoritative_calendar_verified'] is True
    assert str(calendar) not in json.dumps(report)
    assert not any('not independently reloaded' in w for w in report['warnings'])


def test_registered_protocol_requires_2002_decision_clock(prepared):
    source_calendar(prepared)
    root, receipt = prepared
    receipt['experiment_study']['protocol_profile'] = 'ashare_execution_validation.v1'
    targets = pd.read_parquet(root / 'targets-daily.parquet')
    targets['decision_time'] -= pd.Timedelta(minutes=1)
    targets.to_parquet(root / 'targets-daily.parquet')
    freeze(root, receipt)
    with pytest.raises(ValueError, match='20:02'):
        audit_prepared(root)


def test_verified_factor_packet_reports_source_count(prepared):
    root, receipt = prepared
    source = root.parent / (root.name + '-factor-source.json')
    source.write_text('{}')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    packet = dict(daily_manifest_sha256='a'*64, dividend_sha256='b'*64,
                  diagnostic={'path': str(source), 'sha256': digest})
    (root / 'factor-evidence.json').write_text(json.dumps(packet))
    receipt['source_manifest_sha256']['dividends'] = 'b'*64
    receipt['adjustment_event_audit'].update(
        evidence_manifest_sha256=hashlib.sha256((root / 'factor-evidence.json').read_bytes()).hexdigest(),
        evidence_files_sha256={str(source): digest})
    freeze(root, receipt)
    report = audit_prepared(root)
    assert report['checks']['source_references_verified'] == 0
    assert report['checks']['factor_evidence_sources_verified'] == 1
