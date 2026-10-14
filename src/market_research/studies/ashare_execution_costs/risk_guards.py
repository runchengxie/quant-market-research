"""Causal research guards layered on the preserved target selector.

Snapshots request exits; the execution provider determines whether they fill.
"""
from __future__ import annotations

import math

import pandas as pd

from market_research.microcap_execution import historical_name_mask

from .minute import ZONE, build_targets


def _validated_events(events: pd.DataFrame | None) -> pd.DataFrame:
    fields = ['symbol', 'available_time', 'event_id', 'event_type']
    if events is None:
        return pd.DataFrame(columns=fields)
    if set(fields) - set(events):
        raise ValueError('missing risk event columns')
    result = events[fields].copy()
    for field in fields:
        if result[field].map(lambda x: not isinstance(x, str) or not x.strip()).any():
            raise ValueError(f'invalid risk event {field}')
    if result.event_id.duplicated().any():
        raise ValueError('duplicate risk event identity')
    if not result.event_type.eq('confirmed_termination').all():
        raise ValueError('unsupported risk event type')
    stamps = []
    for value in result.available_time:
        try:
            stamp = pd.Timestamp(value)
        except (ValueError, TypeError) as exc:
            raise ValueError('invalid risk event available_time') from exc
        if pd.isna(stamp) or stamp.tzinfo is None:
            raise ValueError('risk event available_time must be timezone aware')
        stamps.append(stamp.tz_convert(ZONE))
    result['available_time'] = stamps
    return result


def build_risk_targets(
    panel: pd.DataFrame, *, count: int, minimum_close: float = 1.0,
    rebalance_sessions: int = 1, buffer_multiple: int = 1,
    namechange: pd.DataFrame | None = None, risk_events: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Select full snapshots with prior-session close and known risk exclusions.

    ``st_available_from`` follows the daily-clean YYYYMMDD contract: false ST
    with no date means known non-ST; false with a date is contradictory. True
    with a future/missing date and null ST are unknown, hence ineligible.
    ``minimum_close`` is an experimental CNY threshold, not statutory face value.
    """
    if isinstance(minimum_close, bool):
        raise ValueError('minimum_close must be positive and finite')
    try:
        threshold = float(minimum_close)
    except (ValueError, TypeError) as exc:
        raise ValueError('minimum_close must be positive and finite') from exc
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError('minimum_close must be positive and finite')
    if 'st_available_from' not in panel:
        raise ValueError('missing st_available_from selection column')
    events = _validated_events(risk_events)
    settings = dict(count=count, rebalance_sessions=rebalance_sessions,
                    buffer_multiple=buffer_multiple, namechange=namechange)
    # Original selection validates the shared schema and settings. Baseline
    # comparison is optional when its candidates cannot supply the requested count.
    try:
        baseline = build_targets(panel, **settings)
    except ValueError as exc:
        if 'insufficient eligible names' not in str(exc):
            raise
        baseline = None
    source = panel.copy().reset_index(drop=True)
    source['trade_date'] = source.trade_date.astype(str)
    available = pd.to_datetime(source.st_available_from, format='%Y%m%d', errors='coerce')
    dates = pd.to_datetime(source.trade_date, format='%Y%m%d', errors='raise')
    st = source.is_st.astype('boolean')
    unknown = (st.isna() | (st.eq(True) & (available.isna() | available.gt(dates)))
               | (st.eq(False) & source.st_available_from.notna())).fillna(True)
    reasons = {
        'below_minimum_close': source.close.lt(threshold),
        'st_unknown_or_contradictory': unknown,
        'known_st': (st.eq(True) & ~unknown).fillna(False),
        'confirmed_termination': pd.Series(False, index=source.index),
    }
    decisions = dates.dt.tz_localize(ZONE) + pd.Timedelta(hours=20, minutes=2)
    for row in events.to_dict('records'):
        reasons['confirmed_termination'] |= (
            source.ts_code.eq(row['symbol']) & decisions.ge(row['available_time'])
        )
    blocked = pd.Series(False, index=source.index)
    for mask in reasons.values():
        blocked |= mask.fillna(False)
    # Audit candidates meet the original non-ST restrictions. Reason counts
    # overlap intentionally; the detailed symbol lists make that visible.
    names = historical_name_mask(namechange, source) if namechange is not None else True
    age = (dates - pd.to_datetime(source.list_date, errors='coerce')).dt.days
    candidates = (source.ts_code.str.match(r'^(00\d{4}\.SZ|60\d{4}\.SH)$')
                  & source.is_suspended.eq(False).fillna(False) & age.ge(120)
                  & (source.delist_date.isna()
                     | source.delist_date.astype(str).gt(source.trade_date))
                  & source.total_mv.gt(0) & source.close.gt(0)
                  & source.amount.gt(0) & names)
    source.loc[blocked, 'amount'] = 0
    targets = build_targets(source, **settings)
    audit_dates = []
    for stamp, group in targets.groupby('decision_time', sort=True):
        day_mask = source.trade_date.eq(stamp.strftime('%Y%m%d'))
        indices = source.index[day_mask & candidates]
        excluded = {reason: source.loc[indices.intersection(mask.index[mask.fillna(False)]),
                                      'ts_code'].tolist() for reason, mask in reasons.items()}
        selected = group.symbol.tolist()
        original = (baseline.loc[baseline.decision_time.eq(stamp), 'symbol'].tolist()
                    if baseline is not None else None)
        audit_dates.append(dict(
            decision_time=stamp.isoformat(),
            excluded_by_reason={key: len(value) for key, value in excluded.items()},
            excluded_candidates=excluded,
            selected_symbols=selected,
            selected_changes=dict(added=[s for s in selected if original is not None and s not in original],
                                  removed=[s for s in original or [] if s not in selected],
                                  baseline_available=original is not None),
        ))
    return targets, dict(
        parameters=dict(count=count, minimum_close=threshold,
                        rebalance_sessions=rebalance_sessions, buffer_multiple=buffer_multiple),
        source_assumptions=dict(
            threshold='experimental_prior_close_CNY_not_statutory_face_value',
            st='daily_clean_st_available_from_YYYYMMDD_unknown_or_contradictory_excluded',
            risk_events='confirmed_termination_available_time_at_or_before_decision_permanent',
            decision='prior_session_20:02_Asia/Shanghai',
            execution='complete_target_snapshot_requests_exit_provider_controls_fill',
            pit_class='reconstructed_pit', revision_safe=False,
        ), dates=audit_dates,
    )
