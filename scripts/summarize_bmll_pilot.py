"""Write provider-derived pilot results only to a caller-supplied private data directory."""

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median

import pandas as pd

from market_research.bmll_pilot import (
    annual_cost_hurdle,
    cap_bucket,
    decode_statement,
    paired_summary,
)

parser = argparse.ArgumentParser()
parser.add_argument("--input-dir", type=Path, required=True)
parser.add_argument("--features", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
parser.add_argument("--config", type=Path, default=Path("configs/bmll/pilot.json"))
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
if args.output_dir.resolve().is_relative_to(repo):
    parser.error("Provider-derived outputs must remain outside the source repository")
config = json.loads(args.config.read_text())
frames = {}
for name in ["reference", "trades", "quotes"]:
    response = json.loads((args.input_dir / f"{name}.json").read_text())
    frames[name] = decode_statement(response)
ref, trades, quotes = frames["reference"], frames["trades"], frames["quotes"]
expected = len(config["symbols"]) * (
    len(config["baseline_dates"]) + len(config["comparison_dates"])
)
if len(ref) != expected or len({(r["reference_date"], r["ticker"]) for r in ref}) != expected:
    raise ValueError("Reference identities are missing or ambiguous")
if len(quotes) != expected * len(config["windows"]):
    raise ValueError("Quote windows missing; do not silently drop empty windows")
for q in quotes:
    if not 0 <= q["fresh60_seconds"] <= q["valid_seconds"] <= q["covered_seconds"] <= 1800.001:
        raise ValueError("Invalid quote time accounting")
    if (
        not 0 <= q["bid_size_seconds"] <= q["valid_seconds"]
        or not 0 <= q["ask_size_seconds"] <= q["valid_seconds"]
    ):
        raise ValueError("Invalid displayed-size time accounting")
    q["fresh60_fraction"] = q["fresh60_seconds"] / 1800
features = pd.read_parquet(args.features)
formation = pd.Timestamp(min(config["baseline_dates"]))
features = features[
    (pd.to_datetime(features["date"]) == formation) & features.symbol.isin(config["symbols"])
]
if features.symbol.duplicated().any():
    raise ValueError("Feature join is not unique")
feature_rows = (
    features[["symbol", "market_cap_usd", "adv20_usd", "eligible"]]
    .astype(object)
    .where(pd.notna(features[["symbol", "market_cap_usd", "adv20_usd", "eligible"]]), None)
    .to_dict("records")
)
features_by_symbol = {r["symbol"]: r for r in feature_rows}
groups = {
    r["ticker"]: (
        "ETF"
        if r["instrument_type"] == "Funds"
        else cap_bucket(features_by_symbol.get(r["ticker"], {}).get("market_cap_usd"))
    )
    for r in ref
}
before, after = set(config["baseline_dates"]), set(config["comparison_dates"])
metrics = [
    "tw_spread_bps",
    "fresh60_fraction",
    "tw_best_bid_dollars",
    "bid_covers_1000_fraction",
    "bid_covers_10000_fraction",
]
paired = {m: paired_summary(quotes, m, before, after) for m in metrics}
for values in paired.values():
    for row in values:
        row["group"] = groups[row["ticker"]]
grouped = []
for group in sorted(set(groups.values())):
    values = [r for r in paired["tw_spread_bps"] if r["group"] == group]
    base = median(r["baseline"] for r in values)
    comparison = median(r["comparison"] for r in values)
    grouped.append(
        {
            "group": group,
            "securities": len(values),
            "baseline_spread_bps": base,
            "comparison_spread_bps": comparison,
            "median_paired_ratio": median(r["ratio"] for r in values),
            "annual_hurdle_scenario": {str(h): annual_cost_hurdle(base, h) for h in [1, 5, 21, 63]},
        }
    )
valid = sum(r["valid_quote_events"] for r in trades)
summary = {
    "scope": config,
    "reference_rows": len(ref),
    "quote_windows": len(quotes),
    "trade_cells": len(trades),
    "total_events": sum(r["events"] for r in trades),
    "valid_quote_events": valid,
    "unknown_direction_fraction": sum(r["unknown_direction_events"] for r in trades) / valid,
    "cancellation_events": sum(r["cancellation_events"] for r in trades),
    "groups": grouped,
    "paired": paired,
    "formation_features": feature_rows,
    "source_hashes": {
        name: hashlib.sha256((args.input_dir / f"{name}.json").read_bytes()).hexdigest()
        for name in frames
    },
}
args.output_dir.mkdir(parents=True, exist_ok=True)
(args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False))
print(
    json.dumps(
        {
            key: summary[key]
            for key in [
                "reference_rows",
                "quote_windows",
                "trade_cells",
                "total_events",
                "unknown_direction_fraction",
                "cancellation_events",
                "groups",
            ]
        },
        indent=2,
    )
)
