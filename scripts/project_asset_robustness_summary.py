"""Public allowlisted aggregates from the reviewed follow-up study."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def project(run: Path, financial: Path) -> dict:
    raw = (run / "results.json").read_bytes()
    data = json.loads(raw)
    audit_bytes = financial.read_bytes()
    audit = json.loads(audit_bytes)
    result = {
        "schema_version": 1,
        "study_id": data["study_id"],
        "as_of": "2025-12-31",
        "retrieved": "2026-10-31",
        "frequency": "monthly",
        "currency": "CNY",
        "result_sha256": hashlib.sha256(raw).hexdigest(),
        "financial_audit_sha256": hashlib.sha256(audit_bytes).hexdigest(),
        "code_hashes": data["provenance"]["code_hashes"],
        "sensitivity": data["sensitivity"],
        "waiting": {},
        "allocations": [],
        "etfs": {},
        "constituents": {},
        "financial_coverage": audit["coverage"],
        "financial_revision_safety": audit["revision_safety"],
    }
    for key, r in data["waiting"].items():
        allowed = [
            "start",
            "end",
            "relative_cagr",
            "relative_max_drawdown",
            "longest_observed_underperformance_months",
            "longest_completed_underperformance_months",
            "current_underperformance_months",
            "no_followup_entries",
            "followed_entries",
            "unrecovered_followed_entries",
        ]
        result["waiting"][key] = {k: r[k] for k in allowed}
        result["waiting"][key]["episodes"] = [
            {
                k: e[k]
                for k in [
                    "peak_date",
                    "recovery_date",
                    "observed_until",
                    "months",
                    "censored",
                    "max_drawdown",
                ]
            }
            for e in r["episodes"]
        ]
    for r in data["allocations"]:
        result["allocations"].append(
            {
                k: r[k]
                for k in [
                    "id",
                    "policy",
                    "target_weights",
                    "cost_bps_per_traded_notional",
                    "start",
                    "end",
                    "months",
                    "summary",
                ]
            }
        )
    for code, r in data["etfs"].items():
        if r["status"] != "descriptive_proxy":
            result["etfs"][code] = {"status": r["status"]}
            continue
        allowed = [
            "status",
            "start",
            "end",
            "months",
            "index_total_cagr",
            "nav_cagr",
            "market_total_proxy_cagr",
            "nav_minus_index_cagr_pp",
            "market_minus_index_cagr_pp",
            "monthly_tracking_error_annualized",
            "nav_relative_wealth_ratio",
            "premium_wealth_ratio",
            "distribution_basis_wealth_ratio",
            "market_relative_wealth_ratio",
            "geometric_reconciliation_error",
            "raw_dividend_records_in_period",
            "unique_dividend_ex_dates",
            "missing_daily_market_sessions",
            "month_end_marks_verified",
            "manager_fees_subtracted_again",
        ]
        result["etfs"][code] = {k: r[k] for k in allowed}
        result["etfs"][code]["full_history_independently_verified"] = False
    for code, r in data["constituents"].items():
        allowed = [
            "status",
            "start",
            "end",
            "snapshots",
            "initial_count",
            "final_count",
            "cohort_retained_count",
            "cohort_retained_fraction",
            "retained_initial_weight",
            "retained_final_weight",
            "weight_rounding_quantum",
            "maximum_raw_weight_sum_error",
            "measured_turnover",
            "financial_growth_attribution_status",
            "transitions",
        ]
        result["constituents"][code] = {k: r[k] for k in allowed}
    # Selected disclosed NAV returns cross-check the proxy, not the full history.
    etf = pd.read_csv(run / "512100_SH_monthly.csv").set_index("date")
    annual = float(etf.loc["2025-12-31", "adj_nav"] / etf.loc["2024-12-31", "adj_nav"] - 1)
    five = float(etf.loc["2025-12-31", "adj_nav"] / etf.loc["2020-12-31", "adj_nav"] - 1)
    if abs(annual - 0.2923) > 0.00005 or abs(five - 0.2195) > 0.00005:
        raise ValueError("selected issuer NAV checks do not reconcile at disclosed precision")
    result["issuer_crosscheck"] = {
        "code": "512100.SH",
        "source": "https://www.sse.com.cn/disclosure/fund/announcement/c/new/2026-03-31/512100_20260331_H7TX.pdf",
        "sections": ["3.1", "3.2.1"],
        "annual_2025_calculated": annual,
        "annual_2025_disclosed": 0.2923,
        "five_year_calculated": five,
        "five_year_disclosed": 0.2195,
        "full_long_window_causal_explanation_verified": False,
    }
    json.dumps(result, allow_nan=False)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--financial", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("review existing projection before replacement")
    args.output.write_text(
        json.dumps(project(args.run, args.financial), ensure_ascii=False, indent=2) + "\n"
    )
