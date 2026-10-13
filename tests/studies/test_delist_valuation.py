import hashlib
import json

import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.delist_valuation import build_valuation_policy


def packet_fixture(tmp_path):
    instrument = dict(symbol='000982.SZ', successor_code='400205', delist_date='20240826',
                      decision_available_time='2024-08-23T09:00:00+08:00',
                      legal_exact_delist_date_available_time='2024-08-23T09:00:00+08:00',
                      delist_effective_time='2024-08-26T09:00:00+08:00',
                      last_exchange_close=0.42, first_transfer_date='20241114',
                      quote_evidence_level='single_source_unverified',
                      quotes=[dict(date='20241114', close=0.31,
                                   available_time='2024-11-15T09:00:00+08:00')])
    verdict = tmp_path / 'investigation.json'
    verdict.write_text(json.dumps({'symbols': [dict(symbol=instrument['symbol'], delist_date=instrument['delist_date'], last_raw_close=instrument['last_exchange_close'], successor_confirmation_code=instrument['successor_code'])]}))
    native = tmp_path / 'quotes.parquet'
    pd.DataFrame([dict(successor_code='400205', date='20241114', close=0.31)]).to_parquet(native)
    refs = [dict(name=name, path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            for name, path in [('delist_investigation', verdict), ('native_quotes', native)]]
    facts = tmp_path / 'normalized-facts.json'
    facts.write_text(json.dumps({'symbols': [dict(
        symbol=instrument['symbol'], delist_date=instrument['delist_date'],
        termination_decision_available_time=instrument['decision_available_time'],
        legal_announcement_available_time=instrument['legal_exact_delist_date_available_time'],
        last_actual_price={'close': instrument['last_exchange_close']},
        mapped_code=instrument['successor_code'], first_transfer_date=instrument['first_transfer_date'],
        tradable=False)]}))
    refs.append(dict(name='normalized_facts', path=str(facts),
                     sha256=hashlib.sha256(facts.read_bytes()).hexdigest()))
    instrument['source_refs'] = [r['name'] for r in refs]
    instrument['quotes'][0]['source_ref'] = 'native_quotes'
    packet = dict(schema='execution-delist-policy-source.v1', source_refs=refs,
                  instruments=[instrument], study=dict(start='20240102', end='20241231',
                                                       selected_symbols=['000982.SZ']))
    path = tmp_path / 'packet.json'
    path.write_text(json.dumps(packet))
    return path, packet, dict(start='20240102', end='20241231',
                             session_dates=pd.bdate_range('2024-01-02', '2024-12-31').strftime('%Y%m%d').tolist())


def save(path, packet):
    path.write_text(json.dumps(packet))


def test_impairment_preserves_holding_as_nontrading_zero_hypothesis(tmp_path):
    path, _, inputs = packet_fixture(tmp_path)
    events, audit = build_valuation_policy(path, inputs, 'full_impairment')
    assert len(events) == 1
    assert events[0]['value_per_share'] == 0
    assert events[0]['effective_time'] == '2024-08-26T09:00:00+08:00'
    assert audit['nontrading'] is True
    assert audit['quote_verified'] is False
    assert audit['revision_safe'] is False
    assert 'hypothesis' in audit


def test_observed_quote_effective_only_when_available(tmp_path):
    path, _, inputs = packet_fixture(tmp_path)
    events, _ = build_valuation_policy(path, inputs, 'impairment_then_observed')
    assert len(events) == 2
    assert events[1]['value_per_share'] == 0.31
    assert events[1]['effective_time'] == events[1]['available_time']
    assert events[1]['effective_time'] == '2024-11-15T09:00:00+08:00'


@pytest.mark.parametrize('change', ['hash', 'close', 'symbol', 'window', 'naive', 'early', 'duplicate', 'legal_unknown', 'legal_late'])
def test_rejects_unbound_or_noncausal_packet(tmp_path, change):
    path, packet, inputs = packet_fixture(tmp_path)
    row = packet['instruments'][0]
    if change == 'hash':
        packet['source_refs'][0]['sha256'] = '0' * 64
    elif change == 'close':
        row['quotes'][0]['close'] = 0.32
    elif change == 'symbol':
        packet['study']['selected_symbols'] = ['000001.SZ']
    elif change == 'window':
        inputs['end'] = '20241230'
    elif change == 'naive':
        row['decision_available_time'] = '2024-08-23T09:00:00'
    elif change == 'early':
        row['quotes'][0]['available_time'] = '2024-11-14T09:00:00+08:00'
    elif change == 'legal_unknown':
        row['legal_exact_delist_date_available_time'] = None
    elif change == 'legal_late':
        row['legal_exact_delist_date_available_time'] = '2024-08-26T10:00:00+08:00'
    else:
        packet['instruments'].append(row.copy())
    save(path, packet)
    with pytest.raises(ValueError):
        build_valuation_policy(path, inputs, 'impairment_then_observed')


def test_quotes_after_window_remain_audited_but_create_no_future_event(tmp_path):
    path, packet, inputs = packet_fixture(tmp_path)
    packet['study']['end'] = inputs['end'] = '20241114'
    save(path, packet)
    events, audit = build_valuation_policy(path, inputs, 'impairment_then_observed')
    assert len(events) == 1
    assert audit['observed_quote_rows'] == 1
    assert audit['excluded_after_window'] == 1


def test_decision_hypothesis_does_not_claim_unknown_legal_date(tmp_path):
    path, packet, inputs = packet_fixture(tmp_path)
    packet['instruments'][0]['legal_exact_delist_date_available_time'] = None
    ref = next(r for r in packet['source_refs'] if r['name'] == 'normalized_facts')
    from pathlib import Path
    facts = json.loads(Path(ref['path']).read_text())
    facts['symbols'][0]['legal_announcement_available_time'] = None
    Path(ref['path']).write_text(json.dumps(facts))
    ref['sha256'] = hashlib.sha256(Path(ref['path']).read_bytes()).hexdigest()
    save(path, packet)
    events, audit = build_valuation_policy(path, inputs, 'termination_decision_full_impairment')
    assert len(events) == 1
    assert events[0]['effective_time'] == events[0]['available_time'] == '2024-08-23T09:00:00+08:00'
    assert audit['trigger'] == 'confirmed_termination_decision_first_session'
    assert audit['impairment_assumption'] is True
    assert audit['legal_exact_date_pit_verified'] is False


def test_decision_observed_is_nontrading_and_revision_unsafe(tmp_path):
    path, _, inputs = packet_fixture(tmp_path)
    events, audit = build_valuation_policy(path, inputs, 'termination_decision_impairment_then_observed')
    assert len(events) == 2
    assert audit['retrospective_transfer_facts'] is True
    assert audit['nontrading'] is True
    assert audit['revision_safe'] is False


def test_duplicate_quote_effective_time_is_rejected(tmp_path):
    path, packet, inputs = packet_fixture(tmp_path)
    row = packet['instruments'][0]
    row['quotes'].append(row['quotes'][0].copy())
    save(path, packet)
    with pytest.raises(ValueError, match='duplicate'):
        build_valuation_policy(path, inputs, 'impairment_then_observed')


def test_selected_inputs_take_precedence_over_packet_scope(tmp_path):
    path, _, inputs = packet_fixture(tmp_path)
    inputs['selected_symbols'] = ['000001.SZ']
    with pytest.raises(ValueError, match='unselected'):
        build_valuation_policy(path, inputs, 'full_impairment')


def test_unknown_mode_cannot_silently_change_valuation(tmp_path):
    path, _, inputs = packet_fixture(tmp_path)
    with pytest.raises(ValueError, match='mode'):
        build_valuation_policy(path, inputs, 'last_price_carry')


@pytest.mark.parametrize('field', ['decision_available_time', 'first_transfer_date'])
def test_packet_cannot_override_hash_bound_normalized_facts(tmp_path, field):
    path, packet, inputs = packet_fixture(tmp_path)
    packet['instruments'][0][field] = ('2024-08-22T09:00:00+08:00'
                                      if field == 'decision_available_time' else '20241113')
    save(path, packet)
    with pytest.raises(ValueError, match='normalized'):
        build_valuation_policy(path, inputs, 'termination_decision_full_impairment')


def test_normalized_source_hash_cannot_be_overridden_by_packet_values(tmp_path):
    path, packet, inputs = packet_fixture(tmp_path)
    ref = next(r for r in packet['source_refs'] if r['name'] == 'normalized_facts')
    from pathlib import Path
    Path(ref['path']).write_text('{}')
    with pytest.raises(ValueError, match='hash mismatch'):
        build_valuation_policy(path, inputs, 'termination_decision_full_impairment')


def test_distinct_native_dates_on_one_session_keep_latest_known_quote(tmp_path):
    path, packet, inputs = packet_fixture(tmp_path)
    row = packet['instruments'][0]
    native_ref = next(r for r in packet['source_refs'] if r['name'] == 'native_quotes')
    from pathlib import Path
    native = Path(native_ref['path'])
    pd.DataFrame([dict(successor_code='400205', date=date, close=value)
                  for date, value in [('20241114', 0.31), ('20241115', 0.32)]]).to_parquet(native)
    native_ref['sha256'] = hashlib.sha256(native.read_bytes()).hexdigest()
    row['quotes'][0]['available_time'] = '2024-11-16T09:00:00+08:00'
    row['quotes'].append(dict(date='20241115', close=0.32,
                              available_time='2024-11-16T09:00:00+08:00',
                              source_ref='native_quotes'))
    save(path, packet)
    events, audit = build_valuation_policy(path, inputs, 'termination_decision_impairment_then_observed')
    assert len(events) == 2
    assert events[-1]['effective_time'] == '2024-11-18T09:00:00+08:00'
    assert audit['superseded_quote_rows'] == 1
    assert events[-1]['value_per_share'] == 0.32



def test_weekend_available_quote_waits_for_actual_session(tmp_path):
    path, packet, inputs = packet_fixture(tmp_path)
    packet['instruments'][0]['quotes'][0]['available_time'] = '2024-11-16T09:00:00+08:00'
    save(path, packet)
    events, _ = build_valuation_policy(path, inputs, 'impairment_then_observed')
    assert events[-1]['available_time'] == '2024-11-16T09:00:00+08:00'
    assert events[-1]['effective_time'] == '2024-11-18T09:00:00+08:00'


def test_holiday_and_missing_session_calendar_cannot_create_fake_day(tmp_path):
    path, _, inputs = packet_fixture(tmp_path)
    inputs['session_dates'].remove('20241115')
    events, _ = build_valuation_policy(path, inputs, 'impairment_then_observed')
    assert events[-1]['effective_time'] == '2024-11-18T09:00:00+08:00'
    del inputs['session_dates']
    with pytest.raises(ValueError, match='session'):
        build_valuation_policy(path, inputs, 'impairment_then_observed')
