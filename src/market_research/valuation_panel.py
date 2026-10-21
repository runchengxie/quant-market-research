"""Descriptive valuation coverage and ranks; no returns or trading eligibility."""

from itertools import combinations

import numpy as np
import pandas as pd

METRICS = ["pe_ttm", "pe_deducted_proxy", "pb_parent", "pb_ex_goodwill_proxy", "pb_ex_intangibles_proxy"]
STATEMENT_FIELDS = {
    "income": ["n_income_attr_p", "comp_type"],
    "fina_indicator": ["profit_dedt", "roe"],
    "balancesheet": ["total_hldr_eqy_exc_min_int", "goodwill", "intan_assets", "minority_int", "oth_eqt_tools_p_shr"],
}


def admitted(frame: pd.DataFrame, date: str, require_observed: bool) -> pd.DataFrame:
    """Select known report versions; reconstructed mode never certifies old retrievals."""
    day = pd.Timestamp(date)
    cutoff = day.tz_localize("Asia/Shanghai") + pd.Timedelta(hours=18)
    disclosure = pd.concat([
        pd.to_datetime(frame[c], format="%Y%m%d", errors="coerce")
        for c in ["ann_date", "f_ann_date"] if c in frame
    ], axis=1).max(axis=1)
    observed = pd.to_datetime(frame["_source_retrieved_at"], utc=True, errors="coerce")
    mask = disclosure.notna() & (disclosure < day) & observed.notna()
    if require_observed:
        mask &= observed <= cutoff
    if "report_type" in frame:
        mask &= frame.report_type.astype(str).eq("1")
    selected = frame.loc[mask].copy()
    selected["disclosed"] = disclosure.loc[mask]
    selected["observed"] = observed.loc[mask]
    keys = ["ts_code", "end_date", "disclosed", "observed"]
    if selected.duplicated(keys).any():
        raise ValueError("ambiguous same-version statement rows")
    return selected.sort_values(["disclosed", "observed"]).drop_duplicates(["ts_code", "end_date"], keep="last")


def trailing_values(latest: pd.DataFrame, source: pd.DataFrame, field: str) -> pd.Series:
    """Match prior full-year and prior-year cumulative legs without zero filling."""
    lookup = pd.to_numeric(source.set_index(["ts_code", "end_date"])[field], errors="coerce")
    periods = latest.end_date.astype(str)
    years = periods.str[:4].astype(int) - 1
    annual_dates = years.astype(str) + "1231"
    prior_dates = years.astype(str) + periods.str[4:]
    def take(dates):
        key = pd.MultiIndex.from_arrays([latest.ts_code, dates])
        return pd.Series(lookup.reindex(key).to_numpy(), index=latest.index)
    current = take(periods)
    return current.where(periods.str.endswith("1231"), current + take(annual_dates) - take(prior_dates))


def make_panel(statements: dict[str, pd.DataFrame], prices: pd.DataFrame, date: str, *, require_observed: bool, private_denominators: bool = False) -> pd.DataFrame:
    if prices.ts_code.duplicated().any():
        raise ValueError("duplicate daily-basic issuer")
    if set(prices.trade_date.astype(str)) != {date}:
        raise ValueError("daily-basic partition date differs from formation date")
    known = {name: admitted(frame, date, require_observed) for name, frame in statements.items()}
    # Each metric uses its own latest report; a missing third table must not erase it.
    latest = {}
    for name in known:
        selected = known[name].sort_values("end_date").drop_duplicates("ts_code", keep="last").copy()
        if name == "income":
            selected["profit_ttm"] = trailing_values(selected, known[name], "n_income_attr_p")
        elif name == "fina_indicator":
            selected["deducted_ttm"] = trailing_values(selected, known[name], "profit_dedt")
        selected[name + "_age_days"] = (pd.Timestamp(date) - pd.to_datetime(selected.end_date, format="%Y%m%d")).dt.days
        derived = ["profit_ttm"] if name == "income" else ["deducted_ttm"] if name == "fina_indicator" else []
        latest[name] = selected[["ts_code", "end_date", *STATEMENT_FIELDS[name], *derived, name + "_age_days"]].rename(columns={"end_date": name + "_period"})
    out = prices[["ts_code", "total_mv"]].copy()
    for name, selected in latest.items():
        out = out.merge(selected, on="ts_code", how="left", validate="one_to_one")
    out["end_date"] = out.balancesheet_period
    out["same_report_period"] = out.income_period.notna() & out.income_period.eq(out.fina_indicator_period) & out.income_period.eq(out.balancesheet_period)
    out["report_age_days"] = out.balancesheet_age_days
    out["market_value"] = pd.to_numeric(out.total_mv, errors="coerce") * 10000
    valid_mv = np.isfinite(out.market_value) & (out.market_value > 0)
    out = out.loc[valid_mv].copy()
    equity = pd.to_numeric(out.total_hldr_eqy_exc_min_int, errors="coerce")
    goodwill = pd.to_numeric(out.goodwill, errors="coerce")
    intangible = pd.to_numeric(out.intan_assets, errors="coerce")
    # Invalid negative asset balances are unavailable, not a bonus to book equity.
    goodwill = goodwill.where(goodwill >= 0)
    intangible = intangible.where(intangible >= 0)
    denominators = [out.profit_ttm, out.deducted_ttm, equity, equity - goodwill, equity - goodwill - intangible]
    fresh = [out.income_age_days.between(0, 550), out.fina_indicator_age_days.between(0, 550), *[out.balancesheet_age_days.between(0, 550)] * 3]
    for name, denominator, age_valid in zip(METRICS, denominators, fresh, strict=True):
        denominator = pd.to_numeric(denominator, errors="coerce").where(age_valid)
        out["denominator_" + name] = denominator.where(np.isfinite(denominator))
        out[name + "_nonpositive"] = np.isfinite(denominator) & (denominator <= 0)
        out[name] = (out.market_value / denominator).where(np.isfinite(denominator) & (denominator > 0))
        out[name] = out[name].where(np.isfinite(out[name]))
    out["reporting_group"] = out.comp_type.astype(str).map({"1": "general_reporting", "2": "financial_reporting", "3": "financial_reporting", "4": "financial_reporting", "7": "financial_reporting"}).fillna("unknown")
    out["size_bucket"] = np.ceil(out.market_value.rank(pct=True, method="average") * 5).astype(int)
    roe = pd.to_numeric(out.roe, errors="coerce")
    roe = roe.where(np.isfinite(roe) & out.fina_indicator_age_days.between(0, 550))
    out["profitability_bucket"] = np.ceil(roe.groupby(out.reporting_group).rank(pct=True) * 5)
    out["all_metrics_available"] = out[METRICS].notna().all(axis=1)
    out["common_five"] = out.all_metrics_available & out.same_report_period
    out["formation_date"] = date
    out["stale_statement"] = out[[n + "_age_days" for n in known]].gt(550).any(axis=1)
    out["minority_equity_present"] = pd.to_numeric(out.minority_int, errors="coerce") > 0
    out["preferred_equity_present"] = pd.to_numeric(out.oth_eqt_tools_p_shr, errors="coerce") > 0
    out["preferred_equity_unknown"] = pd.to_numeric(out.oth_eqt_tools_p_shr, errors="coerce").isna()
    # Retain derived outputs only; do not copy financial source amounts into research outputs.
    columns = ["ts_code", "formation_date", "end_date", "report_age_days", "income_period", "fina_indicator_period", "balancesheet_period", "same_report_period", "all_metrics_available", "reporting_group", "size_bucket", "profitability_bucket", "common_five", "stale_statement", "minority_equity_present", "preferred_equity_present", "preferred_equity_unknown", *METRICS, *[m + "_nonpositive" for m in METRICS]]
    if private_denominators:
        columns += ["market_value", *["denominator_" + m for m in METRICS]]
    result = out[columns].reset_index(drop=True)
    result.attrs["input_quote_records"] = len(prices)
    return result


def rank_comparison(frame: pd.DataFrame, first: str, second: str) -> dict:
    sample = frame.loc[frame.common_five]
    n = len(sample)
    if n < 5:
        return {"first": first, "second": second, "n": n, "spearman": None, "bottom_quintile_jaccard": None}
    a, b = sample[first].rank(), sample[second].rank()
    rho = a.corr(b)
    k = max(1, int(np.ceil(n * .2)))
    left = set(sample.nsmallest(k, first, keep="all").ts_code)
    right = set(sample.nsmallest(k, second, keep="all").ts_code)
    return {"first": first, "second": second, "n": n,
            "spearman": float(rho) if np.isfinite(rho) else None,
            "bottom_quintile_jaccard": len(left & right) / len(left | right),
            "first_selected": len(left), "second_selected": len(right)}


def summarize(frame: pd.DataFrame) -> dict:
    n = len(frame)
    metrics = [{"metric": m, "available": int(frame[m].notna().sum()),
                "nonpositive": int(frame[m + "_nonpositive"].sum()),
                "missing_or_invalid": int(frame[m].isna().sum() - frame[m + "_nonpositive"].sum())} for m in METRICS]
    strata = []
    for (sector, size), group in frame.groupby(["reporting_group", "size_bucket"]):
        strata.append({"reporting_group": sector, "size_bucket": int(size), "records": len(group), "common_five": int(group.common_five.sum())})
    controlled = []
    for first, second in [("pe_ttm", "pe_deducted_proxy"), ("pb_parent", "pb_ex_intangibles_proxy"), ("pe_ttm", "pb_parent")]:
        values = []
        for _, group in frame.groupby(["reporting_group", "size_bucket", "profitability_bucket"]):
            if group.reporting_group.iloc[0] == "unknown" or group.common_five.sum() < 20:
                continue
            result = rank_comparison(group, first, second)
            if result["spearman"] is not None:
                values.append(result["spearman"])
        controlled.append({"first": first, "second": second, "strata": len(values), "median_within_stratum_spearman": float(np.median(values)) if values else None})
    return {"date": str(frame.formation_date.iloc[0]) if n else None, "quote_records": n,
            "input_quote_records": frame.attrs.get("input_quote_records", n), "all_metrics_available": int(frame.all_metrics_available.sum()), "common_five": int(frame.common_five.sum()), "stale_statements": int(frame.stale_statement.sum()),
            "no_common_report": int((~frame.same_report_period).sum()),
            "minority_equity_present": int(frame.minority_equity_present.sum()),
            "preferred_equity_present": int(frame.preferred_equity_present.sum()),
            "preferred_equity_unknown": int(frame.preferred_equity_unknown.sum()),
            "metrics": metrics, "report_type_size_coverage": strata,
            "rank_pairs": [rank_comparison(frame, a, b) for a, b in combinations(METRICS, 2)],
            "report_type_size_roe_rank_diagnostics": controlled}
