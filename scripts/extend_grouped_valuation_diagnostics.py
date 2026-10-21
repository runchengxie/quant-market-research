#!/usr/bin/env python3
"""Bounded follow-up diagnostics on existing retained valuation evidence only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


METRICS = [
    "pe_ttm",
    "pe_deducted_proxy",
    "pb_parent",
    "pb_ex_goodwill_proxy",
    "pb_ex_intangibles_proxy",
]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2, allow_nan=False) + "\n")


def historical_labels(panel, metric):
    """Only prior 12 scheduled snapshots; missing dates do not compress history."""
    dates = sorted(panel.formation_date.unique())
    clean = panel.loc[panel.status.eq("non_st")].copy()
    values = clean.pivot(index="formation_date", columns="ts_code", values=metric).reindex(dates)
    valid = values.gt(0) & np.isfinite(values)
    cheap = np.ceil(values.where(valid).rank(axis=1, method="average", pct=True) * 5).eq(1)
    prior_valid = valid.astype(int).rolling(12, min_periods=12).sum().shift(1)
    prior_cheap = cheap.astype(int).rolling(12, min_periods=12).sum().shift(1)
    frames = []
    for day in dates:
        names = values.columns[cheap.loc[day]]
        known = prior_valid.loc[day, names].fillna(0)
        count = prior_cheap.loc[day, names].fillna(0)
        label = np.select(
            [known.lt(10), count.ge(8), count.le(1)],
            ["history_insufficient", "persistent_cheap", "one_off_cheap"],
            default="other_cheap",
        )
        frames.append(
            pd.DataFrame(
                {
                    "formation_date": day,
                    "ts_code": names,
                    "condition": label,
                    "prior_valid_12": known.values,
                    "prior_cheap_12": count.values,
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    out = args.output.resolve()
    if out.exists() or out.is_relative_to(repo):
        raise ValueError("new external output required")
    receipt_path = args.source_run / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    panel_path = args.source_run / "private_panel.parquet"
    members_path = args.source_run / "private_factor_members.parquet"
    for path in [panel_path, members_path]:
        if digest(path) != receipt["outputs"][path.name]:
            raise ValueError("source hash mismatch")
    instruments_path = Path(receipt["arguments"]["instruments"])
    if digest(instruments_path) != receipt["inputs"][str(instruments_path)]:
        raise ValueError("instrument snapshot hash mismatch")
    inputs = {str(p): digest(p) for p in [receipt_path, panel_path, members_path, instruments_path]}
    panel = pd.read_parquet(panel_path)
    members = pd.read_parquet(
        members_path,
        columns=[
            "ts_code",
            "formation_date",
            "entry_date",
            "endpoint_date",
            "group",
            "metric",
            "quintile",
            "resolved",
            "forward_return",
        ],
    )
    instruments = pd.read_parquet(instruments_path, columns=["ts_code", "industry"])
    if instruments.ts_code.duplicated().any():
        raise ValueError("duplicate instrument labels")
    panel = panel.merge(instruments, on="ts_code", how="left", validate="many_to_one")
    panel["industry_snapshot_proxy"] = panel.industry.fillna("unknown")
    out.mkdir(parents=True)
    all_periods = []
    label_frames = []
    for metric in ["pb_parent", "pe_deducted_proxy"]:
        labels = historical_labels(panel, metric)
        original = members.loc[
            members["group"].eq("non_st") & members.metric.eq(metric) & members.quintile.eq(1)
        ]
        sample = original.merge(
            labels, on=["formation_date", "ts_code"], how="left", validate="one_to_one"
        )
        if sample.condition.isna().any():
            raise ValueError("historical cheap rank differs from frozen non-ST quintile")
        label_frames.append(sample)
        for (day, label), block in sample.groupby(["formation_date", "condition"]):
            observed = block.loc[block.resolved, "forward_return"]
            all_periods.append(
                dict(
                    metric=metric,
                    formation_date=day,
                    condition=label,
                    original_members=len(block),
                    endpoint_resolved=len(observed),
                    unresolved=len(block) - len(observed),
                    conditional_mean=float(observed.mean()) if len(observed) else None,
                    conditional_median=float(observed.median()) if len(observed) else None,
                )
            )
    labels = pd.concat(label_frames, ignore_index=True)
    labels.to_parquet(out / "private_condition_members.parquet", index=False)
    period = pd.DataFrame(all_periods)
    period.to_csv(out / "condition_periods.csv", index=False)
    condition = []
    for (metric, label), block in period.groupby(["metric", "condition"]):
        condition.append(
            dict(
                metric=metric,
                condition=label,
                months=len(block),
                stock_months=int(block.original_members.sum()),
                endpoint_resolved=int(block.endpoint_resolved.sum()),
                unresolved=int(block.unresolved.sum()),
                equal_month_conditional_mean=float(block.conditional_mean.mean()),
                months_with_at_least_20=int(block.original_members.ge(20).sum()),
            )
        )
    dump(
        out / "conditions.json",
        dict(
            definition="current non-ST cheapest quintile; prior 12 scheduled snapshots, >=10 positive usable observations; persistent >=8 prior cheap, one-off <=1 prior cheap",
            revision_safe=False,
            retrospective_exploration=True,
            endpoint_selection_conditioned=True,
            not_executable_returns=True,
            rows=condition,
        ),
    )
    # Coverage and strata retain all quoted observations in denominators.
    coverage = []
    strata = []
    year_ends = panel.groupby(panel.formation_date.str[:4]).formation_date.max().tolist()
    for day, block in panel.groupby("formation_date"):
        for metric in METRICS:
            for status, b in [("all_market", block), *list(block.groupby("status"))]:
                available = b[metric].gt(0) & np.isfinite(b[metric])
                coverage.append(
                    dict(
                        date=day,
                        status=status,
                        metric=metric,
                        quoted=len(b),
                        valid=int(available.sum()),
                        nonpositive=int(b[metric + "_nonpositive"].sum()),
                        missing_other=int((~available & ~b[metric + "_nonpositive"]).sum()),
                        common_five=int(b.common_five.sum()),
                        median=float(b.loc[available, metric].median())
                        if available.any()
                        else None,
                    )
                )
        if day in year_ends:
            for dimension in ["reporting_group", "size_bucket", "industry_snapshot_proxy"]:
                for label, b in block.loc[block.status.eq("non_st")].groupby(dimension):
                    for metric in ["pe_deducted_proxy", "pb_parent", "pb_ex_intangibles_proxy"]:
                        x = b.loc[b[metric].gt(0) & np.isfinite(b[metric]), metric]
                        strata.append(
                            dict(
                                date=day,
                                dimension=dimension,
                                stratum=str(label),
                                metric=metric,
                                quoted=len(b),
                                valid=len(x),
                                median=float(x.median()) if len(x) else None,
                                p05=float(x.quantile(0.05)) if len(x) else None,
                                small_sample=len(x) < 20,
                                industry_is_current_snapshot_proxy=True,
                            )
                        )
    pd.DataFrame(coverage).to_csv(out / "coverage_all_dates.csv", index=False)
    pd.DataFrame(strata).to_csv(out / "annual_strata.csv", index=False)
    # Explicitly descriptive matched-name comparisons, not a historical investable universe.
    latest = panel.formation_date.max()
    comparison = []
    for old in year_ends[:-1]:
        a = panel.loc[panel.formation_date.eq(old) & panel.status.eq("non_st")].set_index("ts_code")
        b = panel.loc[panel.formation_date.eq(latest) & panel.status.eq("non_st")].set_index(
            "ts_code"
        )
        common = a.index.intersection(b.index)
        for metric in ["pb_parent", "pe_deducted_proxy"]:
            aa = a.loc[common, metric]
            bb = b.loc[common, metric]
            good = aa.gt(0) & bb.gt(0) & np.isfinite(aa) & np.isfinite(bb)
            comparison.append(
                dict(
                    earlier=old,
                    later=latest,
                    metric=metric,
                    matched_positive_names=int(good.sum()),
                    earlier_median=float(aa[good].median()),
                    later_median=float(bb[good].median()),
                    median_within_name_ratio=float((bb[good] / aa[good]).median()),
                    later_selection_survivorship_bias=True,
                )
            )
    pd.DataFrame(comparison).to_csv(out / "matched_name_descriptive_comparison.csv", index=False)
    cases = []
    selections = [
        (
            "latest_minimum_pb",
            panel.loc[panel.formation_date.eq(latest) & panel.pb_parent.gt(0)],
            "pb_parent",
        ),
        (
            "historical_non_st_minimum_pb",
            panel.loc[
                panel.status.eq("non_st")
                & panel.pb_parent.gt(0)
                & panel.formation_date.lt("20260101")
            ],
            "pb_parent",
        ),
        (
            "positive_pe_nonpositive_deducted",
            panel.loc[
                panel.pe_ttm.gt(0)
                & panel.pe_deducted_proxy_nonpositive
                & panel.formation_date.ge("20230101")
            ],
            "pe_ttm",
        ),
    ]
    for kind, subset, metric in selections:
        row = subset.sort_values([metric, "formation_date", "ts_code"]).iloc[0]
        cases.append(
            dict(
                case=kind,
                ts_code=row.ts_code,
                date=row.formation_date,
                status=row.status,
                status_reason=row.status_reason,
                metric=metric,
                multiple=float(row[metric]),
                market_value=float(row.market_value),
                denominator=float(row["denominator_" + metric]),
                reporting_group=row.reporting_group,
                size_bucket=int(row.size_bucket),
                industry_snapshot_proxy=row.industry_snapshot_proxy,
                income_period=row.income_period,
                balancesheet_period=row.balancesheet_period,
                explanation_status="Numerical case only; no causal announcement investigation completed.",
            )
        )
    dump(out / "private_cases.json", cases)
    panel.loc[panel.ts_code.isin([c["ts_code"] for c in cases])].to_parquet(
        out / "private_case_timelines.parquet", index=False
    )
    dump(
        out / "limitations.json",
        dict(
            revision_safe=False,
            raw_share_ready=False,
            financial_history_not_repaired=True,
            st_small_sample_warning=True,
            industry_labels="2026-09-28 static snapshot, not point-in-time sector histories",
            headline="Coverage and membership changes prevent a whole-market cheapness conclusion from raw minima.",
            cases="Extreme-value identities and supplier amounts stay private; no causal claims.",
            condition_returns="Existing endpoint-supported adjusted-price returns only, selection conditioned; not new ledger returns.",
        ),
    )
    for path, sha in inputs.items():
        if digest(path) != sha:
            raise ValueError("input changed during diagnostics")
    dump(
        out / "receipt.json",
        dict(
            status="completed_unpublished_exploratory_diagnostics",
            inputs=inputs,
            source_sha256=digest(__file__),
            outputs={str(p.relative_to(out)): digest(p) for p in out.iterdir() if p.is_file()},
        ),
    )
    print(
        json.dumps(
            dict(
                output=str(out),
                condition_rows=len(condition),
                coverage_rows=len(coverage),
                stratum_rows=len(strata),
                cases=len(cases),
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
