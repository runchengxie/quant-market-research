"""Rebuild the reviewed reader projection from three immutable aggregate sources."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

SOURCE_HASHES = {
    "manifest.json": "9638fd5f4a3edc39896ac20dcfb7e47ddb4cd0f0d861e4033a4751e82b5f543f",
    "effect_summary.csv": "3d52f7713be407752fc0dc36252fb1830f3b214a31ac4720f8314d2a65b243e4",
    "monthly_effects.csv": "f93821d03d8ac265a29cef035d55b1a26f9b32986430401aeba1b7a6c3d720d2",
}


def project(source: Path) -> dict:
    for name, expected in SOURCE_HASHES.items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"unreviewed source hash: {name}")
    with (source / "effect_summary.csv").open(encoding="utf-8") as handle:
        effects = {row["signal"]: row for row in csv.DictReader(handle)}
    with (source / "monthly_effects.csv").open(encoding="utf-8") as handle:
        monthly = list(csv.DictReader(handle))
    controls = []
    for stage in ("raw", "size", "size_lowvol", "plus_beta_value"):
        rows = [row for row in monthly if row["signal"] == stage]
        effect = effects[stage]
        if len(rows) != 86 or int(effect["count"]) != 86:
            raise ValueError("inconsistent common period count")
        controls.append({
            "id": stage,
            "low": sum(float(row["low_turnover_leg_return"]) for row in rows) / 86 * 100,
            "high": sum(float(row["high_turnover_leg_return"]) for row in rows) / 86 * 100,
            "spread": float(effect["mean"]) * 100,
            "ciLow": float(effect["bootstrap_ci_low"]) * 100,
            "ciHigh": float(effect["bootstrap_ci_high"]) * 100,
        })
    return {
        "schemaVersion": 1, "unit": "percentage_points",
        "rankingMode": "formation_signal_support_fixed_before_forward_return_filter",
        "evidenceDate": "2026-09-16", "reviewedAt": "2026-10-22",
        "formationStart": "2019-05-31", "formationEnd": "2026-06-30",
        "firstReturnEnd": "2019-06-28", "lastReturnEnd": "2026-07-31", "months": 86,
        "manifestSha256": SOURCE_HASHES["manifest.json"],
        "summarySha256": SOURCE_HASHES["effect_summary.csv"],
        "monthlySha256": SOURCE_HASHES["monthly_effects.csv"], "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(project(args.source), indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
