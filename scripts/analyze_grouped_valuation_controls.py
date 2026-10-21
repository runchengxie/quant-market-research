#!/usr/bin/env python3
"""Frozen exploratory controls on retained adjusted-unit member contributions.

No ledger rerun, outcome-based matching, missing-value imputation, or publication.
Formation-year results group lifetime cohort contributions, not calendar returns.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from market_research.valuation_panel import admitted

PRIMARY_FEATURES = ["reporting_group", "size_bucket", "profitability_bucket"]
ALLOWED_FEATURES = {*PRIMARY_FEATURES, "quality_bucket", "leverage_bucket"}
RULES_HASH = "b44a924b7cc401147d8b98b066230d5c9c2da67768423db83d2017851d659443"
OUTCOMES = {"strict": "strict", "reference_0": "0", "reference_50": "50", "reference_100": "100"}
LAYERS = {
    "report_size": ["reporting_group", "size_bucket"],
    "report_size_profitability": PRIMARY_FEATURES,
    "secondary_quality": [*PRIMARY_FEATURES, "quality_bucket"],
    "secondary_leverage": [*PRIMARY_FEATURES, "leverage_bucket"],
}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def dump(path, value):
    Path(path).write_text(json.dumps(clean_json(value), indent=2, ensure_ascii=True, allow_nan=False) + "\n")


def feature_complete(frame, features):
    if not features or not set(features).issubset(ALLOWED_FEATURES):
        raise ValueError("outcome-dependent or unapproved matching feature")
    valid = frame[features].notna().all(axis=1)
    if "reporting_group" in features:
        valid &= frame.reporting_group.isin(["general_reporting", "financial_reporting"])
    return frame.loc[valid].copy()


def match_support(frame, features, comparison, minimum=5):
    """Create support/weights using only predeclared formation features and Q."""
    sample = feature_complete(frame, features)
    sample = sample.loc[sample.quintile.isin([1, comparison])].copy()
    sample["match_weight"] = np.nan
    sample["stratum_weight"] = np.nan
    if sample.empty:
        return sample
    counts = sample.groupby([*features, "quintile"], observed=True).size().unstack("quintile", fill_value=0)
    if not {1, comparison}.issubset(counts.columns):
        return sample.iloc[:0].copy()
    shared = counts.loc[counts[1].ge(minimum) & counts[comparison].ge(minimum)]
    if shared.empty:
        return sample.iloc[:0].copy()
    shared = shared.copy()
    shared["stratum_weight"] = shared[1] / shared[1].sum()
    shared = shared.rename(columns={1: "q1_count", comparison: "comparison_count"})
    sample = sample.drop(columns=["match_weight", "stratum_weight"]).merge(
        shared.reset_index(), on=features, how="inner", validate="many_to_one")
    sample["match_weight"] = sample.stratum_weight / np.where(
        sample.quintile.eq(1), sample.q1_count, sample.comparison_count)
    return sample


def common_sample(frame):
    return frame.loc[frame.common_five & frame.same_report_period].copy()


def estimate(frame, outcome, comparison, weighted=False):
    result = {}
    for q, name in [(1, "q1"), (comparison, "comparison")]:
        arm = frame.loc[frame.quintile.eq(q)]
        values = pd.to_numeric(arm[outcome], errors="coerce")
        good = np.isfinite(values)
        n, known = len(arm), int(good.sum())
        result.update({name + "_n": n, name + "_known": known, name + "_unknown": n - known})
        if known:
            w = arm.match_weight if weighted else pd.Series(1.0, index=arm.index)
            conditional = float(np.average(values.loc[good], weights=w.loc[good]))
        else:
            conditional = None
        result[name + "_conditional_known_mean"] = conditional
        result[name + "_mean"] = conditional if n and known == n else None
    a, b = result["q1_mean"], result["comparison_mean"]
    result["contrast"] = a - b if a is not None and b is not None else None
    a, b = result["q1_conditional_known_mean"], result["comparison_conditional_known_mean"]
    result["conditional_known_contrast"] = a - b if a is not None and b is not None else None
    return result


def month_schedule(dates):
    months = sorted({str(d)[:6] for d in dates})
    if not months:
        return []
    return pd.period_range(months[0], months[-1], freq="M").strftime("%Y%m").tolist()


def block_bootstrap(series, minimum=12, replications=2000, seed=20261021):
    """Resample original scheduled positions; missing months keep their slots."""
    values = np.asarray(series, dtype=float)
    count = int(np.isfinite(values).sum())
    result = dict(status="insufficient_supported_months", supported_months=count,
                  scheduled_months=len(values), block_months=3, replications=replications,
                  seed=seed, confidence=0.95, low=None, high=None,
                  valid_replications=0, invalid_replications=0,
                  supported_month_range=[str(series.index[np.flatnonzero(np.isfinite(values))[0]]),
                                         str(series.index[np.flatnonzero(np.isfinite(values))[-1]])] if count else None)
    if count < minimum:
        return result
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, len(values), size=(replications, int(np.ceil(len(values) / 3))))
    indices = ((starts[:, :, None] + np.arange(3)) % len(values)).reshape(replications, -1)[:, :len(values)]
    draws = values[indices]
    good = np.isfinite(draws)
    totals = np.where(good, draws, 0).sum(axis=1)
    counts = good.sum(axis=1)
    means = totals[counts > 0] / counts[counts > 0]
    result.update(status="descriptive_resampling_only", low=float(np.quantile(means, .025)),
                  high=float(np.quantile(means, .975)), valid_replications=len(means),
                  invalid_replications=replications - len(means))
    return result


def quality_labels(frame):
    ordinary = pd.to_numeric(frame.denominator_pe_ttm, errors="coerce")
    deducted = pd.to_numeric(frame.denominator_pe_deducted_proxy, errors="coerce")
    same = frame.income_period.notna() & frame.income_period.eq(frame.fina_indicator_period)
    labels = pd.Series([None] * len(frame), index=frame.index, dtype=object)
    valid = same & np.isfinite(ordinary)
    labels.loc[valid & ordinary.le(0)] = "ordinary_nonpositive"
    positive = valid & ordinary.gt(0) & np.isfinite(deducted)
    labels.loc[positive & (deducted / ordinary).lt(.5)] = "deducted_share_lt_0.5"
    labels.loc[positive & (deducted / ordinary).ge(.5)] = "deducted_share_gte_0.5"
    return labels


def attach_disclosure_features(panel, statements):
    """Audit original report choices; add only predeclared leverage secondary."""
    frames = []
    for day, original in panel.groupby("formation_date", sort=True):
        block = original.copy()
        for name, source in statements.items():
            known = admitted(source, str(day), require_observed=False)
            fields = ["ts_code", "end_date", "disclosed", "observed"]
            if name == "balancesheet":
                fields += ["total_assets", "total_liab"]
            selected = known[fields].rename(columns={"end_date": name + "_period"})
            selected = selected.rename(columns={"disclosed": name + "_disclosed", "observed": name + "_observed"})
            block = block.merge(selected, on=["ts_code", name + "_period"], how="left", validate="many_to_one")
        block["leverage_bucket"] = None
        assets = pd.to_numeric(block.total_assets, errors="coerce")
        liabilities = pd.to_numeric(block.total_liab, errors="coerce")
        valid = (block.reporting_group.eq("general_reporting") & block.report_age_days.between(0, 550)
                 & block.balancesheet_disclosed.notna() & assets.gt(0)
                 & np.isfinite(assets) & np.isfinite(liabilities))
        ratio = liabilities / assets
        block["leverage_ratio"] = ratio.where(valid)
        block.loc[valid & ratio.lt(.5), "leverage_bucket"] = "liabilities_to_assets_lt_0.5"
        block.loc[valid & ratio.between(.5, 1), "leverage_bucket"] = "liabilities_to_assets_0.5_to_1"
        block.loc[valid & ratio.gt(1), "leverage_bucket"] = "liabilities_to_assets_gt_1"
        frames.append(block.drop(columns=["total_assets", "total_liab"]))
    return pd.concat(frames, ignore_index=True)


def join_members(members, outcomes):
    m = members.loc[members["group"].eq("all_market") & members.metric.isin(["pb_parent", "pe_deducted_proxy"])].copy()
    m = m.rename(columns={"ts_code": "symbol"})
    keys = ["metric", "quintile", "entry_date", "symbol"]
    if m.duplicated(keys).any() or outcomes.duplicated(keys).any():
        raise ValueError("duplicate frozen member/outcome identity")
    check = m[keys + ["formation_date"]].merge(outcomes, on=keys, how="outer", indicator=True,
                                                validate="one_to_one", suffixes=("_frozen", ""))
    if not check._merge.eq("both").all():
        raise ValueError("member/outcome coverage differs")
    if not check.formation_date.eq(check.formation_date_frozen).all():
        raise ValueError("formation does not map from original entry_date")
    return check.drop(columns=["_merge", "formation_date_frozen"])


def feature_balance(frame, comparison, weighted=False):
    rows = []
    for feature in ["size_bucket", "profitability_bucket", "log_market_value"]:
        arms = [frame.loc[frame.quintile.eq(q)] for q in [1, comparison]]
        means, variances, counts = [], [], []
        for a in arms:
            x = pd.to_numeric(a[feature], errors="coerce")
            good = np.isfinite(x)
            counts.append(int(good.sum()))
            if good.any():
                w = a.loc[good, "match_weight"] if weighted else np.ones(int(good.sum()))
                mean = float(np.average(x[good], weights=w))
                means.append(mean)
                variances.append(float(np.average((x[good] - mean) ** 2, weights=w)))
            else:
                means.append(None)
                variances.append(None)
        smd = None
        if all(v is not None for v in variances):
            scale = np.sqrt(sum(variances) / 2)
            smd = (means[0] - means[1]) / scale if scale > 0 else (0.0 if means[0] == means[1] else None)
        rows.append(dict(feature=feature, q1_available=counts[0], comparison_available=counts[1],
                         q1_mean=means[0], comparison_mean=means[1], standardized_difference=smd))
    return rows


def stability(periods, schedule):
    dimensions = ["metric", "comparison_quintile", "primary_contrast", "sample_basis", "layer", "stage", "outcome"]
    summaries = []
    for key, frame in periods.groupby(dimensions, dropna=False, sort=True):
        series = frame.set_index("formation_month").contrast.reindex(schedule).astype(float)
        good = series.dropna()
        years, leave = [], []
        for year in sorted({m[:4] for m in schedule}):
            mask = series.index.str.startswith(year)
            y, rest = series.loc[mask].dropna(), series.loc[~mask].dropna()
            years.append(dict(formation_year=year, scheduled_months=int(mask.sum()), supported_months=len(y),
                              equal_month_mean_contrast=float(y.mean()) if len(y) else None,
                              positive_month_share=float(y.gt(0).mean()) if len(y) else None,
                              full_schedule_complete=len(y) == int(mask.sum()),
                              full_schedule_mean_contrast=float(y.mean()) if len(y) == int(mask.sum()) and len(y) else None,
                              supported_month_mean_contrast=float(y.mean()) if len(y) else None,
                              missing_months=series.loc[mask & series.isna()].index.tolist(),
                              calendar_year_fully_sampled=int(mask.sum()) == 12,
                              full_calendar_year_mean_contrast=float(y.mean()) if len(y) == 12 and int(mask.sum()) == 12 else None))
            leave.append(dict(excluded_formation_year=year, supported_months=len(rest),
                              equal_month_mean_contrast=float(rest.mean()) if len(rest) else None))
        item = dict(zip(dimensions, key, strict=True))
        item.update(scheduled_months=len(series), supported_months=len(good),
                    supported_formation_months=good.index.tolist(),
                    full_schedule_complete=len(good) == len(series),
                    full_schedule_mean_contrast=float(good.mean()) if len(good) == len(series) and len(good) else None,
                    supported_month_mean_contrast=float(good.mean()) if len(good) else None,
                    missing_months=series.loc[series.isna()].index.tolist(),
                    equal_month_mean_contrast=float(good.mean()) if len(good) else None,
                    positive_month_share=float(good.gt(0).mean()) if len(good) else None,
                    q1_member_slots=int(frame.q1_n.sum()), comparison_member_slots=int(frame.comparison_n.sum()),
                    q1_unknown_slots=int(frame.q1_unknown.sum()), comparison_unknown_slots=int(frame.comparison_unknown.sum()),
                    mean_q1_retention=float(frame.q1_retention.mean()),
                    mean_comparison_retention=float(frame.comparison_retention.mean()),
                    yearly=years, leave_one_year_out=leave, bootstrap=block_bootstrap(series))
        summaries.append(item)
    return summaries


def run(args):
    pa.set_cpu_count(2)
    pa.set_io_thread_count(2)
    repo = Path(__file__).resolve().parents[1]
    out = args.output.resolve()
    if out.exists() or out.is_relative_to(repo):
        raise ValueError("new external output directory required")
    if digest(args.rules) != RULES_HASH:
        raise ValueError("frozen rules hash mismatch")
    rules = json.loads(args.rules.read_text())
    if rules["controls"]["primary_features"] != PRIMARY_FEATURES:
        raise ValueError("primary feature contract differs")
    source = json.loads((args.source_run / "receipt.json").read_text())
    attribution = json.loads((args.attribution / "receipt.json").read_text())
    if not attribution.get("reconciliation_passed") or attribution.get("rules_sha256") != RULES_HASH:
        raise ValueError("attribution has not passed frozen reconciliation")
    inputs = {}
    for directory, receipt, names in [
        (args.source_run, source, ["private_panel.parquet", "private_factor_members.parquet"]),
        (args.attribution, attribution, ["private_member_outcomes.parquet"]),
    ]:
        for name in names:
            p = directory / name
            actual = digest(p)
            if actual != receipt["outputs"][name]:
                raise ValueError("source output hash mismatch")
            inputs[str(p)] = actual
        inputs[str(directory / "receipt.json")] = digest(directory / "receipt.json")
    inputs[str(args.rules.resolve())] = RULES_HASH
    panel_columns = ["ts_code", "formation_date", "status", "income_period", "fina_indicator_period",
                     "balancesheet_period", "same_report_period", "common_five", "report_age_days",
                     "reporting_group", "size_bucket", "profitability_bucket", "stale_statement",
                     "market_value", "denominator_pe_ttm", "denominator_pe_deducted_proxy"]
    panel = pd.read_parquet(args.source_run / "private_panel.parquet", columns=panel_columns)
    if panel.duplicated(["formation_date", "ts_code"]).any():
        raise ValueError("duplicate panel identity")
    members = pd.read_parquet(args.source_run / "private_factor_members.parquet",
                              columns=["ts_code", "group", "metric", "quintile", "entry_date", "formation_date"],
                              filters=[("group", "==", "all_market"),
                                       ("metric", "in", ["pb_parent", "pe_deducted_proxy"])])
    outcomes = pd.read_parquet(args.attribution / "private_member_outcomes.parquet",
                               filters=[("scenario", "==", "touch10")])
    if not outcomes.budget_verified.all():
        raise ValueError("unverified intended budgets")
    if outcomes.loc[~outcomes.budget_positive, ["return_per_intended_budget_" + s for s in OUTCOMES.values()]].notna().any().any():
        raise ValueError("zero budget unexpectedly has a budget return")
    for suffix in OUTCOMES.values():
        failed = ~outcomes.buy_filled & outcomes.budget_positive
        if not outcomes.loc[failed, "return_per_intended_budget_" + suffix].eq(0).all():
            raise ValueError("failed buy slots lost their zero contribution")
    joined = join_members(members, outcomes)
    dates = sorted(joined.formation_date.unique())
    schedule = month_schedule(dates)
    selected_panel = panel.loc[panel.formation_date.isin(dates)].copy()
    statements = {}
    vintage = Path(source["arguments"]["vintage"])
    for name in ["income", "fina_indicator", "balancesheet"]:
        p = vintage / "normalized" / name / "data/part.parquet"
        actual = digest(p)
        if actual != source["inputs"][f"{vintage.name}/{name}/data/part.parquet"]:
            raise ValueError("financial input hash mismatch")
        inputs[str(p)] = actual
        wanted = ["ts_code", "end_date", "ann_date", "f_ann_date", "report_type", "_source_retrieved_at"]
        if name == "balancesheet":
            wanted += ["total_assets", "total_liab"]
        statements[name] = pd.read_parquet(p, columns=[c for c in wanted if c in pq.read_schema(p).names])
        observed = pd.to_datetime(statements[name]._source_retrieved_at, utc=True, errors="coerce")
        if observed.isna().any() or observed.gt(pd.Timestamp.now(tz="UTC")).any():
            raise ValueError("invalid or future observation timestamp")
    features = attach_disclosure_features(selected_panel, statements)
    features["quality_bucket"] = quality_labels(features)
    features["log_market_value"] = np.log(features.market_value)
    audit = []
    for name in statements:
        report = features[name + "_period"].notna()
        known = features[name + "_disclosed"].notna()
        bad = known & features[name + "_disclosed"].ge(pd.to_datetime(features.formation_date))
        if bad.any() or (report & ~known).any():
            raise ValueError("panel period lacks matching prior disclosure")
        audit.append(dict(table=name, selected_report_rows=int(report.sum()), matched_prior_disclosure_rows=int(known.sum()),
                          disclosure_not_before_formation=int(bad.sum()),
                          observations_after_historical_formation=int((features[name + "_observed"].dt.tz_localize(None) > pd.to_datetime(features.formation_date)).sum())))
    data = joined.merge(features.rename(columns={"ts_code": "symbol"}), on=["symbol", "formation_date"],
                        how="left", validate="many_to_one", indicator=True)
    if not data._merge.eq("both").all():
        raise ValueError("member feature identity missing")
    data = data.drop(columns="_merge")
    periods, coverage, balances, support_rows = [], [], [], []
    primaries = {(m, q) for m, _, q in rules["primary_contrasts"]}
    for (metric, day), block in data.groupby(["metric", "formation_date"], sort=True):
        for comparison in range(2, 6):
            arms = block.loc[block.quintile.isin([1, comparison])]
            base_key = dict(metric=metric, comparison_quintile=comparison,
                            primary_contrast=(metric, comparison) in primaries, formation_date=day,
                            formation_month=day[:6])
            for basis, base in [("all_frozen", arms), ("common_five", common_sample(arms))]:
                for layer, fields in LAYERS.items():
                    complete = feature_complete(base, fields)
                    overlap = match_support(base, fields, comparison, minimum=5)
                    for stage, sample in [("full_frozen", base), ("feature_complete", complete), ("overlap", overlap)]:
                        key = {**base_key, "sample_basis": basis, "layer": layer, "stage": stage}
                        weighted = stage == "overlap"
                        q1total = int(arms.quintile.eq(1).sum())
                        comptotal = int(arms.quintile.eq(comparison).sum())
                        q1n = int(sample.quintile.eq(1).sum())
                        compn = int(sample.quintile.eq(comparison).sum())
                        weights = overlap.loc[overlap.quintile.eq(1)].groupby(fields, observed=True).stratum_weight.first() if weighted else pd.Series(dtype=float)
                        support = dict(q1_retention=q1n / q1total if q1total else 0,
                                       comparison_retention=compn / comptotal if comptotal else 0,
                                       strata=len(weights), max_stratum_weight=float(weights.max()) if len(weights) else None,
                                       effective_strata=float(1 / (weights ** 2).sum()) if len(weights) else None)
                        for outcome, suffix in OUTCOMES.items():
                            periods.append({**key, **support, "outcome": outcome,
                                            **estimate(sample, "return_per_intended_budget_" + suffix, comparison, weighted)})
                        for q in [1, comparison]:
                            a = sample.loc[sample.quintile.eq(q)]
                            coverage.append({**key, "quintile": q, "members": len(a),
                                             "failed_buys": int((~a.buy_filled).sum()),
                                             "zero_budget": int((~a.budget_positive).sum()),
                                             "strict_unknown": int(a.return_per_intended_budget_strict.isna().sum()),
                                             "unknown_reporting_group": int(a.reporting_group.eq("unknown").sum()),
                                             "missing_profitability": int(a.profitability_bucket.isna().sum()),
                                             "missing_quality": int(a.quality_bucket.isna().sum()),
                                             "missing_leverage": int(a.leverage_bucket.isna().sum()),
                                             "terminal_unpriced": int(a.terminal_unpriced.sum()),
                                             "non_st": int(a.status.eq("non_st").sum()),
                                             "unknown_st_status": int(a.status.eq("unknown").sum())})
                        balances.extend([{**key, **b} for b in feature_balance(sample, comparison, weighted)])
                    if not overlap.empty:
                        support_rows.append(overlap[["symbol", "metric", "quintile", "entry_date", "formation_date",
                                                     *fields, "match_weight", "stratum_weight"]].assign(
                                                         comparison_quintile=comparison, sample_basis=basis, layer=layer))
    period = pd.DataFrame(periods)
    summaries = stability(period, schedule)
    descriptive_coverage = []
    for (day, status), b in panel.groupby(["formation_date", "status"], sort=True):
        descriptive_coverage.append(dict(formation_date=day, formation_year=day[:4], status=status, members=len(b),
                                         common_five=int(b.common_five.sum()),
                                         known_reporting=int(b.reporting_group.ne("unknown").sum()),
                                         profitability_available=int(b.profitability_bucket.notna().sum()),
                                         stale_statement=int(b.stale_statement.sum())))
    limitations = [
        "Retrospective exploration: every historical period has already been explored; no genuine holdout is admitted.",
        "Financial and reconstructed ST histories are revision_safe=false; prior announcement dates do not certify first-seen report versions.",
        "Outcomes are lifetime cohort net PnL divided by original intended slot budget, including failed buys as zero. They are not monthly traded or calendar-year returns.",
        "Zero intended budget gives an unknown budget return. Any unknown arm member makes that arm and paired complete contrast unavailable; known-only summaries condition on missing outcomes.",
        "Reference 0/50/100 are marked-value scenarios for unresolved inventory, not recovery assumptions, bounds, or certified returns.",
        "Original quintiles remain unchanged after common-five or feature selection; matching uses only formation features and never outcomes.",
        "Main size/report-type/ROE buckets are frozen panel proxies. Cumulative supplier ROE is a profitability proxy, not an independent earnings-quality certificate.",
        "Report type derives from admitted income comp_type and is not historical industry. Static 20260928 industry labels are excluded.",
        "Secondary quality requires aligned periods; secondary leverage applies only to general reporting, matching prior-announced fresh BS with finite liabilities and positive assets.",
        "Formation-calendar-year and block-resampling summaries describe previously explored history. Missing scheduled positions remain in resampling; three-month blocks do not guarantee coverage of repeated-security or cross-year holding dependence; no causal significance claim.",
        "2016-2026 panel coverage is descriptive only; member contributions retain original 36 cohorts without rerunning the ledger or expanding return windows.",
        "No simulated redistribution, matching portfolio execution, raw-share cash ledger, capacity, impact, or current trading recommendation is claimed.",
    ]
    for p, expected in inputs.items():
        if digest(p) != expected:
            raise ValueError("input changed during analysis")
    out.mkdir(parents=True, exist_ok=False)
    period.to_csv(out / "periods.csv", index=False)
    pd.DataFrame(coverage).to_csv(out / "coverage.csv", index=False)
    pd.DataFrame(balances).to_csv(out / "feature_balance.csv", index=False)
    pd.DataFrame(descriptive_coverage).to_csv(out / "historical_feature_coverage.csv", index=False)
    features.to_parquet(out / "private_formation_features.parquet", index=False)
    if support_rows:
        pd.concat(support_rows, ignore_index=True).to_parquet(out / "private_overlap_members.parquet", index=False)
    dump(out / "summaries.json", dict(schema_version="valuation_controls_summaries.v1", rows=summaries,
                                      contrast_direction="q1_minus_comparator", outcome_units="lifetime_cohort_net_pnl_per_intended_budget",
                                      schedule=schedule, genuine_holdout_admitted=False, revision_safe=False))
    dump(out / "announcement_audit.json", dict(rows=audit, revision_safe=False, actual_first_seen_pit_certified=False))
    dump(out / "limitations.json", dict(limitations=limitations))
    receipt = dict(schema_version="valuation_controls_receipt.v1", status="completed_unpublished_exploration",
                   generated_at_utc=datetime.now(timezone.utc).isoformat(), rules_sha256=RULES_HASH,
                   inputs=inputs, source_hashes={str(p.relative_to(repo)): digest(p) for p in [Path(__file__).resolve(), repo / "tests/test_grouped_valuation_controls.py", repo / "src/market_research/valuation_panel.py"]},
                   outputs={p.name: digest(p) for p in out.iterdir() if p.is_file()},
                   source_member_rows=len(data), periods=len(period), summaries=len(summaries),
                   no_backtest_rerun=True, outcome_independent_matching=True, genuine_holdout_admitted=False,
                   resource_policy=dict(threads=2, working_memory_target="512MB_to_1GB", openblas_threads=1))
    dump(out / "receipt.json", receipt)
    print(json.dumps({"status": receipt["status"], "periods": len(period), "summaries": len(summaries), "output": str(out)}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rules", type=Path, required=True)
    p.add_argument("--source-run", type=Path, required=True)
    p.add_argument("--attribution", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    run(p.parse_args())


if __name__ == "__main__":
    main()
