"""Grouped descriptive valuations and conditional endpoint-return diagnostics.

Security identities and financial denominator amounts are private audit outputs.
The public projection contains aggregates only. Nothing here certifies historical
financial vintages, reconstructed status, or an executable portfolio cash ledger.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

GROUPS = ("all_market", "non_st", "st", "star_st", "unknown")
PUBLIC_FIELDS = {
    "total_n", "valid_n", "nonpositive_denominator_n", "missing_or_invalid_n",
    "equal_weight_mean", "ratio_of_totals", "median", "minimum", "maximum",
    "p01", "p05", "p10", "p25", "p75", "p90", "p95", "p99",
    "below_one_n", "below_point_one_n", "minimum_ties", "risk_flags",
}


def _name_kind(names: pd.Series) -> pd.Series:
    upper = names.fillna("").str.upper()
    return pd.Series(np.select(
        [upper.str.contains("*ST", regex=False), upper.str.contains("ST", regex=False)],
        ["star_st", "st"], default="non_st"), index=names.index)


def classify_groups(rows: pd.DataFrame, names: pd.DataFrame, positive: pd.DataFrame) -> pd.DataFrame:
    """A dated non-ST name is required; missing positive rows alone prove nothing."""
    if rows.duplicated(["formation_date", "ts_code"]).any():
        raise ValueError("duplicate formation/security identity")
    if positive.duplicated(["trade_date", "ts_code"]).any():
        raise ValueError("ambiguous reconstructed positive state")
    active = names.copy().drop_duplicates()
    active["start_date"] = active.start_date.fillna("99999999").astype(str)
    active["end_date"] = active.end_date.fillna("99999999").astype(str)
    active["ann_date"] = active.ann_date.fillna("99999999").astype(str)
    frames = []
    for day, block in rows.groupby("formation_date", sort=True):
        event = active.loc[active.start_date.le(day) & active.end_date.ge(day) & active.ann_date.lt(day)]
        event = event.loc[event.start_date.eq(event.groupby("ts_code").start_date.transform("max"))].copy()
        ambiguous = event.groupby("ts_code").name.nunique().gt(1)
        event = event.sort_values(["ts_code", "ann_date"]).drop_duplicates("ts_code", keep="last")
        event["ambiguous_name"] = event.ts_code.map(ambiguous)
        block = block.merge(event[["ts_code", "name", "change_reason", "ambiguous_name"]],
                            on="ts_code", how="left", validate="many_to_one")
        state = positive.loc[positive.trade_date.eq(day), ["ts_code", "name", "available_from"]].copy()
        state = state.rename(columns={"name": "positive_name"})
        block = block.merge(state, on="ts_code", how="left", validate="one_to_one")
        kind = _name_kind(block.name)
        positive_kind = _name_kind(block.positive_name)
        present = block.positive_name.notna()
        known = block.name.notna() & ~block.ambiguous_name.fillna(True).astype(bool)
        alive = block.list_date.notna() & block.list_date.le(day)
        alive &= block.delist_date.isna() | block.delist_date.gt(day)
        # Retrospective instrument/name versions remain disclosed, not certified PIT.
        terminal = block.change_reason.fillna("").eq("\u9000\u5e02\u6574\u7406\u671f")
        agree = ((kind.eq("non_st") & ~present) |
                 (kind.ne("non_st") & present & kind.eq(positive_kind)))
        available = ~present | block.available_from.fillna("99999999").le(day)
        admitted = known & alive & ~terminal & agree & available
        block["status"] = kind.where(admitted, "unknown")
        block["status_reason"] = np.select(
            [~alive, ~known, terminal, ~agree, ~available],
            ["instrument_interval_unknown", "name_unknown_or_ambiguous", "delisting_period",
             "name_positive_conflict", "positive_not_available"], default="dated_name_and_state_agree")
        block["name_known"] = known
        frames.append(block)
    return pd.concat(frames, ignore_index=True) if frames else rows.assign(status="unknown")


def describe_metric(frame: pd.DataFrame, metric: str, denominator: str, *, tail_count: int = 10) -> dict:
    """Compute both arithmetic mean and ratio-of-totals on the identical valid set."""
    values = pd.to_numeric(frame[metric], errors="coerce")
    den = pd.to_numeric(frame[denominator], errors="coerce")
    mv = pd.to_numeric(frame.market_value, errors="coerce")
    valid = np.isfinite(values) & values.gt(0) & np.isfinite(den) & den.gt(0) & np.isfinite(mv) & mv.gt(0)
    selected = frame.loc[valid].copy()
    x = values.loc[valid]
    result = {"total_n": len(frame), "valid_n": int(valid.sum()),
              "nonpositive_denominator_n": int((np.isfinite(den) & den.le(0)).sum()),
              "missing_or_invalid_n": int((~valid & ~(np.isfinite(den) & den.le(0))).sum()),
              "equal_weight_mean": float(x.mean()) if len(x) else None,
              "ratio_of_totals": float(mv.loc[valid].sum() / den.loc[valid].sum()) if len(x) else None,
              "median": float(x.median()) if len(x) else None,
              "minimum": float(x.min()) if len(x) else None,
              "maximum": float(x.max()) if len(x) else None,
              "below_one_n": int(x.lt(1).sum()), "below_point_one_n": int(x.lt(.1).sum())}
    for percentile in (1, 5, 10, 25, 75, 90, 95, 99):
        result[f"p{percentile:02}"] = float(x.quantile(percentile / 100)) if len(x) else None
    records = []
    if len(selected):
        selected = selected.sort_values([metric, "ts_code"])
        tail = selected.nsmallest(max(1, tail_count), metric, keep="all")
        fields = [c for c in ["ts_code", "formation_date", "status", "income_period",
                              "fina_indicator_period", "balancesheet_period", "minority_equity_present",
                              "preferred_equity_present", "preferred_equity_unknown"] if c in tail]
        for _, row in tail.iterrows():
            item = {c: row[c] for c in fields}
            item.update(multiple=float(row[metric]), denominator=float(row[denominator]),
                        market_value=float(row.market_value))
            records.append(item)
    result["tail_records"] = records
    minimum = selected.loc[selected[metric].eq(x.min())] if len(x) else selected
    result["minimum_records"] = [dict(item) for item in records if item["multiple"] == result["minimum"]]
    result["minimum_ties"] = len(minimum)
    result["risk_flags"] = ["retrospective_versions", "minimum_not_investment_signal"]
    if result["valid_n"] < 20:
        result["risk_flags"].append("small_valid_sample")
    if result["below_point_one_n"]:
        result["risk_flags"].append("extreme_positive_multiple_check_denominator_and_units")
    if len(x) and result["equal_weight_mean"] > 3 * result["median"]:
        result["risk_flags"].append("right_skew_mean_sensitive_to_small_denominators")
    return result


def public_statistics(private: dict) -> dict:
    """Explicit aggregate allowlist prevents private amounts/identities leaking."""
    return {key: value for key, value in private.items() if key in PUBLIC_FIELDS}


def verify_legacy_values(current: pd.DataFrame, baseline: pd.DataFrame) -> None:
    """Concatenated Parquet can widen integer ages; every stored value stays exact."""
    pd.testing.assert_frame_equal(current[baseline.columns].reset_index(drop=True),
                                  baseline.reset_index(drop=True), check_dtype=False, check_exact=True)


def factor_period(signal: pd.DataFrame, entry: pd.DataFrame, endpoint: pd.DataFrame, *,
                  metric: str, minimum_names: int = 25) -> tuple[dict, pd.DataFrame]:
    """Form quintiles before future availability; never renormalize missing members.

    IC is conditional on available, endpoint-tradable marks and is not an
    executable strategy estimate. Each long-only basket requires every member.
    """
    if not len(entry) or not len(endpoint) or str(endpoint.trade_date.iloc[0]) <= str(entry.trade_date.iloc[0]):
        raise ValueError("endpoint must be after entry")
    multiple = pd.to_numeric(signal[metric], errors="coerce")
    audit = signal.loc[np.isfinite(multiple) & multiple.gt(0), ["ts_code", metric, "delist_date"]].copy()
    if audit.ts_code.duplicated().any():
        raise ValueError("duplicate factor formation identity")
    audit["quintile"] = np.ceil(audit[metric].rank(pct=True, method="average") * 5).astype(int)
    for label, frame in [("entry", entry), ("end", endpoint)]:
        if frame.ts_code.duplicated().any() or frame.trade_date.nunique() != 1:
            raise ValueError("endpoint must have unique securities at one date")
        cols = ["ts_code", "adj_close", "amount", "is_suspended", "is_limit_up", "is_limit_down"]
        audit = audit.merge(frame[cols].rename(columns={c: label + "_" + c for c in cols if c != "ts_code"}),
                            on="ts_code", how="left", validate="one_to_one")
    for label in ("entry", "end"):
        price = pd.to_numeric(audit[label + "_adj_close"], errors="coerce")
        blocked_flag = "is_limit_up" if label == "entry" else "is_limit_down"
        audit[label + "_valid"] = (np.isfinite(price) & price.gt(0) & audit[label + "_amount"].gt(0)
                                     & ~audit[label + "_is_suspended"].fillna(True).astype(bool)
                                     & ~audit[label + "_" + blocked_flag].fillna(True).astype(bool))
    end_date = str(endpoint.trade_date.iloc[0])
    terminal = audit.delist_date.notna() & audit.delist_date.le(end_date)
    audit["resolved"] = audit.entry_valid & audit.end_valid & ~terminal
    audit["forward_return"] = (audit.end_adj_close / audit.entry_adj_close - 1).where(audit.resolved)
    signal_ok = len(audit) >= minimum_names
    observed = audit.loc[audit.resolved]
    varied = observed[metric].nunique() > 1 and observed.forward_return.nunique() > 1
    rho = (-observed[metric]).rank().corr(observed.forward_return.rank()) if signal_ok and len(observed) >= 10 and varied else np.nan
    result = {"signal_n": len(audit), "return_n": len(observed), "unresolved_n": int((~audit.resolved).sum()),
              "rank_ic": float(rho) if np.isfinite(rho) else None, "quintiles": []}
    for q in range(1, 6):
        block = audit.loc[audit.quintile.eq(q)]
        complete = bool(signal_ok and len(block) and block.resolved.all())
        result["quintiles"].append({"quintile": q, "selected_n": len(block),
                                     "unresolved_n": int((~block.resolved).sum()), "complete": complete,
                                     "gross_return": float(block.forward_return.mean()) if complete else None})
    low, high = result["quintiles"][0], result["quintiles"][-1]
    result["cheap_minus_expensive"] = low["gross_return"] - high["gross_return"] if low["complete"] and high["complete"] else None
    result["whole_group_gross_return"] = float(audit.forward_return.mean()) if signal_ok and len(audit) and audit.resolved.all() else None
    return result, audit


def cost_sensitivity(target: dict, previous_drifted: dict | None, gross_return: float, *,
                     cost_bps: tuple = (0, 10, 30), liquidate: bool = False) -> dict:
    """Additive notional-cost scenario, not a fill/cash-ledger simulation.

    Missing preceding basket marks make turnover/net unavailable, never cash.
    """
    if previous_drifted is None:
        return {"traded_notional": None, "net_sensitivity": {str(b): None for b in cost_bps}}
    names = set(target) | set(previous_drifted)
    traded = sum(abs(target.get(s, 0.) - previous_drifted.get(s, 0.)) for s in names)
    traded += float(liquidate)
    return {"traded_notional": float(traded),
            "net_sensitivity": {str(b): float(gross_return - traded * b / 10000) for b in cost_bps}}
