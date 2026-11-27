"""Private pilot summaries; no inference of strategy returns or executable capacity."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from math import isfinite
from typing import Any


def decode_statement(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Reject unfinished/truncated results instead of silently analysing a partial chunk."""
    if response.get("status", {}).get("state") != "SUCCEEDED":
        raise ValueError("SQL statement has not succeeded")
    manifest = response["manifest"]
    if manifest.get("truncated"):
        raise ValueError("SQL result was truncated")
    rows = response.get("result", {}).get("data_array", [])
    if len(rows) != manifest.get("total_row_count"):
        raise ValueError("Fetch all result chunks before analysis")
    columns = manifest["schema"]["columns"]
    result = []
    for row in rows:
        if len(row) != len(columns):
            raise ValueError("Result shape differs from manifest")
        parsed = {}
        for column, value in zip(columns, row, strict=True):
            kind = column["type_name"]
            if value is not None and kind in ("DOUBLE", "FLOAT", "DECIMAL"):
                value = float(value)
                if not isfinite(value):
                    raise ValueError("Non-finite SQL metric")
            elif value is not None and kind in ("INT", "LONG", "BIGINT", "SHORT"):
                value = int(value)
            parsed[column["name"]] = value
        result.append(parsed)
    return result


def cap_bucket(value: float | None) -> str:
    if value is None or not isfinite(value) or value <= 0:
        return "unclassified"
    for upper, label in [
        (1e7, "under_10m"),
        (1e8, "10m_100m"),
        (1e9, "100m_1bn"),
        (1e10, "1bn_10bn"),
    ]:
        if value < upper:
            return label
    return "over_10bn"


def annual_cost_hurdle(spread_bps: float, holding_days: int, turnover_fraction: float = 1) -> float:
    """Scenario: one full spread per round trip; ignores impact, fees and signal returns."""
    if spread_bps < 0 or holding_days <= 0 or not 0 <= turnover_fraction <= 1:
        raise ValueError("Invalid cost scenario")
    return spread_bps / 10000 * 252 / holding_days * turnover_fraction


def paired_summary(
    rows: list[dict], metric: str, baseline: set[str], comparison: set[str]
) -> list[dict]:
    """Average windows within day, then days within period; retain paired securities only."""
    days = defaultdict(list)
    for row in rows:
        if row[metric] is not None:
            days[(row["ticker"], row["trade_date"])].append(row[metric])
    periods = defaultdict(lambda: [[], []])
    for (ticker, date), values in days.items():
        if date in baseline:
            periods[ticker][0].append(mean(values))
        elif date in comparison:
            periods[ticker][1].append(mean(values))
    result = []
    for ticker, (before, after) in sorted(periods.items()):
        if before and after:
            a, b = mean(before), mean(after)
            result.append(
                {
                    "ticker": ticker,
                    "baseline": a,
                    "comparison": b,
                    "ratio": b / a if a else None,
                    "difference": b - a,
                }
            )
    return result
