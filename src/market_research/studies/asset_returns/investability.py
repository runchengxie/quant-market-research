"""Publication-boundary and explicitly hypothetical round-trip cost diagnostics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .analysis import validate_levels


def launch_split(frame, launch: str) -> dict:
    data = validate_levels(frame, ["total"])
    day = pd.Timestamp(launch)
    pre = data.loc[data.date < day.to_period("M").start_time]
    post = data.loc[data.date >= day]

    def summary(sub):
        if len(sub) < 2:
            return {"months": 0, "cagr": None, "start": None, "first_return_end": None, "end": None}
        return {
            "months": len(sub) - 1,
            "cagr": float((sub.total.iloc[-1] / sub.total.iloc[0]) ** (12 / (len(sub) - 1)) - 1),
            "start": sub.date.iloc[0].date().isoformat(),
            "first_return_end": sub.date.iloc[1].date().isoformat(),
            "end": sub.date.iloc[-1].date().isoformat(),
        }

    return {
        "launch_date": launch,
        "pre_launch": summary(pre),
        "post_launch": summary(post),
        "excluded_launch_month_returns": int(
            ((data.date.dt.to_period("M") == day.to_period("M")) & (data.index > 0)).sum()
        ),
        "total_return_series_original_publication_verified": False,
    }


def round_trip_cagr(growth: float, months: int, cost_bps: float) -> float:
    if (
        not np.isfinite([growth, cost_bps]).all()
        or growth <= 0
        or type(months) is not int
        or months < 1
        or not 0 <= cost_bps < 10000
    ):
        raise ValueError("invalid gross growth, duration or per-side fee")
    rate = cost_bps / 10000
    return float((growth * (1 - rate) / (1 + rate)) ** (12 / months) - 1)


def validate_register(claims: list[dict]) -> None:
    ids = [row.get("id") for row in claims]
    if not all(isinstance(key, str) and key for key in ids) or len(ids) != len(set(ids)):
        raise ValueError("claims need unique stable identifiers")
    for row in claims:
        if row.get("stage") not in {
            "historical_descriptive",
            "sensitivity_only",
            "blocked",
            "protocol_frozen",
        }:
            raise ValueError(
                "unsupported evidence stage; future validation needs separate admission"
            )
        if not all(
            row.get(key) for key in ["scope", "evidence", "review_trigger", "open_question"]
        ):
            raise ValueError("claim scope, evidence and falsification/review conditions required")
