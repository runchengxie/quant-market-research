"""Project explicit derived statistics for review; never copies raw supplier data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


_METRICS = (
    "start",
    "end",
    "observations",
    "total_return",
    "cagr",
    "daily_volatility_252",
    "max_drawdown",
)
_PRIMARY = "H00300.CSI__NHCI.NH"


def _stats(row: dict) -> dict:
    return {key: row[key] for key in _METRICS}


def _analysis(pair: dict | None) -> dict | None:
    if not pair or pair["audit"]["eligible"] is not True or "analysis" not in pair:
        return None
    data = pair["analysis"]
    return {
        "daily": {c: _stats(data["daily"][c]) for c in ["equity", "commodity"]},
        "holding_periods": data.get("holding_periods", {}),
        "monthly_max_drawdown": data.get("monthly_max_drawdown", {}),
        "correlation": data.get("diversification", {}).get("correlation", {}),
        "down_equity_months": data.get("diversification", {}).get("down_market", {}),
        "period_returns": data.get("recent_periods", {}),
        "calendar_year_returns": data.get("calendar_year_returns", []),
    }


def project(full: dict, baseline: dict, recent: dict) -> dict:
    primary_pair = baseline["comparisons"].get(_PRIMARY)
    primary = _analysis(primary_pair)
    allocations = []
    if primary:
        allocations = [
            {
                **_stats(row),
                **{
                    key: row[key]
                    for key in [
                        "commodity_weight",
                        "rebalance",
                        "annual_wealth_drag_bps",
                        "calibrated_cost",
                        "holding_periods",
                    ]
                },
            }
            for row in primary_pair["analysis"]["allocation"]
        ]
    sectors = {
        pair["commodity"]: _analysis(pair)
        for pair in baseline["comparisons"].values()
        if pair["equity"] == "H00300.CSI"
    }
    return {
        "schema_version": 1,
        "study_id": "china_commodity_equity",
        "evidence_stage": "descriptive_index_history",
        "primary": primary,
        "allocations": allocations,
        "sectors": sectors,
        "recent": _analysis(recent["comparisons"].get(_PRIMARY)),
        "full_history_audits": {
            key: row["audit"]
            for key, row in full["comparisons"].items()
            if row["commodity"] == "NHCI.NH"
        },
        "observed_coverage": baseline["coverage"],
        "source_revision": baseline["source_revision"],
        "run_manifest_sha256": {
            name: data["manifest_sha256"]
            for name, data in [("full", full), ("baseline", baseline), ("recent", recent)]
        },
        "limitations": [
            "Coverage-limited baseline starts 2006-12-29; full earlier history remains blocked.",
            "Commodity sectors have different observed inception dates; no common sector ranking.",
            "Fixed-weight index scenarios omit collateral interest and calibrated trading costs.",
            "Point checks do not certify complete vendor history or annual-return conventions.",
            "Current methodology has conflicting roll periods; historical versions remain unresolved.",
            "No raw redistribution permission is asserted; only reviewed derived statistics are projected.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["full", "baseline", "recent", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    paths = {name: getattr(args, name) for name in ["full", "baseline", "recent"]}
    result = project(*(json.loads(paths[name].read_text()) for name in paths))
    result["run_result_sha256"] = {
        name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()
    }
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    with args.output.open("x") as stream:
        stream.write(text)


if __name__ == "__main__":
    main()
