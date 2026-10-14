import json

import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.minute import build_targets
from market_research.studies.ashare_execution_costs.risk_guards import build_risk_targets


def panel():
    return pd.DataFrame([
        dict(ts_code=code, trade_date=day, total_mv=mv, close=1., amount=1000.,
             is_st=False, st_available_from=None, is_suspended=False,
             list_date='20200101', delist_date=None)
        for day in ('20250102', '20250103', '20250106')
        for code, mv in [('000001.SZ', 1.), ('000002.SZ', 2.), ('000003.SZ', 3.)]
    ])


def event(time='2025-01-02T20:03:00+08:00'):
    return pd.DataFrame([dict(symbol='000001.SZ', available_time=time,
                              event_id='termination-1', event_type='confirmed_termination')])


def test_threshold_equality_baseline_and_no_mutation():
    source = panel()
    original = source.copy(deep=True)
    targets, audit = build_risk_targets(source, count=1)
    pd.testing.assert_frame_equal(targets, build_targets(source, count=1))
    pd.testing.assert_frame_equal(source, original)
    json.dumps(audit, allow_nan=False)
    source.loc[source.ts_code.eq('000001.SZ'), 'close'] = .99
    guarded, audit = build_risk_targets(source, count=1)
    assert guarded.symbol.tolist() == ['000002.SZ', '000002.SZ']
    assert audit['dates'][0]['excluded_by_reason']['below_minimum_close'] == 1


def test_announcement_boundary_permanent_exclusion_and_future_invariance():
    source = panel()
    targets, _ = build_risk_targets(source, count=1, risk_events=event())
    assert targets.symbol.tolist() == ['000001.SZ', '000002.SZ']
    exact, _ = build_risk_targets(source, count=1,
                                risk_events=event('2025-01-02T20:02:00+08:00'))
    assert exact.symbol.tolist() == ['000002.SZ', '000002.SZ']
    future, _ = build_risk_targets(source, count=1,
                                 risk_events=event('2026-01-02T20:02:00+08:00'))
    pd.testing.assert_frame_equal(future, build_targets(source, count=1))


def test_st_unknown_contradictory_and_future_excluded():
    source = panel()
    source.loc[source.ts_code.eq('000001.SZ'), ['is_st', 'st_available_from']] = [True, '20260101']
    source.loc[source.ts_code.eq('000002.SZ'), 'st_available_from'] = '20250102'
    targets, audit = build_risk_targets(source, count=1)
    assert targets.symbol.tolist() == ['000003.SZ', '000003.SZ']
    assert audit['dates'][0]['excluded_by_reason']['st_unknown_or_contradictory'] == 2


def test_buffer_does_not_retain_guarded_name_complete_snapshot_for_exit():
    source = panel()
    source.loc[source.trade_date.eq('20250103') & source.ts_code.eq('000001.SZ'), 'close'] = .5
    targets, _ = build_risk_targets(source, count=1, buffer_multiple=3)
    assert targets.symbol.tolist() == ['000001.SZ', '000002.SZ']
    assert targets.groupby('decision_time').weight.sum().eq(1).all()


@pytest.mark.parametrize('value', [0, -1, float('inf'), float('nan'), True])
def test_invalid_threshold(value):
    with pytest.raises(ValueError):
        build_risk_targets(panel(), count=1, minimum_close=value)


@pytest.mark.parametrize('field,value', [
    ('available_time', '2025-01-02T20:02:00'), ('available_time', None),
    ('available_time', 'nonsense'), ('event_id', None), ('event_id', ''),
    ('symbol', None), ('event_type', 'delist_date'),
])
def test_invalid_event(field, value):
    events = event()
    events.loc[0, field] = value
    with pytest.raises(ValueError):
        build_risk_targets(panel(), count=1, risk_events=events)


def test_duplicate_event_and_insufficient_candidates_rejected():
    with pytest.raises(ValueError):
        build_risk_targets(panel(), count=1, risk_events=pd.concat([event(), event()]))
    with pytest.raises(ValueError, match='insufficient'):
        build_risk_targets(panel(), count=3, risk_events=event())


def test_unknown_st_and_invalid_availability_are_ineligible():
    source = panel()
    source['is_st'] = source.is_st.astype('boolean')
    source.loc[source.ts_code.eq('000001.SZ'), 'is_st'] = None
    source.loc[source.ts_code.eq('000002.SZ'), 'st_available_from'] = 'bad-date'
    targets, _ = build_risk_targets(source, count=1)
    assert targets.symbol.tolist() == ['000003.SZ', '000003.SZ']


def test_future_panel_changes_do_not_change_past_decision():
    source = panel()
    before, _ = build_risk_targets(source, count=1)
    source.loc[source.trade_date.eq('20250106'), ['close', 'total_mv']] = [.01, 9999.]
    after, _ = build_risk_targets(source, count=1)
    pd.testing.assert_frame_equal(before, after)


def test_duplicate_input_indices_are_supported():
    source = panel()
    expected, audit = build_risk_targets(source, count=1)
    source.index = [0] * len(source)
    actual, actual_audit = build_risk_targets(source, count=1)
    pd.testing.assert_frame_equal(expected, actual)
    assert actual_audit == audit


def test_missing_st_availability_rejected():
    with pytest.raises(ValueError, match='st_available_from'):
        build_risk_targets(panel().drop(columns='st_available_from'), count=1)


def ablation_panel():
    source = panel()
    extra = source.loc[source.ts_code.eq('000003.SZ')].copy()
    extra['ts_code'] = '000004.SZ'
    extra['total_mv'] = 4.
    source = pd.concat([source, extra], ignore_index=True)
    source.loc[source.ts_code.eq('000001.SZ'), 'close'] = .5
    source.loc[source.ts_code.eq('000002.SZ'), 'st_available_from'] = '20250102'
    return source


@pytest.mark.parametrize('active,expected,reason', [
    ('guard_price', '000002.SZ', 'below_minimum_close'),
    ('guard_st_availability', '000001.SZ', 'st_unknown_or_contradictory'),
    ('guard_termination', '000001.SZ', 'confirmed_termination'),
])
def test_each_guard_applies_only_its_own_exclusion(active, expected, reason):
    source = ablation_panel()
    events = event('2025-01-02T20:02:00+08:00')
    events['symbol'] = '000003.SZ'
    switches = dict(guard_price=False, guard_st_availability=False, guard_termination=False)
    switches[active] = True
    targets, audit = build_risk_targets(source, count=2, risk_events=events, **switches)
    expected_symbols = {
        'guard_price': ['000002.SZ', '000003.SZ'],
        'guard_st_availability': ['000001.SZ', '000003.SZ'],
        'guard_termination': ['000001.SZ', '000002.SZ'],
    }
    assert targets.symbol.tolist() == expected_symbols[active] * 2
    assert targets.symbol.iloc[0] == expected
    assert audit['active_guards'] == [active]
    assert {k: audit['parameters'][k] for k in switches} == switches
    for day in audit['dates']:
        assert day['excluded_by_reason'][reason] == 1
        assert sum(day['excluded_by_reason'].values()) == 1
        assert day['excluded_candidates'][reason] == [{
            'guard_price': '000001.SZ', 'guard_st_availability': '000002.SZ',
            'guard_termination': '000003.SZ',
        }[active]]


def test_all_guards_disabled_preserves_baseline_buffer_and_inputs():
    source = ablation_panel().drop(columns='st_available_from')
    source.loc[source.trade_date.eq('20250103') & source.ts_code.eq('000003.SZ'), 'total_mv'] = .1
    source.loc[source.ts_code.eq('000004.SZ'), 'is_st'] = True
    original = source.copy(deep=True)
    events = event('2025-01-02T20:02:00+08:00')
    original_events = events.copy(deep=True)
    targets, audit = build_risk_targets(
        source, count=2, buffer_multiple=2, risk_events=events,
        guard_price=False, guard_st_availability=False, guard_termination=False,
    )
    pd.testing.assert_frame_equal(targets, build_targets(source, count=2, buffer_multiple=2))
    pd.testing.assert_frame_equal(source, original)
    pd.testing.assert_frame_equal(events, original_events)
    assert '000004.SZ' not in targets.symbol.tolist()
    assert audit['active_guards'] == []
    assert all(sum(day['excluded_by_reason'].values()) == 0 for day in audit['dates'])
    json.dumps(audit, allow_nan=False)


def test_explicit_all_guards_matches_defaults():
    source = ablation_panel()
    defaults, audit = build_risk_targets(source, count=1, risk_events=event())
    explicit, explicit_audit = build_risk_targets(
        source, count=1, risk_events=event(), guard_price=True,
        guard_st_availability=True, guard_termination=True,
    )
    pd.testing.assert_frame_equal(defaults, explicit)
    assert audit == explicit_audit


@pytest.mark.parametrize('switch', ['guard_price', 'guard_st_availability', 'guard_termination'])
@pytest.mark.parametrize('value', [0, 1, None, 'false'])
def test_guard_switches_require_actual_bool(switch, value):
    with pytest.raises(ValueError, match=switch):
        build_risk_targets(panel(), count=1, **{switch: value})


def test_disabled_termination_still_validates_supplied_event_source():
    events = event('not-a-timestamp')
    with pytest.raises(ValueError, match='available_time'):
        build_risk_targets(panel(), count=1, risk_events=events, guard_termination=False)
