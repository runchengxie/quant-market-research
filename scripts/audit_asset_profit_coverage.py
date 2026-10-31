"""Audit retained fiscal-profit availability for fixed historical index cohorts.

Counts valid fields, without estimating earnings growth or certifying original
historical revisions. Reads a hash-matched income component and frozen weights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd
import yaml

from market_research.studies.asset_returns.inputs import read_frozen_response


def audit(normalized_root: Path, owner_task: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("select a new audit output")
    if any(
        (p / ".git").exists()
        for p in [output.resolve(), *output.resolve().parents]
        if p not in {Path.home(), Path(gettempdir())}
    ):
        raise ValueError("audit outputs must remain outside repositories")
    manifest_bytes = (normalized_root / "manifest.yml").read_bytes()
    manifest = yaml.safe_load(manifest_bytes)
    entry = next(
        x
        for x in manifest["integrity"]["files"]
        if x["path"] == "components/income/data/part.parquet"
    )
    income = normalized_root / entry["path"]
    digest = hashlib.sha256(income.read_bytes()).hexdigest()
    if digest != entry["sha256"]:
        raise ValueError("income asset hash does not match its manifest")
    frame = pd.read_parquet(
        income, columns=["ts_code", "end_date", "report_type", "n_income_attr_p"]
    )
    frame = frame[frame.report_type.astype(str).eq("1")].copy()
    frame["end_date"] = frame.end_date.astype(str)
    frame["valid_profit"] = np.isfinite(pd.to_numeric(frame.n_income_attr_p, errors="coerce"))
    raw = owner_task / "raw"
    receipts = json.loads((raw / "receipt.json").read_text())
    res = {}
    for code in ["000300_SH", "000852_SH"]:
        cohorts = {}
        for year in [2015, 2025]:
            ident = f"{code}_weights_{year}"
            row = next(r for r in receipts if r["id"] == ident)
            weights = read_frozen_response(raw / (ident + ".json"), row["sha256"])
            cohorts[year] = set(
                weights.loc[weights.trade_date.eq(weights.trade_date.max()), "con_code"]
            )
        coverage = {}
        for label, symbols in [
            ("initial", cohorts[2015]),
            ("final", cohorts[2025]),
            ("union", cohorts[2015] | cohorts[2025]),
        ]:
            coverage[label] = {"members": len(symbols)}
            for year in [2015, 2025]:
                good = set(
                    frame.loc[frame.end_date.eq(f"{year}1231") & frame.valid_profit, "ts_code"]
                )
                coverage[label][f"fy{year}_profit_available"] = len(symbols & good)
        res[code] = coverage
    result = {
        "income_sha256": digest,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "revision_safety": manifest["revision_safety"],
        "coverage": res,
        "interpretation": "At least one finite retained consolidated-profit field; not original-vintage, share or per-index-EPS certification.",
    }
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--normalized-root", type=Path, required=True)
    parser.add_argument("--owner-task", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(audit(args.normalized_root, args.owner_task, args.output)["coverage"], indent=2)
    )
