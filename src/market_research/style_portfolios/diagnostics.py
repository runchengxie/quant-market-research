from __future__ import annotations

from numbers import Integral

import numpy as np
import pandas as pd


def analyze_tail_monotonicity(
    quantile_returns: pd.DataFrame,
    *,
    direction: str = "ascending",
    tail_quantiles: int = 1,
) -> dict[str, object]:
    """Compare a curve and disjoint tails on common, fully observed dates.

    direction orders the buckets; score is the fraction of nondecreasing
    adjacent means in that order, and spread is first-tail minus last-tail.
    All requested buckets must be present and complete on a date for that date
    to enter either metric. Legacy inputs without requested_quantiles use their
    observed bucket universe. observations counts comparable formation dates.
    """
    if (
        direction not in {"ascending", "descending"}
        or not isinstance(tail_quantiles, Integral) or isinstance(tail_quantiles, bool)
        or tail_quantiles < 1
    ):
        raise ValueError("invalid direction or tail_quantiles")
    summary = {
        "status": "unavailable",
        "monotonicity_score": None,
        "tail_spread": None,
        "observations": 0,
        "formation_dates": 0,
        "excluded_formation_dates": 0,
        "quantiles": 0,
        "direction": direction,
        "warnings": [],
    }
    warnings = summary["warnings"]
    if quantile_returns.empty:
        warnings.append("no_formation_returns")
        return summary
    required = {"formation_date", "bucket", "mean_forward_return"}
    missing = required.difference(quantile_returns.columns)
    if missing:
        raise ValueError("missing quantile columns: " + ", ".join(sorted(missing)))
    frame = quantile_returns.copy()
    if frame.duplicated(["formation_date", "bucket"]).any():
        raise ValueError("duplicate formation_date/bucket rows")
    if frame[["formation_date", "bucket"]].isna().any().any():
        raise ValueError("formation_date and bucket must not be null")
    buckets = sorted(frame["bucket"].unique())
    if "requested_quantiles" in frame:
        requested = pd.to_numeric(frame["requested_quantiles"], errors="coerce")
        if (
            requested.isna().any() or not np.isfinite(requested).all()
            or requested.nunique() != 1 or requested.iloc[0] < 2
            or requested.iloc[0] != int(requested.iloc[0])
        ):
            raise ValueError("requested_quantiles must be one consistent integer >= 2")
        buckets = list(range(1, int(requested.iloc[0]) + 1))
        if not frame["bucket"].isin(buckets).all():
            raise ValueError("bucket outside requested_quantiles")
    summary["quantiles"] = len(buckets)
    summary["formation_dates"] = int(frame["formation_date"].nunique())
    summary["excluded_formation_dates"] = summary["formation_dates"]
    values = pd.to_numeric(frame["mean_forward_return"], errors="coerce")
    complete = pd.Series(np.isfinite(values), index=frame.index)
    if {"count", "observed_return_count"}.issubset(frame):
        count = pd.to_numeric(frame["count"], errors="coerce")
        observed = pd.to_numeric(frame["observed_return_count"], errors="coerce")
        complete &= count.gt(0) & np.isfinite(count) & observed.eq(count)
    if "return_coverage" in frame:
        complete &= pd.to_numeric(frame["return_coverage"], errors="coerce").eq(1)
    if "missing_return_count" in frame:
        complete &= pd.to_numeric(frame["missing_return_count"], errors="coerce").eq(0)
    if not complete.all():
        warnings.append("missing_return_coverage")
    frame["mean_forward_return"] = values.where(complete)
    matrix = frame.pivot(index="formation_date", columns="bucket", values="mean_forward_return")
    matrix = matrix.reindex(columns=buckets)
    paired = matrix.dropna()
    if len(paired) != len(matrix):
        warnings.append("incomplete_quantile_dates")
    if len(buckets) < 2:
        warnings.append("insufficient_quantiles")
        return summary
    if tail_quantiles * 2 > len(buckets):
        warnings.append("overlapping_tails")
        return summary
    if paired.empty:
        warnings.append("no_comparable_formation_dates")
        return summary
    if direction == "descending":
        paired = paired[paired.columns[::-1]]
    # Compute both statistics from the same date set, never unpaired averages.
    curve = paired.mean()
    spread = (paired.iloc[:, :tail_quantiles].mean(axis=1)
              - paired.iloc[:, -tail_quantiles:].mean(axis=1)).mean()
    if not np.isfinite(curve).all() or not np.isfinite(spread):
        warnings.append("nonfinite_diagnostic")
        return summary
    summary.update({
        "status": "available",
        "monotonicity_score": float((curve.diff().iloc[1:] >= 0).mean()),
        "tail_spread": float(spread),
        "observations": int(len(paired)),
        "excluded_formation_dates": int(len(matrix) - len(paired)),
    })
    return summary


def summarize_market_factor_evidence(
    quantile_returns: pd.DataFrame, factor_name: str, metadata: dict[str, object] | None = None
) -> dict[str, object]:
    summary = analyze_tail_monotonicity(quantile_returns)
    summary.update({
        "factor": factor_name,
        "evidence_status": "derived" if summary["status"] == "available" else "unavailable",
    })
    if metadata:
        summary["provenance"] = metadata
    return summary
