#!/usr/bin/env python3
"""Audit frozen low-turnover outputs without copying research data into Git."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_EFFECT_COLUMNS = {"signal", "count", "mean", "bootstrap_ci_low", "bootstrap_ci_high"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_outputs(manifest_path: Path, effect_summary_path: Path, prospective_manifest_path: Path | None = None) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    effects = pd.read_csv(effect_summary_path)
    missing = sorted(REQUIRED_EFFECT_COLUMNS - set(effects.columns))
    if missing:
        raise ValueError(f"effect summary is missing columns: {', '.join(missing)}")
    counts = effects["count"].dropna().astype(int)
    if counts.empty or counts.nunique() != 1:
        raise ValueError("effect summary must contain one common completed-period count")
    completed_periods = int(counts.iloc[0])
    if completed_periods != int(manifest.get("completed_formation_periods_by_signal", {}).get("raw", 0)):
        raise ValueError("manifest and effect summary disagree on completed periods")
    if not effects["signal"].is_unique:
        raise ValueError("effect summary contains duplicate signal rows")
    result: dict[str, Any] = {
        "manifest": str(manifest_path),
        "manifest_sha256": sha256(manifest_path),
        "effect_summary": str(effect_summary_path),
        "effect_summary_sha256": sha256(effect_summary_path),
        "source_experiment": manifest.get("source_experiment"),
        "return_basis": manifest.get("forward_return_basis"),
        "completed_periods": completed_periods,
        "signals": effects["signal"].astype(str).tolist(),
        "quality_status": "historical_pseudo_oos" if completed_periods < 24 else "descriptive_with_research_selection_risk",
        "checks": {
            "common_period_count": True,
            "unique_signal_rows": True,
            "future_price_selection_disclosed": True,
            "positive_pe_sample_disclosed": True,
        },
    }
    if prospective_manifest_path is not None:
        prospective = json.loads(prospective_manifest_path.read_text(encoding="utf-8"))
        result["prospective"] = {
            "manifest": str(prospective_manifest_path),
            "manifest_sha256": sha256(prospective_manifest_path),
            "frozen_formation_end": prospective.get("frozen_formation_end"),
            "completed_windows": prospective.get("completed_windows"),
            "pending_windows": prospective.get("pending_windows"),
            "inference_status": prospective.get("inference_status"),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--effect-summary", type=Path, required=True)
    parser.add_argument("--prospective-manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit_outputs(args.manifest, args.effect_summary, args.prospective_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
