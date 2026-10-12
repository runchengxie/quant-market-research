"""Validate canonical private orders and emit research-only aggregate calibration."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from market_research.studies.ashare_execution_costs.calibration import (
    measure_orders,
    chronological_validation,
    public_calibration,
)


def run(input_root: Path, output_root: Path, *, max_quote_age_ms=1000, min_group_orders=20):
    if min_group_orders < 20:
        raise ValueError("public group minimum is twenty orders")
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError("output must be new or empty; previous runs are retained")
    manifest_path = input_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema_version") != "ashare_execution_costs.canonical_orders.v1":
        raise ValueError("unreviewed canonical input schema")
    if manifest.get("price_unit") != "CNY" or manifest.get("quantity_unit") != "share":
        raise ValueError("canonical price/quantity units required")
    if manifest.get("time_contract") != "explicit_UTC_offset" or not manifest.get("source"):
        raise ValueError("source and explicit timestamp contract required")
    if manifest.get("fees_contract") != "actual_parent_total_CNY_once":
        raise ValueError("parent total fees must be supplied once")
    frames, hashes = {}, {"manifest": hashlib.sha256(manifest_path.read_bytes()).hexdigest()}
    for name in ("orders", "fills", "quotes"):
        files = [input_root / (name + suffix) for suffix in (".csv", ".parquet")]
        present = [path for path in files if path.exists()]
        if len(present) != 1:
            raise ValueError("exactly one CSV or Parquet per canonical input required")
        path = present[0]
        frames[name] = (
            pd.read_parquet(path)
            if path.suffix == ".parquet"
            else pd.read_csv(
                path, dtype={key: str for key in ("symbol", "parent_order_id", "fill_id")}
            )
        )
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if frames["orders"].empty:
        raise ValueError("empty order source")
    measured = measure_orders(
        frames["orders"],
        frames["fills"],
        frames["quotes"],
        data_kind=manifest["data_kind"],
        max_quote_age_ms=max_quote_age_ms,
    )
    validation = chronological_validation(measured)
    public = public_calibration(measured, validation, min_group_orders=min_group_orders)
    public["source_sha256"] = hashes
    public["definitions"] = {
        "benchmarks": "past_available_midpoints_only_with_declared_freshness",
        "max_quote_age_ms": max_quote_age_ms,
        "fees": "actual_parent_total_CNY_once",
        "unfilled": "terminal_midpoint_opportunity_cost_preserved",
        "response": "signed_log_mid_return_from_terminal_time_to_horizon_minus_market_log_return",
        "response_causal": False,
        "min_group_orders": min_group_orders,
        "validation": "whole_UTC_arrival_dates_training_side_median_later_holdout",
        "source_provenance": "operator_declared_not_broker_authenticated",
    }
    output_root.mkdir(parents=True, exist_ok=True)
    measured.to_parquet(output_root / "private-order-measurements.parquet", index=False)
    (output_root / "private-validation.json").write_text(
        json.dumps(validation, indent=2, allow_nan=False) + "\n"
    )
    (output_root / "aggregate.json").write_text(
        json.dumps(public, indent=2, allow_nan=False) + "\n"
    )
    receipt = {
        "input_sha256": hashes,
        "measurement_code_sha256": hashlib.sha256(
            Path(
                __import__(
                    "market_research.studies.ashare_execution_costs.calibration", fromlist=[""]
                ).__file__
            ).read_bytes()
        ).hexdigest(),
        "runner_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "data_kind": manifest["data_kind"],
        "source": manifest["source"],
        "output_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in output_root.iterdir()
        },
    }
    (output_root / "private-receipt.json").write_text(
        json.dumps(receipt, indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "orders": len(measured),
                "eligible_orders": int(measured.calibration_eligible.sum()),
                "data_kind": manifest["data_kind"],
                "validation": validation["status"],
                "actual_order_calibrated": public["actual_order_calibrated"],
            }
        )
    )
    return public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--max-quote-age-ms", type=int, default=1000)
    parser.add_argument("--min-group-orders", type=int, default=20)
    args = parser.parse_args()
    run(
        args.input_root,
        args.output_root,
        max_quote_age_ms=args.max_quote_age_ms,
        min_group_orders=args.min_group_orders,
    )


if __name__ == "__main__":
    main()
