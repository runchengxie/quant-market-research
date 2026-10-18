"""Public aggregate gate for reviewed stress and sampled clock-window evidence."""

import hashlib
import json
import math
import re

from .liquidity_publication import _safe
from .liquidity_stress import WINDOWS


def reviewed_stress(raw: bytes, review: dict, base: dict) -> dict:
    if (
        review.get("passed") is not True
        or review.get("reviewed_summary_sha256") != hashlib.sha256(raw).hexdigest()
    ):
        raise ValueError("review checksum mismatch")
    if (
        review.get("aggregate_cells_checked", 0) <= 0
        or review.get("cohort_formations_checked", 0) <= 0
    ):
        raise ValueError("independent cohort/statistic checks missing")
    result = json.loads(raw)
    _safe(result)
    if re.search(r"\b\d{6}\.(?:SH|SZ|BJ)\b", raw.decode()):
        raise ValueError("security identifiers are not public aggregates")
    expected = next(
        r["sha256"] for r in base["source_receipts"] if r["source_id"] == "a_sh_sz_features"
    )
    if result["feature_sha256"] != expected:
        raise ValueError("source feature version differs from published daily scope")
    if (
        result["schema_version"] != "liquidity.stress-persistence.v1"
        or result["historical_pit_eligible"] is not False
        or result["actual_execution_calibrated"] is not False
    ):
        raise ValueError("invalid evidence declaration")
    if len(result["minute_quality"]) != review.get("raw_minute_dates_checked"):
        raise ValueError("raw window dates not fully reviewed")
    for key in ["stress", "cohorts"]:
        keys = [(r["year"], r["bucket"]) for r in result[key]]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate year/bucket aggregates")
    for row in result["stress"]:
        ratio = row["retained_budget_fraction"]
        if ratio is not None and (
            row["months"] < 6
            or not 0 <= ratio <= 1
            or len(row["stress_months"]) != math.ceil(row["months"] * 0.2)
        ):
            raise ValueError("invalid lower-turnover month selection")
    for row in result["cohorts"]:
        values = [
            row[key + "_fraction"] for key in ["retained", "migrated", "ineligible", "missing"]
        ]
        if not all(0 <= v <= 1 for v in values) or not math.isclose(sum(values), 1, abs_tol=1e-10):
            raise ValueError("endpoint categories do not conserve membership")
        if (
            not 0 <= row["continuous_fraction"] <= row["retained_fraction"]
            or not 0 <= row["frozen_valid_formations"] <= row["formations"]
        ):
            raise ValueError("invalid continuity denominator")
    for row in result["cohorts"]:
        if (
            not row["continuous_fraction"]
            <= row["usable_continuous_fraction"]
            <= row["retained_fraction"] + row["migrated_fraction"] + 1e-12
        ):
            raise ValueError("continuous usable membership does not conserve endpoint eligibility")
    totals = {}
    for row in result["minute_quality"]:
        if sum(row["reasons"].values()) != row["eligible_candidates"] or row["accepted"] != row[
            "reasons"
        ].get("accepted", 0):
            raise ValueError("minute qualification ledger does not conserve candidates")
        year = int(row["date"][:4])
        totals[year] = totals.get(year, 0) + row["accepted"]
    groups = {}
    for row in result["windows"]:
        if row["window"] not in WINDOWS:
            raise ValueError("unknown clock window")
        values = [row[k] for k in ["p25", "median", "p75"]]
        if row["observations"]:
            if any(v is None or not 0 <= v <= 1 for v in values) or sorted(values) != values:
                raise ValueError("invalid window share quantiles")
        elif any(v is not None for v in values):
            raise ValueError("missing windows must stay null")
        key = (row["year"], row["window"])
        groups[key] = groups.get(key, 0) + row["observations"] + row["missing_window_observations"]
    for year, n in totals.items():
        for window in WINDOWS:
            if groups.get((year, window), 0) != n:
                raise ValueError("window observations do not conserve accepted stock-days")
    return result
