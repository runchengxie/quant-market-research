"""Availability-aware macro classification; reconstructed vintages stay labeled."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _available_time(value) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    return timestamp.tz_localize("Asia/Shanghai") if timestamp.tzinfo is None else timestamp


def classify_regimes(
    decisions: pd.DatetimeIndex, records: pd.DataFrame, require_verified: bool = True
) -> list[dict]:
    required = {"series", "available_at", "value", "vintage_verified"}
    if not required <= set(records):
        raise ValueError("macro series, availability, values and vintage flags required")
    data = records.copy()
    data["available_at"] = [_available_time(v).tz_convert("UTC") for v in data.available_at]
    data["value"] = pd.to_numeric(data.value, errors="raise")
    if not np.isfinite(data.value).all() or data.duplicated(["series", "available_at"]).any():
        raise ValueError("finite unique macro releases required")
    if require_verified:
        data = data.loc[data.vintage_verified.eq(True)]
    data = data.sort_values("available_at")
    rows = []
    for decision in decisions:
        cutoff = _available_time(decision.normalize()) + pd.Timedelta(hours=15)
        known = data.loc[
            (data.available_at <= cutoff) & (data.available_at > cutoff - pd.Timedelta(days=100))
        ]
        picked = {s: known.loc[known.series.eq(s)].tail(1) for s in ["pmi", "ppi"]}
        row = {
            "decision_date": str(decision.date()),
            "regime": None,
            "point_in_time_verified": False,
        }
        if all(len(v) for v in picked.values()):
            pmi, ppi = float(picked["pmi"].value.iloc[0]), float(picked["ppi"].value.iloc[0])
            row.update(
                regime=("pmi_at_least_50" if pmi >= 50 else "pmi_below_50")
                + "__"
                + ("ppi_at_least_0" if ppi >= 0 else "ppi_below_0"),
                point_in_time_verified=bool(
                    all(v.vintage_verified.iloc[0] for v in picked.values())
                ),
                pmi=pmi,
                ppi=ppi,
                latest_available_at=max(
                    v.available_at.iloc[0] for v in picked.values()
                ).isoformat(),
            )
        rows.append(row)
    return rows
