"""Descriptive index statistics and predeclared hypothetical allocations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_research.studies.asset_returns.analysis import diversification


def _valid(values: pd.Series) -> None:
    if (
        len(values) < 2
        or not isinstance(values.index, pd.DatetimeIndex)
        or values.index.hasnans
        or values.index.duplicated().any()
        or not values.index.is_monotonic_increasing
        or not np.isfinite(values).all()
        or (values <= 0).any()
    ):
        raise ValueError("require ordered unique dates and finite positive levels")


def summarize(values: pd.Series) -> dict:
    _valid(values)
    years = (values.index[-1] - values.index[0]).days / 365.25
    returns = values.pct_change(fill_method=None).iloc[1:]
    peak, peak_date, underwater = float(values.iloc[0]), values.index[0], False
    episodes = []
    for date, value in values.iloc[1:].items():
        if value >= peak:
            if underwater:
                episodes.append(
                    {
                        "peak_date": peak_date.date().isoformat(),
                        "end_date": date.date().isoformat(),
                        "recovered": True,
                        "calendar_days": (date - peak_date).days,
                    }
                )
            peak, peak_date, underwater = float(value), date, False
        else:
            underwater = True
    if underwater:
        episodes.append(
            {
                "peak_date": peak_date.date().isoformat(),
                "end_date": values.index[-1].date().isoformat(),
                "recovered": False,
                "calendar_days": (values.index[-1] - peak_date).days,
            }
        )
    return {
        "start": values.index[0].date().isoformat(),
        "end": values.index[-1].date().isoformat(),
        "observations": len(values),
        "total_return": float(values.iloc[-1] / values.iloc[0] - 1),
        "cagr": float((values.iloc[-1] / values.iloc[0]) ** (1 / years) - 1),
        "daily_volatility_252": float(returns.std(ddof=1) * np.sqrt(252))
        if len(returns) > 1
        else None,
        "max_drawdown": float((values / values.cummax() - 1).min()),
        "drawdown_episodes": episodes,
    }


def monthly_levels(
    values: pd.Series, calendar: pd.DatetimeIndex, cutoff: pd.Timestamp
) -> pd.Series:
    _valid(values)
    # Calendar must extend to the final session of each candidate month. A month
    # with no verified final-session calendar is not declared complete by this helper.
    endpoints = pd.Series(calendar, index=calendar.to_period("M")).groupby(level=0).max()
    endpoints = endpoints[(endpoints >= values.index[0]) & (endpoints <= cutoff)]
    # Even if a short calendar ends at cutoff, a partial terminal month is excluded.
    if cutoff < cutoff + pd.offsets.MonthEnd(0):
        endpoints = endpoints[endpoints.index < cutoff.to_period("M")]
    selected = values.reindex(pd.DatetimeIndex(endpoints.to_numpy()))
    if selected.isna().any():
        raise ValueError("missing exact monthly endpoint")
    return pd.Series(selected.to_numpy(), index=endpoints.index.to_timestamp("M"), name=values.name)


def portfolio_path(
    levels: pd.DataFrame,
    weight: float,
    rebalance: str,
    month_ends: set[pd.Timestamp],
    drag_bps: float = 0,
) -> pd.Series:
    for col in ["equity", "commodity"]:
        _valid(levels[col])
    if not 0 <= weight <= 1 or rebalance not in {"monthly", "annual"} or not 0 <= drag_bps < 10000:
        raise ValueError("invalid fixed portfolio rule")
    holdings = np.array([1 - weight, weight], dtype=float)
    marks = [1.0]
    returns = levels.pct_change(fill_method=None).iloc[1:]
    for date, row in zip(returns.index, returns[["equity", "commodity"]].to_numpy()):
        holdings *= 1 + row
        wealth = float(holdings.sum())
        marks.append(wealth)
        if date in month_ends and (rebalance == "monthly" or date.month == 12):
            holdings = wealth * np.array([1 - weight, weight])
    elapsed = (levels.index - levels.index[0]).days.to_numpy() / 365.25
    return pd.Series(np.array(marks) * (1 - drag_bps / 10000) ** elapsed, index=levels.index)


def holding_summary(values: pd.Series) -> list[dict]:
    _valid(values)
    months = values.index.to_period("M").astype("int64")
    if not values.index.is_month_end.all() or not (np.diff(months) == 1).all():
        raise ValueError("consecutive calendar month-end marks required")
    levels = values.to_numpy()
    rows = []
    for horizon in [12, 36, 60, 120]:
        growth = levels[horizon:] / levels[:-horizon] if len(levels) > horizon else np.array([])
        annualized = growth ** (12 / horizon) - 1
        rows.append(
            {
                "months": horizon,
                "completed_windows": len(growth),
                "incomplete_windows": min(horizon, len(values)),
                "nominal_loss_fraction": float((growth < 1).mean()) if len(growth) else None,
                "worst_annualized_return": float(annualized.min()) if len(growth) else None,
                "median_annualized_return": float(np.median(annualized)) if len(growth) else None,
            }
        )
    return rows


def period_returns(values: pd.Series) -> dict:
    """Synchronized endpoints; unavailable anchors remain explicit."""
    _valid(values)
    end = values.index[-1]

    def interval(start, finish):
        if (
            start is None
            or finish is None
            or start not in values.index
            or finish not in values.index
            or start >= finish
        ):
            return None
        return {
            "start": start.date().isoformat(),
            "end": finish.date().isoformat(),
            "return": float(values.loc[finish] / values.loc[start] - 1),
        }

    previous_friday = end - pd.Timedelta(days=(end.weekday() - 4) % 7)
    # If the latest observation is before Friday, use the last completed week.
    week = values.index[values.index <= previous_friday]
    week_end = week[-1] if len(week) else None
    week_start_days = values.index[values.index <= previous_friday - pd.Timedelta(days=7)]
    week_start = week_start_days[-1] if len(week_start_days) else None
    completed = values.loc[values.index.to_period("M") < end.to_period("M")]
    monthly = completed.groupby(completed.index.to_period("M")).tail(1)
    last_month = None
    if (
        len(monthly) >= 2
        and monthly.index[-1].to_period("M").ordinal - monthly.index[-2].to_period("M").ordinal == 1
    ):
        last_month = interval(monthly.index[-2], monthly.index[-1])
    year_days = values.index[values.index.year == end.year - 1]
    year_start = year_days[-1] if len(year_days) and year_days[-1].month == 12 else None
    target = end - pd.DateOffset(years=1)
    trailing_days = values.index[values.index <= target]
    # A prior common session may precede an anniversary by a market closure;
    # report the actual date and reject absent history rather than inventing it.
    trailing_start = trailing_days[-1] if len(trailing_days) else None
    return {
        "last_week": interval(week_start, week_end),
        "last_month": last_month,
        "year_to_date": interval(year_start, end),
        "trailing_12_months": interval(trailing_start, end),
    }


def describe_pair(levels: pd.DataFrame, calendar: pd.DatetimeIndex, cutoff: pd.Timestamp) -> dict:
    monthly = pd.DataFrame({c: monthly_levels(levels[c], calendar, cutoff) for c in levels})
    result = {
        "daily": {c: summarize(levels[c]) for c in levels},
        "recent_periods": {c: period_returns(levels[c]) for c in levels},
        "monthly_observations": len(monthly),
        "allocation": [],
    }
    if len(monthly) < 2:
        result["monthly_unavailable"] = "fewer than two verified completed month-end marks"
        return result
    data = monthly.rename_axis("date").reset_index()
    result["holding_periods"] = {c: holding_summary(monthly[c]) for c in levels}
    result["diversification"] = diversification(data, ["equity", "commodity"], "equity")
    result["monthly_max_drawdown"] = {
        c: float((monthly[c] / monthly[c].cummax() - 1).min()) for c in levels
    }
    # Restrict allocation to exact complete month-end anchor, then retain daily marks
    # to measure portfolio intramonth drawdown and drift.
    first_month = monthly.index[0].to_period("M")
    ends = pd.Series(calendar, index=calendar.to_period("M")).groupby(level=0).max()
    anchor = ends.loc[first_month]
    allocation_levels = levels.loc[anchor : ends.loc[monthly.index[-1].to_period("M")]]
    for policy in ["monthly", "annual"]:
        for weight in [0, 0.1, 0.2, 0.3, 0.4]:
            for drag in [0, 50, 100]:
                nav = portfolio_path(allocation_levels, weight, policy, set(ends), drag)
                nav_monthly = monthly_levels(nav, calendar, nav.index[-1] + pd.offsets.MonthEnd(0))
                holdings = holding_summary(nav_monthly)
                result["allocation"].append(
                    {
                        "commodity_weight": weight,
                        "rebalance": policy,
                        "annual_wealth_drag_bps": drag,
                        "calibrated_cost": False,
                        **summarize(nav),
                        "holding_periods": holdings,
                    }
                )
    annual = monthly.loc[monthly.index.month == 12]
    result["calendar_year_returns"] = [
        {
            "year": int(annual.index[i].year),
            **{c: float(annual[c].iloc[i] / annual[c].iloc[i - 1] - 1) for c in levels},
        }
        for i in range(1, len(annual))
        if annual.index[i].year == annual.index[i - 1].year + 1
    ]
    return result
