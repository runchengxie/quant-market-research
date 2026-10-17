"""Publish only reviewed aggregate fields; never copy private provenance locators."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ARMS = (
    "ideal_one_day", "retry_tradable_unlimited", "same_day_capacity",
    "same_day_capacity_lots", "same_day_capacity_lots_t1",
    "same_day_capacity_lots_t1_limits", "prior20_budget", "prior20_budget_realized_guard",
)
METRICS = ("net_annual_return", "net_max_drawdown", "net_sharpe", "fill_ratio", "avg_cash_weight",
           "fills_over_5pct_realized_amount")


def project(rows, support, coverage, ledger, trace):
    if len(rows) != len(ARMS) or {row["arm"] for row in rows} != set(ARMS):
        raise ValueError("expected exactly the approved execution arms")
    if coverage["status"] != "completed" or trace["closed_original_runtime_gap"]:
        raise ValueError("review scope or historical-runtime status changed")
    if support["signal_checks"]["raw_max_abs_error"] != 0:
        raise ValueError("shared raw means do not reconcile")
    execution = []
    for arm in ARMS:
        row = next(row for row in rows if row["arm"] == arm)
        values = {key: float(row[key]) if row.get(key) not in (None, "") else None for key in METRICS}
        if any(value is not None and not math.isfinite(value) for value in values.values()):
            raise ValueError("nonfinite public metric")
        execution.append({"id": arm, **values})
    coverage_rows = {}
    for minimum in ("45", "90"):
        source = coverage["target_summary"][minimum]
        fields = ("names", "stock_months", "queried_names", "unqueried_names", "unqueried_stock_months")
        coverage_rows[minimum] = {key: source[key] for key in fields}
        coverage_rows[minimum]["positive_share_rows_missing_listing_date"] = source[
            "implemented_ex_date_field_audit"]["stock_positive_missing_listing_date"]
    return {
        "schema_version": 1, "reviewed_on": "2026-10-17",
        "sample": {"start": "2015-03-02", "end": "2026-07-31", "sessions": 2778,
                   "capital_cny": 100_000_000, "fee_bps": 10,
                   "adjusted_share_scenarios": True, "raw_share_readiness": False},
        "accounting": {"synthetic_max_daily_error": ledger["synthetic_accounting_identity"]["max_daily_abs_difference"]},
        "support": {key: {field: support[key][field] for field in ("formations", "different", "different_2016plus")}
                    for key in ("support_no_buffer", "support_buffer", "shared_scores_no_buffer",
                                "shared_scores_buffer", "coverage_s45_b40", "coverage_s45_b60")},
        "signal_checks": {key: support["signal_checks"][key] for key in (
            "common_rows", "raw_max_abs_error", "identical_input_score_max_abs_error")},
        "execution": execution, "action_coverage": coverage_rows,
        "history": {"inspection_records": len(trace["records"]), "original_runtime_recovered": False},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("ladder", "support", "coverage", "ledger-review", "trace", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    def load(path):
        return json.loads(path.read_text())
    if load(args.ladder / "receipt.json")["status"] != "completed":
        raise ValueError("incomplete execution ladder")
    if load(args.support / "receipt.json")["status"] != "completed":
        raise ValueError("incomplete support ablation")
    with (args.ladder / "metrics.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    data = project(rows, load(args.support / "summary.json"), load(args.coverage),
                   load(args.ledger_review), load(args.trace))
    sources = {"execution_metrics": args.ladder / "metrics.csv", "execution_receipt": args.ladder / "receipt.json",
               "support_summary": args.support / "summary.json", "support_receipt": args.support / "receipt.json",
               "action_coverage": args.coverage, "accounting_review": args.ledger_review,
               "historical_trace": args.trace}
    data["source_hashes"] = {role: hashlib.sha256(path.read_bytes()).hexdigest() for role,path in sources.items()}
    args.output.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
