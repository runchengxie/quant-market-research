import hashlib
import json

import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.risk_sources import load_risk_events


def packet(tmp_path):
    primary = tmp_path / 'notice.pdf'
    primary.write_bytes(b'primary announcement')
    core = dict(symbol='600836.SH', event_id='independent-confirmation',
                event_type='confirmed_termination', available_time='2024-07-08T09:00:00+08:00')
    facts = dict(schema='execution-risk-event-facts.v1', events=[dict(
        **core, primary_publication_date='2024-07-05', primary_file_ref='primary',
        publication_intraday_timestamp=None,
        availability_rule='next_exchange_trading_day_09:00_Asia/Shanghai_after_date_only_publication')])
    fact_path = tmp_path / 'facts.json'
    fact_path.write_text(json.dumps(facts))
    refs = [dict(name=name, path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            for name, path in [('primary', primary), ('facts', fact_path)]]
    value = dict(schema='execution-risk-events-source.v1', source_refs=refs, facts_ref=refs[1],
                 events=[dict(**core, source_refs=['primary'])],
                 coverage=dict(scope='selected_baseline_109_2024_delisted', symbols=['600836.SH'],
                               complete_for_scope=True, all_market_announcement_coverage=False),
                 source_flags=['subset_only'])
    path = tmp_path / 'packet.json'
    path.write_text(json.dumps(value))
    return path, value


def load(path, **kwargs):
    return load_risk_events(path, ['20240705', '20240708', '20240709'], **kwargs)


def test_bound_packet_and_conservative_time(tmp_path):
    path, _ = packet(tmp_path)
    events, audit = load(path, expected_symbols={'600836.SH'})
    assert events.symbol.tolist() == ['600836.SH']
    assert events.available_time.tolist() == ['2024-07-08T09:00:00+08:00']
    assert audit['coverage']['all_market_announcement_coverage'] is False
    json.dumps(audit, allow_nan=False)


@pytest.mark.parametrize('case', ['hash', 'facts_hash', 'fact_mismatch', 'duplicate_identity',
                                 'naive_time', 'early_time', 'unknown_ref', 'duplicate_ref',
                                 'incomplete', 'missing_primary', 'extra_fact'])
def test_reject_unbound_or_invalid_packet(tmp_path, case):
    path, value = packet(tmp_path)
    if case == 'hash':
        (tmp_path / 'notice.pdf').write_bytes(b'tampered')
    elif case == 'facts_hash':
        (tmp_path / 'facts.json').write_text('{}')
    elif case in ('fact_mismatch', 'missing_primary', 'extra_fact'):
        facts = json.loads((tmp_path / 'facts.json').read_text())
        if case == 'fact_mismatch':
            facts['events'][0]['symbol'] = '000001.SZ'
        elif case == 'missing_primary':
            facts['events'][0]['primary_file_ref'] = 'missing'
        else:
            facts['events'].append(dict(facts['events'][0], event_id='other'))
        (tmp_path / 'facts.json').write_text(json.dumps(facts))
        digest = hashlib.sha256((tmp_path / 'facts.json').read_bytes()).hexdigest()
        value['facts_ref']['sha256'] = digest
        value['source_refs'][1]['sha256'] = digest
    elif case == 'duplicate_identity':
        value['events'].append(value['events'][0])
    elif case == 'naive_time':
        value['events'][0]['available_time'] = '2024-07-08T09:00:00'
    elif case == 'early_time':
        value['events'][0]['available_time'] = '2024-07-05T09:00:00+08:00'
    elif case == 'unknown_ref':
        value['events'][0]['source_refs'] = ['missing']
    elif case == 'duplicate_ref':
        value['source_refs'].append(value['source_refs'][0])
    elif case == 'incomplete':
        value['coverage']['complete_for_scope'] = False
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        load(path)


def test_expected_coverage_and_calendar_rejected(tmp_path):
    path, _ = packet(tmp_path)
    with pytest.raises(ValueError):
        load(path, expected_symbols={'600836.SH', '000982.SZ'})
    with pytest.raises(ValueError):
        load_risk_events(path, ['20240705'])
    with pytest.raises(ValueError):
        load_risk_events(path, [pd.NaT])
