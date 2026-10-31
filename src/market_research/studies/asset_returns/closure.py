"""Descriptive ETF reconciliation and conservative missing-member classification."""

from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"], errors="raise")
    if result.empty or result.date.isna().any() or not result.date.is_monotonic_increasing:
        raise ValueError("monthly dates must be present and ordered")
    periods = pd.PeriodIndex(result.date, freq="M")
    if periods.has_duplicates or not periods.equals(
        pd.period_range(periods[0], periods[-1], freq="M")
    ):
        raise ValueError("monthly observations must be unique and contiguous")
    values = result.drop(columns="date").to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("levels must be finite and positive")
    return result


def annual_etf_audit(frame: pd.DataFrame, disclosed: dict[int, float]) -> list[dict]:
    frame = monthly_frame(frame)
    frame["year"] = frame.date.dt.year
    rows = []
    for year in sorted(frame.year.unique()):
        start = frame[(frame.year == year - 1) & (frame.date.dt.month == 12)]
        end = frame[(frame.year == year) & (frame.date.dt.month == 12)]
        if start.empty or end.empty:
            continue
        nav = float(end.adj_nav.iloc[0] / start.adj_nav.iloc[0] - 1)
        reference = float(end.index_total.iloc[0] / start.index_total.iloc[0] - 1)
        reported = disclosed.get(int(year))
        rows.append(
            {
                "year": int(year),
                "nav_return": nav,
                "index_total_return": reference,
                "relative_wealth_change": (1 + nav) / (1 + reference) - 1,
                "log_relative_growth": float(np.log1p(nav) - np.log1p(reference)),
                "disclosed_nav_return": reported,
                "disclosed_return_matches": None
                if reported is None
                else abs(nav - reported) <= 0.00005 + 1e-12,
            }
        )
    return rows


def classify_member(
    master: dict | None, profit_available: bool, fiscal_end: str = "20251231"
) -> str:
    if profit_available:
        return "profit_retrieved_requires_vintage_review"
    if master is None:
        return "unresolved_identity"
    if master.get("list_status") == "D":
        date = str(master.get("delist_date") or "")
        if len(date) != 8 or not date.isdigit():
            return "delisted_date_unresolved"
        return "delisted_by_fiscal_end" if date <= fiscal_end else "delisted_after_fiscal_end"
    if master.get("list_status") == "L":
        return "listed_missing_profit"
    return "unresolved_identity"
