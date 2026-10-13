import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.minute import (
    build_targets, prepare_minute_bars, normalize_dividends,
    assert_unowned_events,
    apply_dividend_overrides, audit_adjustment_events,
    measure_arrival_shortfall,
    add_suspension_marks,
)


def panel():
    rows = []
    for day in ('20250102', '20250103', '20250106'):
        for code, mv in [('000001.SZ', 1), ('000002.SZ', 2), ('000003.SZ', 3)]:
            rows.append(dict(ts_code=code, trade_date=day, total_mv=float(mv), close=10.,
                             amount=1000., is_st=False, is_suspended=False,
                             list_date='20200101', delist_date=None))
    return pd.DataFrame(rows)


def test_targets_next_session_buffer_and_frequency_are_decision_only():
    source = panel()
    source.loc[(source.trade_date == '20250103') & (source.ts_code == '000001.SZ'), 'total_mv'] = 2.5
    targets = build_targets(source, count=1, rebalance_sessions=1, buffer_multiple=3)
    assert targets.symbol.tolist() == ['000001.SZ', '000001.SZ']
    assert (targets.decision_time < targets.entry_time).all()
    changed = source.copy()
    changed.loc[changed.trade_date == '20250106', 'total_mv'] = 999
    pd.testing.assert_frame_equal(targets, build_targets(changed, count=1, rebalance_sessions=1,
                                                       buffer_multiple=3))
    assert len(build_targets(source, count=1, rebalance_sessions=2)) == 1
    assert build_targets(source, count=1).symbol.tolist() == ['000001.SZ', '000002.SZ']


def test_minute_inputs_preserve_units_and_delay_bar_availability():
    raw = pd.DataFrame(dict(ts_code=['000001.SZ']*2,
                            trade_time=pd.to_datetime(['2025-01-03 09:31', '2025-01-03 15:00']),
                            open=[10., 10.], high=[10., 10.], low=[10., 10.], close=[10., 10.],
                            vol=[1000., 100.], amount=[10000., 1000.]))
    marks = pd.DataFrame(dict(ts_code=['000001.SZ'], trade_date=['20250103'], close=[10.],
                             up_limit=[11.], down_limit=[9.], is_suspended=[False]))
    bars, audit = prepare_minute_bars(raw, marks)
    assert bars.iloc[0].time == pd.Timestamp('2025-01-03 09:32', tz='Asia/Shanghai')
    assert bars.iloc[0].interval_start == pd.Timestamp('2025-01-03 09:30', tz='Asia/Shanghai')
    assert bars.iloc[0].volume == 1000
    assert bars.iloc[0].amount == 10000
    assert not bars.iloc[-1].tradable
    assert audit['availability_policy'] == 'source_wallclock_plus_one_minute'
    with pytest.raises(ValueError, match='duplicate'):
        prepare_minute_bars(pd.concat([raw, raw.iloc[:1]]), marks)


def dividend():
    return dict(ts_code='000001.SZ', end_date='20241231', div_proc='实施',
                imp_ann_date='20250101', ann_date='20241220', record_date='20250103',
                ex_date='20250106', pay_date='20250106', div_listdate=None,
                cash_div_tax=0.1, stk_div=0.)


def test_dividend_exact_duplicates_are_not_double_counted_and_conflicts_block():
    row = dividend()
    events, audit = normalize_dividends(pd.DataFrame([row, row]), {'000001.SZ'},
                                      start='20250102', end='20250110')
    assert len(events) == 1
    assert events[0]['cash_per_share'] == .1
    assert audit['exact_duplicates_removed'] == 1
    with pytest.raises(ValueError, match='conflicting'):
        normalize_dividends(pd.DataFrame([row, dict(row, cash_div_tax=.2)]), {'000001.SZ'},
                            start='20250102', end='20250110')


def test_dividend_unknown_dates_or_availability_never_become_zero_cash():
    with pytest.raises(ValueError, match='pay_date'):
        normalize_dividends(pd.DataFrame([dict(dividend(), pay_date=None)]), {'000001.SZ'},
                            start='20250102', end='20250110')
    with pytest.raises(ValueError, match='availability'):
        normalize_dividends(pd.DataFrame([dict(dividend(), imp_ann_date='20250107')]),
                            {'000001.SZ'}, start='20250102', end='20250110')


def test_unknown_status_and_unlisted_names_cannot_enter_targets():
    source = panel()
    source['is_st'] = source.is_st.astype('boolean')
    source.loc[source.ts_code == '000001.SZ', 'is_st'] = None
    source.loc[source.ts_code == '000002.SZ', 'list_date'] = '20260101'
    assert set(build_targets(source, count=1).symbol) == {'000003.SZ'}


def test_unverified_reorganization_cannot_be_ignored_when_held():
    blocked = [{'symbol': 'A', 'record_dates': ['20250103']}]
    holdings = pd.DataFrame(dict(date=[pd.Timestamp('20250103').date()], symbol=['A'], quantity=[100.]))
    with pytest.raises(ValueError, match='held'):
        assert_unowned_events(holdings, ['20250103'], blocked)
    assert assert_unowned_events(holdings.iloc[:0], ['20250103'], blocked) == 1
    with pytest.raises(ValueError, match='coverage'):
        assert_unowned_events(holdings.iloc[:0], [], blocked)


def test_primary_announcement_override_is_explicit_and_preserves_raw():
    row = dividend()
    raw = pd.DataFrame([dict(row, cash_div_tax=None, stk_div=.4)])
    fixed = apply_dividend_overrides(raw, [{'symbol': '000001.SZ', 'ex_date': '20250106',
                                         'cash_per_share': 0., 'stock_per_share': .4,
                                         'kind': 'ordinary_distribution', 'source_url': 'https://issuer/a',
                                         'stock_listing_date': '20250106',
                                         'source_pdf_sha256': 'a'*64}])
    assert raw.cash_div_tax.isna().all()
    events, _ = normalize_dividends(fixed, {'000001.SZ'}, start='20250102', end='20250110')
    assert events[0]['stock_per_share'] == .4
    assert events[0]['cash_per_share'] == 0


def test_unexplained_adjustment_factor_change_blocks_complete_accounting():
    marks = pd.DataFrame(dict(ts_code=['A', 'A'], trade_date=['20250102', '20250103'],
                             adj_factor=[1., 1.1]))
    with pytest.raises(ValueError, match='unexplained'):
        audit_adjustment_events(marks, set())
    assert audit_adjustment_events(marks, {('A', '20250103')})['explained_changes'] == 1


def test_partial_fill_shortfall_includes_unfilled_quantity_without_future_quotes():
    deadline = pd.Timestamp('20250103 10:00', tz='Asia/Shanghai')
    orders = pd.DataFrame([dict(order_id=0, symbol='A', side='buy', quantity=100., filled_quantity=60.,
                                reference_price=10., deadline=deadline)])
    fills = pd.DataFrame([dict(order_id=0, gross_amount=660., quantity=60., transaction_cost=1.)])
    bars = pd.DataFrame(dict(symbol=['A', 'A'], time=[deadline, deadline+pd.Timedelta(minutes=1)],
                             close=[12., 999.]))
    measured, summary = measure_arrival_shortfall(orders, fills, bars)
    assert measured.iloc[0].arrival_shortfall_cny == 141.
    assert measured.iloc[0].unfilled_opportunity_cny == 80.
    assert summary['target_notional_completion'] == .6
    bars.loc[1, 'close'] = 1.
    changed, _ = measure_arrival_shortfall(orders, fills, bars)
    pd.testing.assert_frame_equal(measured, changed)
    missing, summary = measure_arrival_shortfall(orders, fills, bars.iloc[:0])
    assert missing.arrival_shortfall_cny.isna().all()
    assert summary['cost_available_orders'] == 0
    assert summary['unfilled_opportunity_cny'] is None


def test_confirmed_full_day_suspension_can_carry_value_but_never_liquidity():
    bar = dict(symbol='A', time=pd.Timestamp('20250102 15:01', tz='Asia/Shanghai'),
               interval_start=pd.Timestamp('20250102 14:59', tz='Asia/Shanghai'),
               open=10., high=10., low=10., close=10., volume=100., amount=1000.,
               up_limit=11., down_limit=9., tradable=False)
    events = pd.DataFrame(dict(ts_code=['A'], trade_date=['20250103'],
                              suspend_type=['S'], suspend_timing=[None]))
    bars, audit = add_suspension_marks(pd.DataFrame([bar]), events, ['20250102', '20250103'], [])
    carried = bars.iloc[-1]
    assert carried.close == 10.
    assert carried.volume == carried.amount == 0.
    assert not carried.tradable
    assert carried.mark_basis == 'confirmed_suspension_carry'
    assert audit['carried_symbol_days'] == 1
    ignored, audit = add_suspension_marks(pd.DataFrame([bar]), events.assign(suspend_timing='09:30-10:00'),
                                         ['20250102', '20250103'], [])
    assert len(ignored) == 1
    assert audit['carried_symbol_days'] == 0


def test_shortfall_accepts_native_parquet_and_runtime_timestamp_resolutions():
    deadline = pd.Timestamp('20250103 10:00', tz='Asia/Shanghai')
    orders = pd.DataFrame([dict(order_id=0, symbol='A', side='buy', quantity=100., filled_quantity=100.,
                                reference_price=10., deadline=deadline)])
    orders['deadline'] = orders.deadline.dt.as_unit('us')
    fills = pd.DataFrame([dict(order_id=0, gross_amount=1000., quantity=100., transaction_cost=1.)])
    bars = pd.DataFrame(dict(symbol=['A'], time=[deadline], close=[10.]))
    bars['time'] = bars.time.dt.as_unit('ns')
    result, _ = measure_arrival_shortfall(orders, fills, bars)
    assert result.iloc[0].arrival_shortfall_cny == 1.
