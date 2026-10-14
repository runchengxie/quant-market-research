import json

import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.diagnostics import analyze_run


def fixture(root, nav=971):
    run = root / 'test'
    run.mkdir()
    (run / 'receipt.json').write_text(json.dumps({'config': {'initial_cash': 1000, 'participation_rate': .05}}))
    (root / 'inputs.json').write_text('{}')
    (root / 'corporate-actions.json').write_text(json.dumps([dict(event_id='d', symbol='A', record_date='20240102', ex_date='20240103', cash_pay_date='20240104', stock_tradable_date=None, cash_per_share=1, stock_per_share=0, withholding_rate=0)]))
    t = pd.Timestamp('2024-01-02 10:00', tz='Asia/Shanghai')
    pd.DataFrame([dict(symbol='A', time=t, close=10, high=10, down_limit=10, volume=0, tradable=False)]).to_parquet(root / 'bars.parquet')
    pd.DataFrame([dict(order_id=0, symbol='A', time=t, side='buy', quantity=10, gross_amount=100, transaction_cost=1), dict(order_id=1, symbol='A', time=t+pd.Timedelta(days=1), side='sell', quantity=4, gross_amount=60, transaction_cost=0)]).to_parquet(run / 'fills.parquet')
    pd.DataFrame([dict(order_id=1, symbol='A', side='sell', quantity=10, filled_quantity=4, entry_time=t+pd.Timedelta(days=1), deadline=t+pd.Timedelta(days=1, hours=1)), dict(order_id=2, symbol='A', side='sell', quantity=6, filled_quantity=0, entry_time=t+pd.Timedelta(days=2), deadline=t+pd.Timedelta(days=2, hours=1))]).to_parquet(run / 'orders.parquet')
    pd.DataFrame([dict(date='2024-01-02', symbol='A', quantity=10), dict(date='2024-01-03', symbol='A', quantity=6), dict(date='2024-01-04', symbol='A', quantity=6)]).to_parquet(run / 'holdings.parquet')
    pd.DataFrame([dict(date='2024-01-02', nav=999), dict(date='2024-01-03', nav=969), dict(date='2024-01-04', nav=nav)]).to_parquet(run / 'daily.parquet')
    pd.DataFrame([dict(symbol='A', time=t+pd.Timedelta(days=1), value_per_share=0, previous_value_per_share=10, cash_before=959, cash_after=959)]).to_parquet(run / 'valuation-ledger.parquet')
    return root


def test_partial_exit_dividend_and_zero_mark(tmp_path):
    report = analyze_run(fixture(tmp_path, nav=969), 'test')
    row = report['symbols']['A']
    assert row['cash_dividend_paid'] == 10
    assert row['pnl'] == -31
    assert report['exit']['partial_sell_orders'] == 1
    assert report['exit']['zero_fill_sell_orders'] == 1
    assert report['exit']['terminal_trapped_marked_value'] == 0
    assert report['exit']['terminal_trapped_pre_impairment_value'] == 60
    json.dumps(report, allow_nan=False)


def test_refuses_unreconciled_nav(tmp_path):
    with pytest.raises(ValueError, match='NAV reconciliation'):
        analyze_run(fixture(tmp_path), 'test')


def test_same_day_sale_refused(tmp_path):
    root = fixture(tmp_path)
    p = root / 'test/fills.parquet'
    fills = pd.read_parquet(p)
    fills.loc[1, 'time'] = fills.loc[0, 'time']
    fills.to_parquet(p)
    with pytest.raises(ValueError, match='T.plus.one'):
        analyze_run(root, 'test')


def test_unpaid_cash_and_stock_rights(tmp_path):
    root = fixture(tmp_path, nav=976)
    actions = json.loads((root / 'corporate-actions.json').read_text())
    actions[0].update(cash_pay_date='20240105', stock_per_share=.1, stock_tradable_date='20240105')
    (root / 'corporate-actions.json').write_text(json.dumps(actions))
    ledger_path = root / 'test/valuation-ledger.parquet'
    ledger = pd.read_parquet(ledger_path)
    ledger['value_per_share'] = 1
    ledger.to_parquet(ledger_path)
    # NAV 959 cash + 6 inventory + 10 cash rights + 1 stock right.
    report = analyze_run(root, 'test')
    assert report['symbols']['A']['cash_dividend_unpaid'] == 10
    assert report['symbols']['A']['stock_receivable_value'] == 1


def test_failed_exit_without_sales_and_overlapping_blockers(tmp_path):
    root = fixture(tmp_path, nav=909)
    fills_path = root / 'test/fills.parquet'
    pd.read_parquet(fills_path).iloc[:1].to_parquet(fills_path)
    holdings_path = root / 'test/holdings.parquet'
    holdings = pd.read_parquet(holdings_path)
    holdings['quantity'] = 10
    holdings.to_parquet(holdings_path)
    orders_path = root / 'test/orders.parquet'
    orders = pd.read_parquet(orders_path)
    orders['filled_quantity'] = 0
    orders.to_parquet(orders_path)
    bars_path = root / 'bars.parquet'
    bars = pd.read_parquet(bars_path)
    bars['time'] += pd.Timedelta(days=1)
    bars['tradable'] = True
    bars.to_parquet(bars_path)
    report = analyze_run(root, 'test')
    assert report['symbols']['A']['sell_gross'] == 0
    assert report['exit']['terminal_trapped_quantities'] == {'A': 10}
    window = report['exit']['order_windows'][0]
    assert window['limit_down_bars'] == window['zero_volume_bars'] == 1
    assert report['exit']['longest_failed_sell_session_span'] == 2


def test_absent_previous_session_holding_does_not_resurrect_inventory(tmp_path):
    root = fixture(tmp_path, nav=1000)
    (root / 'corporate-actions.json').write_text('[]')
    run = root / 'test'
    t = pd.Timestamp('2024-01-02 10:00', tz='Asia/Shanghai')
    pd.DataFrame([
        dict(order_id=i, symbol='A', time=t+pd.Timedelta(days=day, minutes=minute),
             side=side, quantity=10, gross_amount=100, transaction_cost=0)
        for i, (day, minute, side) in enumerate([(0, 0, 'buy'), (1, 0, 'sell'), (2, 0, 'buy'), (2, 1, 'sell')])
    ]).to_parquet(run / 'fills.parquet')
    pd.DataFrame([dict(date='2024-01-02', symbol='A', quantity=10)]).to_parquet(run / 'holdings.parquet')
    pd.DataFrame([dict(date=f'2024-01-0{day}', nav=1000) for day in [2, 3, 4]]).to_parquet(run / 'daily.parquet')
    with pytest.raises(ValueError, match='T.plus.one'):
        analyze_run(root, 'test')


def test_fill_session_dates_use_exchange_timezone(tmp_path):
    root = fixture(tmp_path, nav=969)
    path = root / 'test/fills.parquet'
    fills = pd.read_parquet(path)
    # A next-session 00:30 Shanghai sale appears on the prior UTC date.
    fills.loc[1, 'time'] = pd.Timestamp('2024-01-03 00:30', tz='Asia/Shanghai')
    fills['time'] = fills.time.dt.tz_convert('UTC')
    fills.to_parquet(path)
    assert analyze_run(root, 'test')['pnl'] == -31


def test_capacity_excludes_limit_touch_and_pre_activation_intervals(tmp_path):
    root = fixture(tmp_path, nav=969)
    t = pd.Timestamp('2024-01-03 10:00', tz='Asia/Shanghai')
    pd.DataFrame([
        dict(symbol='A', time=t+pd.Timedelta(minutes=2), interval_start=t+pd.Timedelta(minutes=1), close=11, high=12, low=10, down_limit=10, volume=1000, tradable=True),
        dict(symbol='A', time=t+pd.Timedelta(minutes=3), interval_start=t-pd.Timedelta(minutes=1), close=11, high=12, low=11, down_limit=10, volume=1000, tradable=True),
    ]).to_parquet(root / 'bars.parquet')
    window = analyze_run(root, 'test')['exit']['order_windows'][0]
    assert window['observed_participation_capacity'] == 0
    assert window['provider_limit_touch_bars'] == 1
    assert window['limit_down_bars'] == 0
    assert window['interval_activation_verified']
    assert window['capacity_is_upper_bound']
