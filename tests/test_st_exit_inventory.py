"""Exit evidence must never repair a missing entry or synthesize a return."""
import importlib.util
from pathlib import Path

import pandas as pd

spec = importlib.util.spec_from_file_location(
    'exit_audit', Path(__file__).parents[1] / 'scripts/audit_st_paired_exits.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_suspension_corroborates_absence_without_supplying_trade_or_return():
    rows = pd.DataFrame([dict(
        formation='20250331', execution='20250401', endpoint='20250506',
        ts_code='300117.SZ', name='issuer', n=50, arm='include_st', weight=.02,
        delist_date='20250430', terminal_before_end=True, resolved=False,
        entry_adj_close=None, end_adj_close=None, entry_valid=None, end_valid=None,
    )])
    original = rows.copy(deep=True)
    suspensions = pd.DataFrame([dict(ts_code='300117.SZ', trade_date='20250401',
                                    suspend_type='S')])
    result = module.inventory(rows, suspensions).iloc[0]
    assert result.entry_failure == 'missing_clean_row'
    assert result.entry_dated_suspension
    assert not result.end_dated_suspension
    assert result.resolution == 'unresolved'
    assert 'entry trade on scheduled date' in result.required_evidence
    assert 'forward_return' not in result.index
    pd.testing.assert_frame_equal(rows, original)


def test_resume_event_is_not_suspension_evidence_and_arm_weights_are_preserved():
    rows = pd.DataFrame([dict(
        formation='20230131', execution='20230201', endpoint='20230301',
        ts_code='X', name='issuer', n=100, arm='exclude_st', weight=.01,
        delist_date=None, terminal_before_end=False, resolved=False,
        entry_adj_close=1., end_adj_close=None, entry_valid=True, end_valid=None,
    )])
    events = pd.DataFrame([dict(ts_code='X', trade_date='20230301', suspend_type='R')])
    result = module.inventory(rows, events).iloc[0]
    assert not result.end_dated_suspension
    assert result.weight == .01
    assert result.arm == 'exclude_st'
    assert result.entry_failure == 'valid'
    assert result.resolution == 'unresolved'


def test_reviewed_identity_alias_only_links_suspension_evidence():
    rows = pd.DataFrame([dict(
        formation='20230131', execution='20230201', endpoint='20230301',
        ts_code='920039.BJ', name='issuer', n=100, arm='include_st', weight=.01,
        delist_date=None, terminal_before_end=False, resolved=False,
        entry_adj_close=1., end_adj_close=None, entry_valid=True, end_valid=None,
    )])
    events = pd.DataFrame([dict(ts_code='831039.BJ', trade_date='20230301',
                               suspend_type='S')])
    result = module.inventory(rows, events, {'920039.BJ': '831039.BJ'}).iloc[0]
    assert result.ts_code == '920039.BJ'
    assert result.end_suspension_evidence_code == '831039.BJ'
    assert result.end_dated_suspension
    assert result.resolution == 'unresolved'
