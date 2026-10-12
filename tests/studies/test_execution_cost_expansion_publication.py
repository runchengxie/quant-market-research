import pytest

from market_research.studies.ashare_execution_costs.expansion_publication import public_expansion, public_strategy


def test_expansion_export_drops_paths_ids_and_unknown_nested_fields():
    private = {'study_id':'ashare_execution_costs','inputs':[{'path':'/private/source','sha256':'a'*64,
        'bytes':100,'metadata_rows':20,'clock_profile':'relative_0930_ms'}],
        'audit':[{'day':20210104,'valid_books':10,'SecuCode':37}],
        'event_audit':{'20210104':{'orders':{'rows':5,'timestamp_regressions':1,'raw_records':[37]},
            'references':[{'candidate':'OrderID','eligible_positive_trade_rows':2,
                'identity_scope':'security_only_channel_unavailable','buy':{'matched':1,'path':'/private'}}]}},
        'comparison':{'days':[20210104,20260416],'common_securities':10,'security_ids':[37]},
        'raw_ids':[37]}
    result = public_expansion(private,confirmed_on='2026-10-12')
    assert '/private' not in str(result)
    assert 'SecuCode' not in str(result)
    assert 'raw_records' not in str(result)
    assert result['event_audit']['20210104']['orders']['timestamp_regressions'] == 1
    assert result['comparison']['common_securities'] == 10


def test_export_rejects_nonfinite_numbers_and_unknown_profile():
    with pytest.raises(ValueError):
        public_expansion({'study_id':'ashare_execution_costs','audit':[{'day':float('nan')}]},confirmed_on='2026-10-12')
    with pytest.raises(ValueError,match='profile'):
        public_expansion({'study_id':'ashare_execution_costs','inputs':[{'sha256':'a'*64,'bytes':1,
            'metadata_rows':1,'clock_profile':'guess'}]},confirmed_on='2026-10-12')


def test_strategy_export_keeps_scenarios_and_suppresses_private_receipt_fields():
    rows = [{'capital_cny':10000000,'scenario':'gross','terminal_nav':1.1,'raw_symbol':'secret'}]
    result = public_strategy(rows,[],[],{'source_period':['20250103','20250331'],
        'source_sha256':{'fills':'a'*64},'private_path':'/private','simulator_configuration':{'participation_rate':0.05,'instrument_metadata':{'secret':{}}}},
        confirmed_on='2026-10-12')
    assert 'secret' not in str(result)
    assert '/private' not in str(result)
    assert result['modeled'][0]['terminal_nav'] == 1.1
    assert result['configuration']['participation_rate'] == 0.05


def test_strategy_export_rejects_unreviewed_scenario_names():
    with pytest.raises(ValueError,match='scenario'):
        public_strategy([{'capital_cny':10000000,'scenario':'secret_strategy'}],[],[],{},confirmed_on='2026-10-12')


def test_market_segments_are_scrubbed_and_zero_sequences_remain_visible():
    value = {'study_id':'ashare_execution_costs','event_audit':{'20210104':{'by_market':{
        'shanghai':{'orders':{'rows':0,'raw_id':123}},
        'shenzhen':{'trades':{'rows':10,'nonpositive_sequence_rows':10,'sequence_available':True}},
        '/private':{'orders':{'rows':1}}}}}}
    result = public_expansion(value,confirmed_on='2026-10-12')
    markets = result['event_audit']['20210104']['by_market']
    assert markets['shanghai']['orders']['rows'] == 0
    assert markets['shenzhen']['trades']['sequence_column_present'] is True
    assert markets['shenzhen']['trades']['nonpositive_sequence_rows'] == 10
    assert 'raw_id' not in str(result) and '/private' not in str(result)
