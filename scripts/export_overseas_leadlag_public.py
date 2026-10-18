"""Project a reviewed run into aggregate-only public evidence (never daily bars)."""
import argparse
import json
from pathlib import Path


def project(data):
    if data["schema_version"] != "overseas_leadlag_reviewed.v2":
        raise ValueError("Unsupported run schema")
    if data["timing"]["future_assumed_inputs"] or data["timing"]["historical_pit_certified"]:
        raise ValueError("Unreviewed or unsupported timing claim")
    allowed = ["schema_version", "generated_at_utc", "evidence_status", "sample_end",
               "source_sha256", "timing", "etf_input_quality", "limitations"]
    result = {key: data[key] for key in allowed}
    metric_keys = ["target", "outcome", "lag_sessions", "n", "first", "last", "baseline",
                   "augmented", "baseline_hit", "augmented_hit", "mse_gain", "mse_gain_ci95",
                   "baseline_rmse_bp", "augmented_rmse_bp"]
    cost_keys = ["target", "outcome", "lag_sessions", "model", "scenario", "round_trip_bp",
                 "commission_bp", "slippage_one_way_bp", "n", "mean_daily_net_bp", "sharpe",
                 "total_return", "max_drawdown", "exposure_fraction", "one_way_trades",
                 "blocked_changes", "terminal_open_position", "cost_one_way_bp",
                 "notional_budget_yuan", "max_prior_adv_fraction"]
    result["comparisons"] = [{k: row[k] for k in metric_keys} for row in data["comparisons"]]
    result["annual"] = [{k: row[k] for k in metric_keys + ["year"]} for row in data["annual"]]
    result["costs"] = [{k: row[k] for k in cost_keys if k in row} for row in data["costs"]]
    fold_keys = ["target", "outcome", "lag_sessions", "year", "train_n", "test_n",
                 "train_end", "last_training_label_utc", "test_first_decision_utc"]
    result["folds"] = [{k: row[k] for k in fold_keys} for row in data["folds"]]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = project(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
