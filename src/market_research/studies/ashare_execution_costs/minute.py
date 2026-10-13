"""Dated public small-cap targets and raw minute input preparation.

This is research orchestration, not a matching engine. Historical source
availability is reconstructed and must not be described as revision-safe PIT.
"""
from __future__ import annotations

import hashlib
import math

import pandas as pd

from market_research.microcap_execution import historical_name_mask

ZONE = 'Asia/Shanghai'


def build_targets(panel: pd.DataFrame, *, count: int, rebalance_sessions: int = 1,
                  buffer_multiple: int = 1, namechange: pd.DataFrame | None = None) -> pd.DataFrame:
    """Complete snapshots, prior close selection, next-session 09:31 entry.

    Main-board Shanghai/Shenzhen names only: the fixed 100-share buy lot is
    unsuitable for other board rules. Buffers retain previous target names only
    while eligible and within count*buffer_multiple in the current ranking.
    """
    if any(type(v) is not int or v < 1 for v in (count, rebalance_sessions, buffer_multiple)):
        raise ValueError('selection settings must be positive integers')
    required = {'ts_code', 'trade_date', 'total_mv', 'close', 'amount', 'is_st',
                'is_suspended', 'list_date', 'delist_date'}
    if required - set(panel):
        raise ValueError('missing selection columns')
    source = panel.copy()
    source['trade_date'] = source.trade_date.astype(str)
    if source.duplicated(['trade_date', 'ts_code']).any():
        raise ValueError('duplicate selection keys')
    days = sorted(source.trade_date.unique())
    names = historical_name_mask(namechange, source) if namechange is not None else True
    age = (pd.to_datetime(source.trade_date) - pd.to_datetime(source.list_date, errors='coerce')).dt.days
    eligible = (
        source.ts_code.str.match(r'^(00\d{4}\.SZ|60\d{4}\.SH)$')
        & source.is_st.eq(False).fillna(False) & source.is_suspended.eq(False).fillna(False)
        & age.ge(120) & (source.delist_date.isna() | source.delist_date.astype(str).gt(source.trade_date))
        & source.total_mv.gt(0) & source.close.gt(0) & source.amount.gt(0) & names
    )
    candidates = source.loc[eligible].sort_values(['trade_date', 'total_mv', 'ts_code'])
    previous: list[str] = []
    result = []
    for i in range(0, len(days) - 1, rebalance_sessions):
        day = days[i]
        ranked = candidates.loc[candidates.trade_date.eq(day), 'ts_code'].tolist()
        if len(ranked) < count:
            raise ValueError(f'{day} has insufficient eligible names')
        pool = set(ranked[:count * buffer_multiple])
        retained = [s for s in previous if s in pool]
        selected = retained + [s for s in ranked if s not in retained][:count - len(retained)]
        previous = selected
        decision = pd.Timestamp(day, tz=ZONE) + pd.Timedelta(hours=20, minutes=2)
        entry = pd.Timestamp(days[i + 1], tz=ZONE) + pd.Timedelta(hours=9, minutes=31)
        result.extend(dict(decision_time=decision, entry_time=entry, symbol=s, weight=1/count)
                      for s in selected)
    return pd.DataFrame(result, columns=['decision_time', 'entry_time', 'symbol', 'weight'])


def prepare_minute_bars(raw: pd.DataFrame, daily: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Normalize already published minute units; do not infer missing liquidity.

    Availability is conservatively one minute after the source label because
    provider timestamps do not establish actual historical receive times.
    09:30 and 15:00 source bars provide marks only, excluding auctions from fills.
    """
    if raw.duplicated(['ts_code', 'trade_time']).any():
        raise ValueError('duplicate minute bars')
    if daily.duplicated(['ts_code', 'trade_date']).any():
        raise ValueError('duplicate daily marks')
    work = raw.copy()
    stamp = pd.to_datetime(work.trade_time)
    if stamp.dt.tz is not None:
        raise ValueError('source time must use the native naive wallclock contract')
    work['trade_date'] = stamp.dt.strftime('%Y%m%d')
    work['time'] = stamp.dt.tz_localize(ZONE) + pd.Timedelta(minutes=1)
    # Keep the earliest possible interval start separately. A delayed receive
    # label cannot make trades before activation executable.
    work['interval_start'] = stamp.dt.tz_localize(ZONE) - pd.Timedelta(minutes=1)
    marks = daily[['ts_code', 'trade_date', 'up_limit', 'down_limit', 'is_suspended']].copy()
    marks['trade_date'] = marks.trade_date.astype(str)
    work = work.merge(marks, on=['ts_code', 'trade_date'], how='left', validate='many_to_one')
    if work[['up_limit', 'down_limit', 'is_suspended']].isna().any().any():
        raise ValueError('unknown minute trading constraints')
    price_cols = ['open', 'high', 'low', 'close', 'up_limit', 'down_limit']
    if work[price_cols].le(0).any().any() or work[['vol', 'amount']].lt(0).any().any():
        raise ValueError('invalid minute prices or liquidity')
    if (work.vol.eq(0) & work.amount.gt(0)).any():
        raise ValueError('zero volume with positive amount')
    vwap = work.amount / work.vol.where(work.vol.gt(0))
    outside = work.vol.gt(0) & (vwap.lt(work.low - .01) | vwap.gt(work.high + .01))
    # Native receipts permit rounded volume/amount differences. Keep this
    # diagnostic visible and let the generic engine bound the proxy to OHLC.
    auction = stamp.dt.strftime('%H:%M').isin(['09:30', '15:00']).to_numpy()
    work['tradable'] = (~work.is_suspended.astype(bool) & ~auction & work.vol.gt(0)).astype(bool)
    bars = work.rename(columns={'ts_code': 'symbol', 'vol': 'volume'})[
        ['symbol', 'time', 'interval_start', 'open', 'high', 'low', 'close', 'volume', 'amount',
         'up_limit', 'down_limit', 'tradable']
    ]
    return bars.sort_values(['time', 'symbol']).reset_index(drop=True), {
        'rows': len(bars), 'symbols': bars.symbol.nunique(),
        'availability_policy': 'source_wallclock_plus_one_minute',
        'volume_unit': 'share', 'amount_unit': 'CNY',
        'auction_bars_mark_only': int(auction.sum()),
        'vwap_outside_ohlc_one_cent': int(outside.sum()),
        'actual_receive_times_verified': False,
        'execution_interval_policy': 'entire_source_label_minus_one_minute_interval_after_activation',
    }


def normalize_dividends(raw: pd.DataFrame, symbols: set[str], *, start: str, end: str) -> tuple[list[dict], dict]:
    """Select implemented rights, exact-deduplicate, block conflicting versions.

    Cash uses cash_div_tax (gross CNY per share); tax withholding is an explicit
    zero-rate research assumption, not a broker-specific settlement estimate.
    """
    selected = raw.loc[raw.ts_code.isin(symbols) & raw.div_proc.str.strip().eq('实施')].copy()
    # A missing ex date cannot be used to exclude a potentially in-window event.
    unknown = selected.ex_date.isna() & selected.imp_ann_date.astype(str).between(start, end)
    if unknown.any():
        raise ValueError('implemented dividend has unknown ex_date')
    selected = selected.loc[selected.ex_date.astype(str).between(start, end)].copy()
    selected = selected.drop(columns=['event_key_conflict'], errors='ignore')
    before = len(selected)
    selected = selected.drop_duplicates()
    fields = ['ts_code', 'record_date', 'ex_date', 'pay_date', 'div_listdate',
              'imp_ann_date', 'cash_div_tax', 'stk_div']
    zero = selected.cash_div_tax.eq(0) & selected.stk_div.eq(0)
    unique = selected.loc[~zero, fields].drop_duplicates()
    if unique.duplicated(['ts_code', 'ex_date']).any():
        raise ValueError('conflicting implemented dividend versions')
    result = []
    for row in unique.to_dict('records'):
        for name in ('record_date', 'ex_date', 'imp_ann_date'):
            if pd.isna(row[name]):
                raise ValueError(f'implemented dividend missing {name}')
        cash, stock = row['cash_div_tax'], row['stk_div']
        if not all(pd.notna(v) and math.isfinite(float(v)) and v >= 0 for v in (cash, stock)):
            raise ValueError('unknown dividend cash or stock entitlement')
        if cash == 0 and stock == 0:
            continue  # Explicit zero original-holder distribution, not missing cash.
        if row['imp_ann_date'] > row['record_date'] or row['imp_ann_date'] > row['ex_date']:
            raise ValueError('dividend availability is later than entitlement')
        if cash > 0 and pd.isna(row['pay_date']):
            raise ValueError('cash dividend missing pay_date')
        if stock > 0 and pd.isna(row['div_listdate']):
            raise ValueError('stock dividend missing div_listdate')
        # Cash-only start owns no historical record-date entitlements.
        if row['record_date'] < start:
            continue
        event_id = hashlib.sha256(f"{row['ts_code']}:{row['ex_date']}".encode()).hexdigest()[:20]
        result.append(dict(event_id=event_id, symbol=row['ts_code'],
                           available_date=row['imp_ann_date'], record_date=row['record_date'],
                           ex_date=row['ex_date'], cash_pay_date=row['pay_date'] if cash > 0 else None,
                           stock_tradable_date=row['div_listdate'] if stock > 0 else None,
                           cash_per_share=float(cash), stock_per_share=float(stock),
                           withholding_rate=0.0))
    return result, {'events': len(result), 'exact_duplicates_removed': before - len(selected),
                    'withholding_rate_assumption': 0.0, 'cash_basis': 'cash_div_tax_gross_CNY_per_share',
                    'pit_class': 'reconstructed_pit', 'revision_safe': False}


def assert_unowned_events(holdings: pd.DataFrame, days: list[str], blocked: list[dict]) -> int:
    """Unmodeled events may be irrelevant only with verified zero ownership.

    Eligibility and target weights do not prove that old inventory was sold.
    Missing record-day coverage prevents this exemption.
    """
    calendar = set(days)
    positions = holdings.copy()
    positions['day'] = pd.to_datetime(positions.date).dt.strftime('%Y%m%d')
    for event in blocked:
        records = event['record_dates']
        if not records or any(day not in calendar for day in records):
            raise ValueError('unverified corporate event lacks record-day coverage')
        owned = positions.loc[positions.symbol.eq(event['symbol']) & positions.day.isin(records)]
        if owned.quantity.gt(1e-8).any():
            raise ValueError('unverified corporate event was held: cannot publish complete NAV')
    return len(blocked)


def apply_dividend_overrides(raw: pd.DataFrame, overrides: list[dict]) -> pd.DataFrame:
    """Apply separately retained primary-source decisions without changing raw."""
    result = raw.copy()
    for row in overrides:
        if not row.get('source_url') or len(row.get('source_pdf_sha256', '')) != 64:
            raise ValueError('override requires primary source evidence')
        if row['kind'] not in ('ordinary_distribution', 'no_original_holder_distribution'):
            raise ValueError('unknown override kind')
        match = (result.ts_code.eq(row['symbol']) & result.ex_date.eq(row['ex_date'])
                 & result.div_proc.str.strip().eq('实施'))
        if not match.any():
            continue
        for field, value in [('cash_div_tax', row['cash_per_share']), ('stk_div', row['stock_per_share'])]:
            if not math.isfinite(value) or value < 0:
                raise ValueError('invalid override entitlement')
            result.loc[match, field] = value
        if row.get('stock_listing_date'):
            result.loc[match, 'div_listdate'] = row['stock_listing_date']
    return result


def audit_adjustment_events(marks: pd.DataFrame, explained: set[tuple[str, str]]) -> dict:
    """Block factor changes absent any known modeled or explicitly blocked event.

    A factor match is a missing-event screen, not independent proof of event
    amounts or full rights-issue coverage.
    """
    work = marks.sort_values(['ts_code', 'trade_date']).copy()
    previous = work.groupby('ts_code').adj_factor.shift()
    changed = previous.notna() & (work.adj_factor / previous - 1).abs().gt(1e-9)
    keys = set(zip(work.loc[changed, 'ts_code'], work.loc[changed, 'trade_date'], strict=True))
    if keys - explained:
        raise ValueError(f'unexplained adjustment events: {len(keys - explained)}')
    return {'explained_changes': len(keys), 'unexplained_changes': 0,
            'scope': 'factor_change_screen_not_complete_event_source'}


def measure_arrival_shortfall(orders: pd.DataFrame, fills: pd.DataFrame,
                             bars: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Arrival-reference shortfall including explicitly retained missed quantity.

    The reference is the engine's known raw or synthetic ex reference, not a
    midpoint or real broker arrival price. End marks must be available by the
    same fixed deadline and no more than one minute old. Signed results include
    price movement; they are not causal own-order impact.
    """
    work = orders.copy()
    work['deadline'] = pd.to_datetime(work.deadline).dt.as_unit('ns')
    work['unfilled_quantity'] = work.quantity - work.filled_quantity
    work['reference_notional'] = work.quantity * work.reference_price
    quotes = bars[['symbol', 'time', 'close']].rename(columns={'time': 'quote_time', 'close': 'end_price'})
    quotes['quote_time'] = pd.to_datetime(quotes.quote_time).dt.as_unit('ns')
    if len(quotes):
        work = pd.merge_asof(work.sort_values('deadline'), quotes.sort_values('quote_time'),
                             left_on='deadline', right_on='quote_time', by='symbol',
                             direction='backward', tolerance=pd.Timedelta(minutes=1))
    else:
        work['end_price'] = float('nan')
        work['quote_time'] = pd.NaT
    totals = fills.groupby('order_id')[['gross_amount', 'quantity', 'transaction_cost']].sum()
    for source, destination in [('gross_amount', 'filled_gross'), ('transaction_cost', 'fees')]:
        work[destination] = work.order_id.map(totals[source]).fillna(0.)
    sign = work.side.map({'buy': 1., 'sell': -1.})
    work['executed_price_cost_cny'] = sign * (work.filled_gross - work.filled_quantity * work.reference_price)
    work['unfilled_opportunity_cny'] = sign * work.unfilled_quantity * (work.end_price - work.reference_price)
    work.loc[work.unfilled_quantity.eq(0), 'unfilled_opportunity_cny'] = 0.
    work['arrival_shortfall_cny'] = work.executed_price_cost_cny + work.unfilled_opportunity_cny + work.fees
    work['arrival_shortfall_bp'] = work.arrival_shortfall_cny / work.reference_notional.where(work.reference_notional.gt(0)) * 10000
    available = work.arrival_shortfall_bp.notna()
    ref_total = work.reference_notional.sum()
    completed = (work.filled_quantity * work.reference_price).sum()
    cost = work.loc[available, 'arrival_shortfall_bp']
    summary = {'cost_available_orders': int(available.sum()), 'cost_unavailable_orders': int((~available).sum()),
               'target_notional_completion': float(completed / ref_total) if ref_total > 0 else None,
               'arrival_shortfall_p50_bp': float(cost.median()) if len(cost) else None,
               'arrival_shortfall_p90_bp': float(cost.quantile(.9)) if len(cost) else None,
               'arrival_shortfall_p95_bp': float(cost.quantile(.95)) if len(cost) else None,
               'unfilled_opportunity_cny': (float(work.unfilled_opportunity_cny.sum())
                                             if work.unfilled_opportunity_cny.notna().all() else None),
               'benchmark': 'known_raw_or_synthetic_ex_arrival_reference',
               'causal_impact_identified': False}
    return work.sort_values('order_id').reset_index(drop=True), summary


def add_suspension_marks(bars: pd.DataFrame, suspensions: pd.DataFrame, days: list[str],
                         actions: list[dict]) -> tuple[pd.DataFrame, dict]:
    """Explicit nontradable valuation carry for confirmed full-day suspensions.

    No observed bars on the entire date plus S with no intraday timing is
    required. Unknown/intraday gaps stay missing. The carried reference is never
    a quote or a fill; ordinary known distributions adjust its price basis.
    """
    observed = bars.copy()
    observed['mark_basis'] = 'observed_bar'
    observed['reference_source_time'] = observed.time
    groups = {symbol: frame.sort_values('time') for symbol, frame in observed.groupby('symbol')}
    present = set(zip(observed.symbol, observed.time.dt.strftime('%Y%m%d'), strict=True))
    full = suspensions.loc[suspensions.suspend_type.eq('S') &
                            (suspensions.suspend_timing.isna() | suspensions.suspend_timing.eq(''))]
    full = full.loc[full.trade_date.astype(str).isin(days) & full.ts_code.isin(groups)]
    extra = []
    missing_history = 0
    for row in full.drop_duplicates(['ts_code', 'trade_date']).itertuples():
        day = str(row.trade_date)
        if (row.ts_code, day) in present:
            continue
        midnight = pd.Timestamp(day, tz=ZONE)
        history = groups[row.ts_code]
        index = history.time.searchsorted(midnight) - 1
        if index < 0:
            missing_history += 1
            continue
        prior = history.iloc[index].to_dict()
        price = prior['close']
        prior_day = prior['time'].strftime('%Y%m%d')
        for event in sorted(actions, key=lambda e: e['ex_date']):
            if event['symbol'] == row.ts_code and prior_day < event['ex_date'] <= day:
                price = (price - event['cash_per_share']) / (1 + event['stock_per_share'])
        if not math.isfinite(price) or price <= 0:
            raise ValueError('invalid corporate-adjusted suspension reference')
        prior.update(time=midnight + pd.Timedelta(hours=15, minutes=1),
                     interval_start=midnight + pd.Timedelta(hours=14, minutes=59),
                     open=price, high=price, low=price, close=price, volume=0., amount=0.,
                     tradable=False, mark_basis='confirmed_suspension_carry',
                     reference_source_time=history.iloc[index].time)
        extra.append(prior)
    result = pd.concat([observed, pd.DataFrame(extra)], ignore_index=True)
    return result.sort_values(['time', 'symbol']).reset_index(drop=True), {
        'carried_symbol_days': len(extra), 'missing_prior_history': missing_history,
        'max_calendar_staleness_days': max(((row['time'].date() - row['reference_source_time'].date()).days
                                            for row in extra), default=0),
        'policy': 'known_full_day_S_and_no_bars_last_raw_reference_valuation_only',
    }
