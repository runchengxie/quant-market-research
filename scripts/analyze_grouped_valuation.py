#!/usr/bin/env python3
"""Extend the frozen 130-date valuation panel without replacing any prior result.

Read existing owner assets only. New output root must not exist and must be
outside the repository. No network requests, collection, publication or aliases.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from analyze_valuation_panel import load_snapshot
from market_research.valuation_groups import (
    GROUPS, classify_groups, cost_sensitivity, describe_metric, factor_period, public_statistics,
    verify_legacy_values,
)
from market_research.valuation_panel import METRICS, make_panel


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    def encode(item):
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(type(item).__name__)
    path.write_text(json.dumps(value, ensure_ascii=True, allow_nan=False, default=encode,
                               separators=(",", ":")) + "\n")


def distributions(panel):
    public, minimum, tail, coverage = [], [], [], []
    for day, block in panel.groupby("formation_date", sort=True):
        coverage.append({"formation_date": day, "quoted_n": len(block),
                         **{s + "_n": int(block.status.eq(s).sum()) for s in GROUPS[1:]},
                         "unknown_reasons": block.loc[block.status.eq("unknown"), "status_reason"].value_counts().to_dict()})
        for group in GROUPS:
            selected = block if group == "all_market" else block.loc[block.status.eq(group)]
            for basis in ("metric_available", "common_five"):
                sample = selected if basis == "metric_available" else selected.loc[selected.common_five]
                for metric in METRICS:
                    key = {"formation_date": day, "group": group, "sample_basis": basis, "metric": metric}
                    stats = describe_metric(sample, metric, "denominator_" + metric)
                    public.append({**key, **public_statistics(stats)})
                    for output, rows in [(minimum, stats["minimum_records"]), (tail, stats["tail_records"])]:
                        for row in rows:
                            output.append({**key, **row, "valid_n": stats["valid_n"],
                                           "risk_flags": "|".join(stats["risk_flags"])})
    return public, minimum, tail, coverage


def factor_diagnostics(panel, prices, calendar, start, end):
    days = sorted(calendar)
    dates = sorted(panel.formation_date.unique())
    windows = []
    for formation, next_formation in zip(dates, dates[1:]):
        ix, iy = bisect.bisect_right(days, formation), bisect.bisect_right(days, next_formation)
        if max(ix, iy) >= len(days):
            continue
        entry, endpoint = days[ix], days[iy]
        if start <= entry <= end:
            windows.append((formation, entry, endpoint))
    if not windows:
        raise ValueError("no calendar-complete factor windows")
    needed = sorted({d for w in windows for d in w[1:]})
    con = duckdb.connect(":memory:")
    con.execute("SET threads=2")
    con.execute("SET memory_limit='512MB'")
    con.register("needed", pd.DataFrame({"trade_date": needed}))
    columns = "ts_code,trade_date,adj_close,amount,is_suspended,is_limit_up,is_limit_down"
    price = con.execute(f"SELECT {columns} FROM read_parquet(?) JOIN needed USING(trade_date)",
                        [str(prices / "data/*.parquet")]).fetchdf()
    if set(price.trade_date) != set(needed) or price.duplicated(["ts_code", "trade_date"]).any():
        raise ValueError("price endpoint dates/identities differ from the frozen calendar")
    marks = dict(tuple(price.groupby("trade_date", sort=False)))
    formations = dict(tuple(panel.groupby("formation_date", sort=False)))
    periods, selections = [], []
    previous = {}
    for window_ix, (day, entry, endpoint) in enumerate(windows):
        block = formations[day]
        for group in GROUPS[:-1]:
            group_rows = block if group == "all_market" else block.loc[block.status.eq(group)]
            # An explicit historical listing interval is required for return diagnostics.
            alive = group_rows.list_date.notna() & group_rows.list_date.le(day)
            alive &= group_rows.delist_date.isna() | group_rows.delist_date.gt(day)
            group_rows = group_rows.loc[alive]
            for metric in METRICS:
                result, audit = factor_period(group_rows, marks[entry], marks[endpoint], metric=metric)
                key = {"formation_date": day, "entry_date": entry, "endpoint_date": endpoint,
                       "group": group, "metric": metric, "sample_basis": "metric_available",
                       "unknown_status_in_signal_n": int(group_rows.status.eq("unknown").sum())}
                for q in result["quintiles"]:
                    state_key = (group, metric, q["quintile"])
                    if q["complete"]:
                        members = audit.loc[audit.quintile.eq(q["quintile"])]
                        target = {c: 1 / len(members) for c in members.ts_code}
                        prior = previous.get(state_key, {} if window_ix == 0 else None)
                        q.update(cost_sensitivity(target, prior, q["gross_return"],
                                                  liquidate=window_ix == len(windows) - 1))
                        previous[state_key] = {
                            row.ts_code: (1 + row.forward_return) / len(members) / (1 + q["gross_return"])
                            for row in members.itertuples()
                        }
                    else:
                        previous[state_key] = None
                        q.update(traded_notional=None, net_sensitivity={"0": None, "10": None, "30": None})
                periods.append({**key, **result})
                selections.append(audit.assign(**key))
        print("factor_window", day, entry, endpoint, flush=True)
    private_members = pd.concat(selections, ignore_index=True)
    summaries = []
    for group in GROUPS[:-1]:
        for metric in METRICS:
            rows = [x for x in periods if x["group"] == group and x["metric"] == metric]
            ic = pd.Series([x["rank_ic"] for x in rows], dtype=float).dropna()
            spread = pd.Series([x["cheap_minus_expensive"] for x in rows], dtype=float).dropna()
            item = {"group": group, "metric": metric, "attempted_months": len(rows),
                    "ic_months": len(ic), "mean_rank_ic": float(ic.mean()) if len(ic) else None,
                    "rank_icir_annualized": float(ic.mean() / ic.std(ddof=1) * np.sqrt(12)) if len(ic) >= 6 and ic.std(ddof=1) > 0 else None,
                    "paired_tail_months": len(spread), "mean_cheap_minus_expensive": float(spread.mean()) if len(spread) else None,
                    "quintiles": []}
            for quintile in range(1, 6):
                qs = [x["quintiles"][quintile - 1] for x in rows]
                valid = [q["gross_return"] for q in qs if q["gross_return"] is not None]
                costs = {}
                for bps in ("0", "10", "30"):
                    values = [q["net_sensitivity"][bps] for q in qs if q["net_sensitivity"][bps] is not None]
                    costs[bps] = {"months": len(values), "mean_monthly_return": float(np.mean(values)) if values else None}
                traded = [q["traded_notional"] for q in qs if q["traded_notional"] is not None]
                item["quintiles"].append({"quintile": quintile, "complete_months": len(valid),
                                           "mean_gross_monthly_return": float(np.mean(valid)) if valid else None,
                                           "mean_traded_notional": float(np.mean(traded)) if traded else None,
                                           "cost_sensitivity": costs})
            summaries.append(item)
    return periods, summaries, private_members, windows


def run(args):
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(repo):
        raise ValueError("output must be new and outside the repository")
    if args.factor_start > args.factor_end:
        raise ValueError("invalid factor window")
    source_files = [args.baseline_panel, args.baseline_summary, args.namechange, args.instruments,
                    args.st_history, args.calendar, args.daily_clean / "manifest.yml"]
    hashes = {str(p.resolve()): digest(p) for p in source_files}
    baseline_meta = json.loads(args.baseline_summary.read_text())
    baseline = pd.read_parquet(args.baseline_panel)
    if baseline.duplicated(["formation_date", "ts_code"]).any():
        raise ValueError("ambiguous baseline panel")
    financial_hashes = {}
    statements = load_snapshot(args.vintage, financial_hashes)
    for name, actual in financial_hashes.items():
        if baseline_meta["input_sha256"].get(name) != actual:
            raise ValueError("financial inputs differ from the frozen baseline")
    hashes.update(financial_hashes)
    panels = []
    for day, old in baseline.groupby("formation_date", sort=True):
        path = args.daily_basic / "data" / f"trade_date={day}" / "part.parquet"
        actual = digest(path)
        if actual != baseline_meta["input_sha256"]["daily_basic/" + day]:
            raise ValueError("daily-basic partition differs from frozen baseline")
        hashes[str(path.resolve())] = actual
        price = pq.ParquetFile(path).read(columns=["ts_code", "trade_date", "total_mv"]).to_pandas()
        current = make_panel(statements, price, day, require_observed=False, private_denominators=True)
        verify_legacy_values(current, old)
        panels.append(current)
        print("formation_verified", day, len(current), flush=True)
    private = pd.concat(panels, ignore_index=True)
    instruments = pd.read_parquet(args.instruments, columns=["ts_code", "list_date", "delist_date"])
    if instruments.ts_code.duplicated().any():
        raise ValueError("ambiguous instrument identity")
    instruments = instruments.replace({"None": None, "": None})
    private = private.merge(instruments, on="ts_code", how="left", validate="many_to_one")
    private = classify_groups(private, pd.read_parquet(args.namechange), pd.read_parquet(args.st_history))
    aggregate, minimum, tail, coverage = distributions(private)
    # Keep a concrete first-layer deliverable even if return inputs fail later.
    output.mkdir(parents=True, exist_ok=False)
    private.to_parquet(output / "private_panel.parquet", index=False)
    pd.DataFrame(minimum).to_csv(output / "private_minimum_audit.csv", index=False)
    pd.DataFrame(tail).to_csv(output / "private_low_valuation_tail.csv", index=False)
    pd.DataFrame(aggregate).to_csv(output / "distribution_statistics.csv", index=False)
    write_json(output / "distribution_aggregate_draft.json", {
        "schema_version": "grouped_valuation_distributions.v1", "status": "completed_unpublished_draft",
        "financial_revision_safe": False, "st_revision_safe": False,
        "panel_records": len(private), "formation_count": private.formation_date.nunique(),
        "coverage": coverage, "distributions": aggregate})
    write_json(output / "phase1_receipt.json", {"status": "distributions_completed_factor_pending",
        "inputs": hashes, "outputs": {p.name: digest(p) for p in output.iterdir()}})
    print("distribution_checkpoint", str(output), len(aggregate), json.dumps(coverage[-1]), flush=True)
    calendar = pd.read_parquet(args.calendar)
    days = calendar.loc[calendar.exchange.eq("SSE") & calendar.is_open.eq(1), "cal_date"].astype(str).tolist()
    periods, summaries, members, windows = factor_diagnostics(
        private, args.daily_clean, days, args.factor_start, args.factor_end)
    # Detect aliases/source changes during the run before any result is written.
    for path, expected in [(p, hashes[str(p.resolve())]) for p in source_files]:
        if digest(path) != expected:
            raise ValueError("source changed during research run")
    members.to_parquet(output / "private_factor_members.parquet", index=False)
    write_json(output / "factor_periods.json", periods)
    public = {"schema_version": "grouped_valuation_exploration.v1",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_status": "unpublished_draft_retrospective_exploration",
              "historical_pit_certified": False, "financial_revision_safe": False,
              "st_revision_safe": False, "executable_returns_certified": False,
              "original_baseline_reproduced": True, "panel_records": len(private),
              "formation_count": private.formation_date.nunique(), "groups": list(GROUPS),
              "metrics": METRICS, "coverage": coverage, "distributions": aggregate,
              "factor_window": {"entry_start": windows[0][1], "last_endpoint": windows[-1][2],
                                "formations": len(windows), "sample_basis": "metric_available"},
              "factor_summaries": summaries,
              "definitions": {"equal_weight_mean": "arithmetic mean of positive valid per-security multiples",
                              "ratio_of_totals": "sum(market_value)/sum(denominator) over the identical positive valid set; not a market-cap-weighted mean",
                              "rank_ic": "Spearman(-multiple, next-session-close to next-formation-next-session-close adjusted-price return), conditional on resolved endpoints; >=25 signals, >=10 outcomes",
                              "quintiles": "rank ascending multiple; average-rank ties kept together; equal initial weights, fixed shares within the month; incomplete basket unavailable",
                              "cost": "additive 0/10/30 bp per traded notional; L1 target minus previous drifted weights; cash only initially, no reset after missing marks; terminal liquidation included; no fill/cash-ledger certification",
                              "status": "known prior-announced active name plus listing interval and matching reconstructed positive state; *ST before ST; absence alone never establishes non-ST",
                              "all_market": "all quoted positive-market-value rows, including unknown status; return diagnostics additionally require a listing interval; not independently complete exchange membership"},
              "limitations": ["financial_revision_safe_false", "st_reconstructed_pit_revision_safe_false",
                              "frozen_20261018_financial_template_baseline_not_repaired",
                              "parent_equity_minus_consolidated_assets_proxy_preferred_and_multiclass_scope_uncertified",
                              "conditional_rank_ic_selection_missing_outcomes", "endpoint_flags_only_no_intramonth_execution_replay",
                              "adjusted_price_proxy_no_corporate_action_cash_ledger", "no_borrow_or_capacity_claim",
                              "no_zero_fill_no_terminal_settlement_imputation", "means_and_cost_scenarios_use_different_complete_month_support",
                              "historical_exploration_not_untouched_out_of_sample", "private_security_and_denominator_audits_not_in_public_projection"]}
    write_json(output / "public_aggregate_draft.json", public)
    sources = [Path(__file__), repo / "src/market_research/valuation_groups.py", repo / "src/market_research/valuation_panel.py"]
    receipt = {"schema_version": "grouped_valuation_run_receipt.v1", "status": "completed_unpublished_draft",
               "generated_at_utc": public["generated_at_utc"], "inputs": hashes,
               "source_sha256": {str(p.relative_to(repo)): digest(p) for p in sources},
               "arguments": {k: str(v) for k, v in vars(args).items()},
               "resources": {"duckdb_threads": 2, "duckdb_memory": "512MB", "blas_threads": os.environ.get("OPENBLAS_NUM_THREADS")},
               "outputs": {p.name: digest(p) for p in output.iterdir()}}
    write_json(output / "receipt.json", receipt)
    print(json.dumps({"output": str(output), "records": len(private), "formations": public["formation_count"],
                      "distribution_rows": len(aggregate), "factor_periods": len(periods), "coverage_latest": coverage[-1]}), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["baseline-panel", "baseline-summary", "vintage", "daily-basic", "namechange", "instruments",
                 "st-history", "daily-clean", "calendar", "output"]:
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--factor-start", default="20230101")
    p.add_argument("--factor-end", default="20251231")
    run(p.parse_args())
