"""Run a calendar-audited comparison from an explicit frozen data-owner bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import gettempdir

import pandas as pd

from .inputs import read_bundle, audit_pair
from .analysis import describe_pair


def run_study(manifest_path: Path, output: Path) -> dict:
    output = output.resolve()
    if any(
        (parent / ".git").exists()
        for parent in [output, *output.parents]
        if parent not in {Path(gettempdir()), Path.home()}
    ):
        raise ValueError("outputs must remain outside source repositories")
    if output.exists():
        raise FileExistsError("select a new output directory")
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    for spec in manifest.get("series", {}).values():
        allowed = {
            "equity": {"price", "total_return"},
            "commodity": {"commodity_index", "commodity_futures_return_index"},
        }
        if spec.get("role") not in allowed or spec.get("return_basis") not in allowed[spec["role"]]:
            raise ValueError("invalid role or return basis")
        if spec.get("currency") != "CNY":
            raise ValueError("this study requires CNY levels")
    series, calendars, receipts = read_bundle(manifest_path)
    for exchange in ["SSE", "SHFE"]:
        if exchange not in calendars:
            raise ValueError("independent SSE and SHFE calendars required")
    start = pd.Timestamp(manifest["start"])
    end = pd.Timestamp(manifest["end"])
    results = {
        "schema_version": 1,
        "evidence_stage": "numerical_diagnostics",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_revision": manifest["source_revision"],
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "code_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ["inputs.py", "analysis.py", "run.py"]
        },
        "input_receipts": receipts,
        "series_metadata": manifest["series"],
        "coverage": {},
        "comparisons": {},
        "missing_series": [],
        "limitations": [
            "Observed revised history, not point-in-time inputs.",
            "Index allocations are hypothetical and omit collateral, implementation and calibrated costs.",
            "Monthly windows overlap; no forecast probabilities or optimized weights.",
            "Source semantic review and publication rights remain separate from numerical checks.",
        ],
    }
    for code in manifest["series"]:
        if code not in series:
            results["missing_series"].append(code)
            continue
        s = series[code]
        results["coverage"][code] = {
            "first": s.index.min().date().isoformat(),
            "last": s.index.max().date().isoformat(),
            "rows": len(s),
        }
    for equity, eq_meta in manifest["series"].items():
        if eq_meta["role"] != "equity" or equity not in series:
            continue
        for commodity, co_meta in manifest["series"].items():
            if co_meta["role"] != "commodity" or commodity not in series:
                continue
            if eq_meta["currency"] != co_meta["currency"]:
                raise ValueError("currency mismatch")
            audit, levels = audit_pair(
                series[equity], series[commodity], calendars["SSE"], calendars["SHFE"], start, end
            )
            comparison = {
                "equity": equity,
                "commodity": commodity,
                "audit": audit,
                "equity_return_basis": eq_meta["return_basis"],
                "commodity_return_basis": co_meta["return_basis"],
            }
            if levels is not None:
                common = calendars["SSE"].intersection(calendars["SHFE"])
                comparison["analysis"] = describe_pair(levels, common, min(end, levels.index[-1]))
            results["comparisons"][equity + "__" + commodity] = comparison
    serialized = json.dumps(results, indent=2, allow_nan=False) + "\n"
    output.mkdir(parents=True, exist_ok=False)
    (output / "result.json").write_text(serialized)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_study(args.manifest, args.output)
    print(
        json.dumps(
            {
                "comparisons": len(result["comparisons"]),
                "eligible": sum(v["audit"]["eligible"] for v in result["comparisons"].values()),
            }
        )
    )


if __name__ == "__main__":
    main()
