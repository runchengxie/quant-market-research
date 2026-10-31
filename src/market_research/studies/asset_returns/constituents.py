"""Annual constituent-cohort audit, separate from financial earnings causality."""

from __future__ import annotations

import numpy as np
import pandas as pd


def constituent_retention(
    frame: pd.DataFrame, expected_count: int, weight_quantum: float = 0
) -> dict:
    data = frame[["date", "symbol", "weight"]].copy()
    data["date"] = pd.to_datetime(data.date, errors="raise")
    data["weight"] = pd.to_numeric(data.weight, errors="raise")
    if (
        data.empty
        or data.date.isna().any()
        or data.symbol.isna().any()
        or data.duplicated(["date", "symbol"]).any()
        or not np.isfinite(data.weight).all()
        or (data.weight < 0).any()
    ):
        raise ValueError("unique dated members and finite nonnegative fractional weights required")
    if not np.isfinite(weight_quantum) or weight_quantum < 0:
        raise ValueError("invalid declared weight precision")
    if weight_quantum and not np.allclose(
        data.weight / weight_quantum, np.round(data.weight / weight_quantum), atol=1e-7, rtol=0
    ):
        raise ValueError("weights do not match declared rounding quantum")
    raw_sums = []
    snapshots = []
    for date, group in data.sort_values("date").groupby("date"):
        if (
            len(group) != expected_count
            or abs(group.weight.sum() - 1) > expected_count * weight_quantum / 2 + 1e-10
        ):
            raise ValueError("snapshot count or weight closure failed")
        raw_sums.append({"date": date.date().isoformat(), "weight_sum": float(group.weight.sum())})
        snapshots.append((date, group.set_index("symbol").weight / group.weight.sum()))
    if len(snapshots) < 2:
        raise ValueError("at least two annual snapshots are required")
    years = np.array([date.year for date, _ in snapshots])
    if not np.all(np.diff(years) == 1):
        raise ValueError("exactly one snapshot in each consecutive year required")
    first_date, first = snapshots[0]
    last_date, last = snapshots[-1]
    transitions = []
    for (date0, w0), (date1, w1) in zip(snapshots, snapshots[1:]):
        a, b = set(w0.index), set(w1.index)
        both = sorted(a | b)
        transitions.append(
            {
                "from": date0.date().isoformat(),
                "to": date1.date().isoformat(),
                "retained_count": len(a & b),
                "entries": len(b - a),
                "exits": len(a - b),
                "jaccard": len(a & b) / len(a | b),
                "weight_distance": float(
                    0.5
                    * (w0.reindex(both, fill_value=0) - w1.reindex(both, fill_value=0)).abs().sum()
                ),
            }
        )
    retained = set(first.index) & set(last.index)
    return {
        "start": first_date.date().isoformat(),
        "end": last_date.date().isoformat(),
        "snapshots": len(snapshots),
        "weight_rounding_quantum": weight_quantum,
        "raw_weight_sums": raw_sums,
        "maximum_raw_weight_sum_error": max(abs(r["weight_sum"] - 1) for r in raw_sums),
        "initial_count": len(first),
        "final_count": len(last),
        "cohort_retained_count": len(retained),
        "cohort_retained_fraction": len(retained) / len(first),
        "retained_initial_weight": float(first.loc[list(retained)].sum()),
        "retained_final_weight": float(last.loc[list(retained)].sum()),
        "transitions": transitions,
        "measured_turnover": False,
        "financial_growth_attribution_status": "blocked_pending_independent_financial_and_share_ledgers",
        "interpretation": "Snapshot membership and weight distance include market drift, omit within-year transitions and are not realized trading turnover.",
    }


def profit_bridge(frame: pd.DataFrame) -> dict:
    """Aggregate-profit identity, not index EPS or an independent vintage audit.

    Requires closing profits of exited firms for the fixed opening cohort. Never
    substitute zero for a delisted/missing firm. Negative profits remain included.
    """
    data = frame[
        ["symbol", "opening_profit", "closing_profit", "opening_member", "closing_member"]
    ].copy()
    if data.symbol.isna().any() or data.symbol.duplicated().any() or data.empty:
        raise ValueError("unique nonmissing company identities required")
    for col in ["opening_member", "closing_member"]:
        if (
            data[col].isna().any()
            or not data[col].map(lambda x: isinstance(x, (bool, np.bool_))).all()
        ):
            raise ValueError("membership must be explicit booleans")
    opening = data.opening_member
    closing = data.closing_member
    if not opening.any() or not closing.any():
        raise ValueError("both periods need members")
    for col, needed in [("opening_profit", opening), ("closing_profit", opening | closing)]:
        data[col] = pd.to_numeric(data[col], errors="raise")
        if not np.isfinite(data.loc[needed, col]).all():
            raise ValueError("required profits missing; exited companies cannot disappear")
    common = opening & closing
    entrants = closing & ~opening
    exits = opening & ~closing
    base = float(data.loc[opening, "opening_profit"].sum())
    final = float(data.loc[closing, "closing_profit"].sum())
    incumbent = float(
        (data.loc[common, "closing_profit"] - data.loc[common, "opening_profit"]).sum()
    )
    membership = float(
        data.loc[entrants, "closing_profit"].sum() - data.loc[exits, "opening_profit"].sum()
    )
    fixed = float((data.loc[opening, "closing_profit"] - data.loc[opening, "opening_profit"]).sum())
    return {
        "dynamic_profit_change": final - base,
        "incumbent_profit_change": incumbent,
        "net_membership_change": membership,
        "fixed_initial_cohort_profit_change": fixed,
        "reconciliation_error": final - base - incumbent - membership,
        "independent_financial_vintage_validation": False,
        "per_share_index_attribution": False,
        "interpretation": "Same-scope aggregate-profit accounting requires independent financial scope, revisions and shares before investment interpretation.",
    }
