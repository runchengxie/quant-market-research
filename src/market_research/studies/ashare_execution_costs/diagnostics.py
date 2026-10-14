"""Independent accounting and observed exit diagnostics for prepared minute runs.

No asset is removed or cash recovery inferred. Differences are accounting
attributions, not estimates of causal strategy effects or own market impact.
"""
from collections import defaultdict
import json
import math
from pathlib import Path

import pandas as pd


def _day(value):
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert('Asia/Shanghai')
    return timestamp.strftime('%Y%m%d')


def analyze_run(prepared_root: Path, scenario: str) -> dict:
    """Read a frozen run and refuse to report unreconciled terminal P&L."""
    root = Path(prepared_root)
    if Path(scenario).name != scenario or scenario in {'.', '..'}:
        raise ValueError('scenario must be a directory name')
    run = root / scenario
    json.loads((root / 'inputs.json').read_text())
    cfg = json.loads((run / 'receipt.json').read_text())['config']
    initial = float(cfg['initial_cash'])
    daily = pd.read_parquet(run / 'daily.parquet').sort_values('date')
    fills = pd.read_parquet(run / 'fills.parquet').sort_values('time')
    orders = pd.read_parquet(run / 'orders.parquet')
    holdings = pd.read_parquet(run / 'holdings.parquet')
    bars = pd.read_parquet(root / 'bars.parquet').sort_values('time')
    bars_by_symbol = {s: g for s, g in bars.groupby('symbol', sort=False)}
    ledger_path = run / 'valuation-ledger.parquet'
    ledger = pd.read_parquet(ledger_path).sort_values('time') if ledger_path.exists() else pd.DataFrame()
    actions_path = root / 'corporate-actions.json'
    actions = json.loads(actions_path.read_text()) if actions_path.exists() else []
    end = _day(daily.iloc[-1]['date'])
    if len(ledger):
        if (ledger.time.dt.strftime('%Y%m%d') > end).any():
            raise ValueError('valuation ledger extends beyond terminal session')
        if {'cash_before', 'cash_after'} <= set(ledger):
            if (ledger.cash_before != ledger.cash_after).any():
                raise ValueError('nontrading valuation must not change cash')
    symbols = sorted(set(fills.symbol) | set(holdings.symbol) | set(orders.symbol))
    rows = {s: dict(buy_gross=0., sell_gross=0., fees=0., cash_dividend_paid=0.,
                    cash_dividend_unpaid=0., stock_receivable_value=0.) for s in symbols}
    holdings = holdings.assign(day=pd.to_datetime(holdings.date).dt.strftime('%Y%m%d'))
    holdings_by_symbol = {s: g.sort_values('date') for s, g in holdings.groupby('symbol', sort=False)}
    account_sessions = sorted(set(daily.date.map(_day)))
    previous_session = {day: account_sessions[i-1] if i else ''
                        for i, day in enumerate(account_sessions)}
    sold_today = defaultdict(float)
    prior_day = None
    for f in fills.itertuples():
        day = _day(f.time)
        if day != prior_day:
            sold_today.clear()
            prior_day = day
        if f.side == 'sell':
            symbol_holdings = holdings_by_symbol.get(f.symbol, holdings.iloc[:0])
            if day not in previous_session:
                raise ValueError('fill falls outside recorded account sessions')
            previous_day = previous_session[day]
            previous = symbol_holdings.loc[symbol_holdings.day == previous_day]
            available = float(previous.iloc[-1].quantity) if len(previous) else 0.
            for action in actions:
                release = action.get('stock_tradable_date')
                if action['symbol'] == f.symbol and release and previous_day < release <= day:
                    record = symbol_holdings.loc[symbol_holdings.day == action['record_date']]
                    available += (float(record.iloc[-1].quantity) if len(record) else 0.) * float(action['stock_per_share'])
            sold_today[f.symbol] += float(f.quantity)
            if sold_today[f.symbol] > available + 1e-8:
                raise ValueError('T-plus-one sale exceeds prior closing holdings plus released rights')
        row = rows[f.symbol]
        row[f'{f.side}_gross'] += float(f.gross_amount)
        row['fees'] += float(f.transaction_cost)
    stock_pending = defaultdict(float)
    for a in actions:
        sym = a['symbol']
        if sym not in rows or a['record_date'] > end:
            continue
        symbol_holdings = holdings_by_symbol.get(sym, holdings.iloc[:0])
        saved = symbol_holdings.loc[symbol_holdings.day == a['record_date']]
        q = float(saved.iloc[-1].quantity) if len(saved) else 0.
        if a['ex_date'] > end:
            continue
        cash = q * float(a['cash_per_share']) * (1 - float(a['withholding_rate']))
        paid = a.get('cash_pay_date') and a['cash_pay_date'] <= end
        rows[sym]['cash_dividend_paid' if paid else 'cash_dividend_unpaid'] += cash
        if not a.get('stock_tradable_date') or a['stock_tradable_date'] > end:
            stock_pending[sym] += q * float(a['stock_per_share'])
    terminal = holdings.loc[holdings.day == end]
    quantity = dict(zip(terminal.symbol, terminal.quantity))
    marked, exposure = {}, {}
    for sym in symbols:
        symbol_bars = bars_by_symbol.get(sym, bars.iloc[:0])
        observed = symbol_bars.loc[symbol_bars.time.dt.strftime('%Y%m%d') == end]
        declarations = ledger.loc[ledger.symbol == sym] if len(ledger) else ledger
        q = float(quantity.get(sym, 0))
        price = float(declarations.iloc[-1].value_per_share) if len(declarations) else (
            float(observed.iloc[-1].close) if len(observed) else None)
        if price is None and q + stock_pending[sym] > 1e-8:
            raise ValueError(f'missing terminal valuation: {sym}')
        price = price if price is not None else 0.
        if not math.isfinite(price) or price < 0:
            raise ValueError('terminal mark must be finite and nonnegative')
        reference = float(declarations.iloc[0].previous_value_per_share) if len(declarations) else price
        row = rows[sym]
        row.update(terminal_quantity=q, terminal_mark=price, inventory_value=q * price,
                   stock_receivable_value=stock_pending[sym] * price)
        row['pnl'] = (row['sell_gross'] - row['buy_gross'] - row['fees']
                      + row['cash_dividend_paid'] + row['cash_dividend_unpaid']
                      + row['inventory_value'] + row['stock_receivable_value'])
        marked[sym], exposure[sym] = q * price, q * reference
    final_nav = float(daily.iloc[-1].nav)
    residual = final_nav - initial - sum(r['pnl'] for r in rows.values())
    if not math.isfinite(residual) or abs(residual) > max(.05, abs(final_nav) * 1e-10):
        raise ValueError(f'NAV reconciliation failed: residual={residual}')
    sells = orders.loc[(orders.side == 'sell') & (orders.quantity > 0)].copy()
    blockers = []
    failed_symbols = set()
    longest = 0
    session_dates = sorted(set(daily.date.map(_day)))
    longest_sessions = 0
    for sym, group in sells.groupby('symbol'):
        streak = 0
        failure_start = None
        for o in group.sort_values('entry_time').itertuples():
            failed = o.filled_quantity < o.quantity
            streak = streak + 1 if failed else 0
            longest = max(longest, streak)
            if failed:
                failure_start = failure_start or _day(o.entry_time)
                duration = sum(failure_start <= d <= _day(o.deadline) for d in session_dates)
                longest_sessions = max(longest_sessions, duration)
            else:
                failure_start = None
            if failed:
                failed_symbols.add(sym)
            symbol_bars = bars_by_symbol.get(sym, bars.iloc[:0])
            window = symbol_bars.loc[(symbol_bars.time >= o.entry_time) & (symbol_bars.time <= o.deadline)]
            eligible = window.loc[window.tradable.astype(bool)]
            interval_verified = 'interval_start' in window and window.interval_start.notna().all()
            activated = eligible
            if interval_verified:
                activation = o.entry_time + pd.Timedelta(minutes=cfg.get('latency_minutes', 0))
                activated = eligible.loc[eligible.interval_start > activation]
            low_verified = 'low' in activated and activated.low.notna().all()
            capacity_bars = activated.loc[activated.low > activated.down_limit] if low_verified else activated.loc[activated.high > activated.down_limit]
            counts = dict(nontradable_bars=int((~window.tradable.astype(bool)).sum()),
                          limit_down_bars=int((eligible.high <= eligible.down_limit).sum()),
                          provider_limit_touch_bars=int((eligible.low <= eligible.down_limit).sum()) if 'low' in eligible else None,
                          zero_volume_bars=int((window.volume <= 0).sum()))
            capacity = float((capacity_bars.volume * cfg['participation_rate']).sum())
            blockers.append(dict(order_id=int(o.order_id), symbol=sym, **counts,
                                 missing_window_bars=len(window) == 0,
                                 observed_participation_capacity=capacity,
                                 capacity_is_upper_bound=True,
                                 interval_activation_verified=bool(interval_verified),
                                 provider_low_touch_verified=bool(low_verified),
                                 capacity_below_order=capacity < o.quantity,
                                 window_minutes=float((o.deadline-o.entry_time).total_seconds()/60)))
    trapped = [s for s in failed_symbols if quantity.get(s, 0) > 0]
    trapped_value = sum(marked[s] for s in trapped)
    return dict(schema='execution-diagnostics.v1', scenario=scenario, initial_capital=initial,
                final_nav=final_nav, pnl=final_nav-initial, reconciliation_residual=residual,
                symbols=rows, exit=dict(total_sell_orders=len(sells),
                    zero_fill_sell_orders=int((sells.filled_quantity == 0).sum()),
                    partial_sell_orders=int(((sells.filled_quantity > 0) & (sells.filled_quantity < sells.quantity)).sum()),
                    terminal_trapped_quantities={s: float(quantity[s]) for s in sorted(trapped)},
                    terminal_trapped_marked_value=trapped_value,
                    terminal_trapped_marked_value_nav_ratio=trapped_value/final_nav if final_nav else None,
                    terminal_trapped_pre_impairment_value=sum(exposure[s] for s in trapped),
                    longest_consecutive_failed_sell_orders=longest,
                    longest_failed_sell_session_span=longest_sessions, order_windows=blockers),
                limitations=['Blocker categories overlap; observed windows do not identify a unique expiry cause.',
                             'Nontradable bars include session exclusions; they do not alone prove suspension.',
                             'Participation capacity is an upper bound before lot rounding, slicing, T+1 and other orders; absent interval or low fields leave activation or limit-touch eligibility unverified.',
                             'Failure session spans run from first to last consecutive incomplete order, including intervening sessions without orders.',
                             'Accounting attribution is not causal attribution; no own market impact is estimated.',
                             'Trapped means terminal inventory with an observed incomplete sell attempt.'])
