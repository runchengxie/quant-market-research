"""Entry-reset index accounts and finite rolling allocation comparisons."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .analysis import _valid


def index_account(
    levels: pd.DataFrame,
    weight: float,
    policy: str,
    month_ends: set[pd.Timestamp],
    cost_bps: float = 0,
) -> dict:
    """Idealized fractional index sleeves; no initial/final trade or contract fills.

    Each segment compounds actual asset growth from its own opening marks.
    A scheduled rebalance pays a funded two-sided notional fee after returns.
    """
    for col in ["equity", "commodity"]:
        _valid(levels[col])
    if (
        not np.isfinite([weight, cost_bps]).all()
        or not 0 <= weight <= 1
        or not 0 <= cost_bps < 10000
    ):
        raise ValueError("invalid weight or cost")
    if policy not in {"monthly", "annual", "buy_hold"}:
        raise ValueError("unsupported rebalance policy")
    targets = np.array([1 - weight, weight])
    values = levels[["equity", "commodity"]].to_numpy(dtype=float)
    ends = [
        i
        for i, d in enumerate(levels.index)
        if 0 < i < len(levels) - 1
        and d in month_ends
        and (policy == "monthly" or policy == "annual" and d.month == 12)
    ]
    if policy == "buy_hold":
        ends = []
    ends.append(len(levels) - 1)
    nav = np.ones(len(levels))
    opening, wealth, total_cost, turnover, count = 0, 1.0, 0.0, 0.0, 0
    for closing in ends:
        relative = values[opening + 1 : closing + 1] / values[opening]
        segment = wealth * (relative @ targets)
        nav[opening + 1 : closing + 1] = segment
        holdings = wealth * targets * (values[closing] / values[opening])
        before = float(holdings.sum())
        if closing != len(levels) - 1:
            low, high = 0.0, before
            if cost_bps:
                for _ in range(60):
                    fee = (low + high) / 2
                    required = cost_bps / 10000 * np.abs(targets * (before - fee) - holdings).sum()
                    if fee > required:
                        high = fee
                    else:
                        low = fee
                fee = (low + high) / 2
            else:
                fee = 0.0
            traded = float(np.abs(targets * (before - fee) - holdings).sum())
            total_cost += fee
            turnover += traded / before
            count += int(traded > 1e-12)
            wealth = before - fee
            nav[closing] = wealth
        else:
            wealth = before
        opening = closing
    return {
        "nav": pd.Series(nav, index=levels.index),
        "cost_paid": total_cost,
        "two_sided_turnover": turnover,
        "rebalance_count": count,
    }


def annual_drag_budget(portfolio_wealth: float, equity_wealth: float, years: float) -> float:
    if (
        not np.isfinite([portfolio_wealth, equity_wealth, years]).all()
        or min(portfolio_wealth, equity_wealth, years) <= 0
    ):
        raise ValueError("positive wealth and years required")
    return max(0.0, float(1 - (equity_wealth / portfolio_wealth) ** (1 / years))) * 10000


def rolling_comparison(
    levels: pd.DataFrame,
    endpoints: pd.DatetimeIndex,
    weight: float,
    policy: str,
    horizon_months: int = 60,
) -> list[dict]:
    periods = endpoints.to_period("M").astype("int64")
    if (
        len(endpoints) < 2
        or not endpoints.is_monotonic_increasing
        or endpoints.has_duplicates
        or not (np.diff(periods) == 1).all()
        or not endpoints.isin(levels.index).all()
    ):
        raise ValueError("consecutive verified month endpoints required")
    if type(horizon_months) is not int or horizon_months < 1:
        raise ValueError("positive integer horizon required")
    rows = []
    for i in range(max(0, len(endpoints) - horizon_months)):
        start, end = endpoints[i], endpoints[i + horizon_months]
        window = levels.loc[start:end]
        nav = index_account(window, weight, policy, set(endpoints))["nav"]
        equity = window.equity / window.equity.iloc[0]
        port_growth, eq_growth = float(nav.iloc[-1]), float(equity.iloc[-1])
        port_dd = float((nav / nav.cummax() - 1).min())
        eq_dd = float((equity / equity.cummax() - 1).min())
        improves_return = port_growth > eq_growth + 1e-12
        improves_dd = port_dd > eq_dd + 1e-12
        rows.append(
            {
                "start": str(start.date()),
                "end": str(end.date()),
                "months": horizon_months,
                "portfolio_total_return": port_growth - 1,
                "equity_total_return": eq_growth - 1,
                "portfolio_cagr": port_growth ** (12 / horizon_months) - 1,
                "equity_cagr": eq_growth ** (12 / horizon_months) - 1,
                "portfolio_max_drawdown": port_dd,
                "equity_max_drawdown": eq_dd,
                "improves_return": bool(improves_return),
                "improves_drawdown": bool(improves_dd),
                "improves_both": bool(improves_return and improves_dd),
                "improves_neither": bool(not improves_return and not improves_dd),
            }
        )
    return rows


def summarize_windows(rows: list[dict]) -> dict:
    result = {"completed_windows": len(rows), "overlapping_not_independent": True}
    for name in ["improves_return", "improves_drawdown", "improves_both", "improves_neither"]:
        count = sum(row[name] for row in rows)
        result[name] = {"count": count, "fraction": count / len(rows) if rows else None}
    for name in ["portfolio_cagr", "equity_cagr", "portfolio_max_drawdown", "equity_max_drawdown"]:
        result[name] = {
            "minimum": min((x[name] for x in rows), default=None),
            "median": float(np.median([x[name] for x in rows])) if rows else None,
        }
    return result
