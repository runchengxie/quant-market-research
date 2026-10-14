"""Conserved accounting comparisons and prior-session descriptive market labels."""
import math

import pandas as pd


DEFAULT_AVOIDED = frozenset({'600321.SH', '000982.SZ'})


def compare_reports(baseline: dict, risk: dict, *, avoided_symbols=DEFAULT_AVOIDED) -> dict:
    """Split symbol P&L excluding fees, then account for the fee difference once."""
    capital = float(baseline['initial_capital'])
    if capital <= 0 or risk['initial_capital'] != capital:
        raise ValueError('paired reports require the same positive initial capital')
    avoided = set(avoided_symbols)
    if '002621.SZ' in avoided:
        raise ValueError('retained symbol cannot also be avoided')
    deltas = {}
    buckets = dict(avoided_two_gross_pnl_delta=0., retained_002621_gross_pnl_delta=0.,
                   other_replacement_rebalancing_gross_pnl_delta=0., fee_pnl_delta=0.)
    symbols = sorted(set(baseline['symbols']) | set(risk['symbols']))
    for symbol in symbols:
        a = baseline['symbols'].get(symbol, {})
        b = risk['symbols'].get(symbol, {})
        gross = (float(b.get('pnl', 0)) + float(b.get('fees', 0))
                 - float(a.get('pnl', 0)) - float(a.get('fees', 0)))
        fee = float(a.get('fees', 0)) - float(b.get('fees', 0))
        key = ('avoided_two_gross_pnl_delta' if symbol in avoided else
               'retained_002621_gross_pnl_delta' if symbol == '002621.SZ' else
               'other_replacement_rebalancing_gross_pnl_delta')
        buckets[key] += gross
        buckets['fee_pnl_delta'] += fee
        deltas[symbol] = dict(gross_pnl_delta=gross, fee_pnl_delta=fee, net_pnl_delta=gross+fee)
    delta = float(risk['final_nav']) - float(baseline['final_nav'])
    residual = delta - sum(buckets.values())
    if not math.isfinite(residual) or abs(residual) > max(.05, abs(delta)*1e-10):
        raise ValueError(f'paired accounting identity failed: residual={residual}')
    return dict(schema='execution-paired-accounting.v1', initial_capital=capital,
                nav_profit_delta=delta, return_delta=delta/capital, buckets=buckets,
                return_delta_buckets={k: v/capital for k, v in buckets.items()},
                identity_residual=residual, symbols=deltas, avoided_symbols=sorted(avoided),
                selected_problem_three=['600321.SH', '000982.SZ', '002621.SZ'],
                limitations=['Selected problem symbols are an after-observation descriptive scope, not a fitted risk exclusion.',
                             'Other symbols combine replacement and rebalancing; this is accounting attribution, not a causal counterfactual.',
                             'Gross symbol P&L includes dividends, rights and terminal inventory but excludes transaction fees.',
                             'No own market impact is estimated.'])


def market_regime_summary(full_panel: pd.DataFrame, daily: pd.DataFrame) -> dict:
    """Label each session using only preceding full-market main-board observations.

    Frozen descriptive thresholds: prior five/20-session amount mean < 0.8;
    prior close down-limit share >= 2%. No history is filled from future data.
    """
    market = full_panel.copy()
    code = 'ts_code' if 'ts_code' in market else 'symbol'
    date = 'trade_date' if 'trade_date' in market else 'date'
    market['day'] = pd.to_datetime(market[date].astype(str)).dt.normalize()
    market = market.loc[market[code].str.match(r'^(00\d{4}\.SZ|60\d{4}\.SH)$')]
    if market.duplicated([code, 'day']).any():
        raise ValueError('duplicate full-market symbol/session observations')
    grouped = market.groupby('day', sort=True)
    amounts = grouped.amount.sum(min_count=1)
    five = amounts.rolling(5, min_periods=5).mean().shift(1)
    twenty = amounts.rolling(20, min_periods=20).mean().shift(1)
    ratio = five / twenty.where(twenty > 0)
    if 'down_limit' in market:
        eligible = market.close.notna() & market.down_limit.notna() & market.down_limit.gt(0)
        market['eligible'] = eligible.astype(int)
        market['at_down'] = (eligible & market.close.le(market.down_limit)).astype(int)
        eligible_count = market.groupby('day').eligible.sum()
        down_count = market.groupby('day').at_down.sum()
        shares = (down_count / eligible_count.where(eligible_count > 0)).shift(1)
        down_count = down_count.shift(1)
        eligible_count = eligible_count.shift(1)
    else:
        shares = pd.Series(float('nan'), index=amounts.index)
        down_count = shares.copy()
        eligible_count = shares.copy()
    if daily.empty:
        raise ValueError('account daily ledger must contain sessions')
    work = daily.copy()
    work['day'] = pd.to_datetime(work.date.astype(str)).dt.normalize()
    work = work.sort_values('day')
    if work.day.duplicated().any():
        raise ValueError('duplicate account sessions')
    # No fabricated initial NAV: first session return is unavailable.
    work['return'] = work.nav.pct_change(fill_method=None)
    work['cost_delta'] = work.transaction_cost.diff()
    work.loc[work.index[0], 'cost_delta'] = work.iloc[0].transaction_cost
    sessions, regimes = [], {}
    overlap = dict(low_liquidity=0, down_limit_stress=0, both=0)
    for row in work.itertuples():
        value = ratio.get(row.day, float('nan'))
        history = pd.notna(twenty.get(row.day))
        share = shares.get(row.day, float('nan'))
        low = bool(value < .8) if history and pd.notna(value) else None
        stress = bool(share >= .02) if history and pd.notna(share) else None
        label = ('insufficient_history' if not history else
                 'low_liquidity_and_down_limit_stress' if low and stress else
                 'low_liquidity' if low else 'down_limit_stress' if stress else
                 'market_data_unavailable' if stress is None or low is None else 'ordinary')
        sessions.append(dict(date=row.day.strftime('%Y-%m-%d'), history_status='sufficient' if history else 'insufficient_history',
                             amount_prior_5_over_20=float(value) if pd.notna(value) else None,
                             prior_down_limit_share=float(share) if history and pd.notna(share) else None,
                             prior_down_limit_count=int(down_count.get(row.day)) if history and pd.notna(down_count.get(row.day)) else None,
                             prior_eligible_count=int(eligible_count.get(row.day)) if history and pd.notna(eligible_count.get(row.day)) else None,
                             low_liquidity=low, down_limit_stress=stress, regime=label))
        target = regimes.setdefault(label, dict(sessions=0, return_observations=0,
                                                account_compounded_return=0., transaction_cost_delta=0.))
        if 'trapped_marked_value' in work:
            trapped = float(work.loc[row.Index, 'trapped_marked_value'])
            if math.isfinite(trapped):
                target['trapped_marked_value_sum'] = target.get('trapped_marked_value_sum', 0.) + trapped
                target['trapped_marked_value_observations'] = target.get('trapped_marked_value_observations', 0) + 1
                target['max_trapped_marked_value'] = max(target.get('max_trapped_marked_value', 0.), trapped)
        target['sessions'] += 1
        target['transaction_cost_delta'] += float(row.cost_delta)
        ret = float(work.loc[row.Index, 'return'])
        if math.isfinite(ret):
            target['return_observations'] += 1
            target['account_compounded_return'] = (1+target['account_compounded_return'])*(1+ret)-1
        overlap['low_liquidity'] += int(low is True)
        overlap['down_limit_stress'] += int(stress is True)
        overlap['both'] += int(low is True and stress is True)
    for target in regimes.values():
        if target.get('trapped_marked_value_observations'):
            target['mean_trapped_marked_value'] = target.pop('trapped_marked_value_sum') / target['trapped_marked_value_observations']
    return dict(schema='execution-market-regime.v1', sessions=sessions, regimes=regimes,
                overlap_counts=overlap, thresholds=dict(liquidity_ratio=.8, down_limit_share=.02, history_sessions=20, lag_sessions=1),
                limitations=['Regimes are descriptive labels, not trade signals or statistical causal evidence.',
                             'The first account session return is unavailable without a preceding NAV; its recorded cost is included.',
                             'No future data fill and no own market impact estimate.',
                             'Trapped exposure by regime requires session-level inventory and marks; account daily ledgers alone cannot identify it.',
                             'Down-limit shares count symbols with observed positive limits; unavailable limits are not inferred.'])
