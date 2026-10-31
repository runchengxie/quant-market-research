"""Audit frozen ETF years and missing original members; retain details externally."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd
import yaml

from market_research.studies.asset_returns.closure import annual_etf_audit, classify_member
from market_research.studies.asset_returns.inputs import read_frozen_response


def audit(owner: Path, cohort_owner: Path, normalized: Path, etf_monthly: Path, output: Path):
    if output.exists():
        raise FileExistsError("select a new audit output")
    if any(
        (p / ".git").exists()
        for p in [output.resolve(), *output.resolve().parents]
        if p not in {Path.home(), Path(gettempdir())}
    ):
        raise ValueError("outputs must remain outside repositories")
    sources = []

    def response(folder, ident):
        receipt = folder / "receipt.json"
        entries = json.loads(receipt.read_bytes())
        row = next(x for x in entries if x["id"] == ident)
        if row.get("code") != 0:
            raise ValueError(f"unsuccessful response: {ident}")
        path = folder / (ident + ".json")
        blob = path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != row["sha256"]:
            raise ValueError("frozen response hash mismatch")
        sources.append(
            {
                "id": f"{folder.name}/{ident}",
                "sha256": row["sha256"],
                "observed_at": row["observed_at"],
            }
        )
        data = json.loads(blob)["data"]
        return pd.DataFrame(data["items"], columns=data["fields"])

    master = pd.concat(
        [
            response(
                owner / ("master-explicit" if status == "L" else "master-retry"), "master_" + status
            )
            for status in ("L", "D")
        ]
    )
    if master.ts_code.duplicated().any():
        raise ValueError("duplicate security identity")
    master = master.set_index("ts_code").to_dict("index")
    manifest_blob = (normalized / "manifest.yml").read_bytes()
    manifest = yaml.safe_load(manifest_blob)
    entry = next(
        x
        for x in manifest["integrity"]["files"]
        if x["path"] == "components/income/data/part.parquet"
    )
    income_path = normalized / entry["path"]
    if hashlib.sha256(income_path.read_bytes()).hexdigest() != entry["sha256"]:
        raise ValueError("income asset hash mismatch")
    frame = pd.read_parquet(income_path)
    good = set(
        frame.loc[
            (frame.end_date.astype(str) == "20251231")
            & (frame.report_type.astype(str) == "1")
            & np.isfinite(pd.to_numeric(frame.n_income_attr_p, errors="coerce")),
            "ts_code",
        ]
    )
    cohorts, details = {}, []
    for code in ("000300_SH", "000852_SH"):
        raw = cohort_owner / "raw"
        ident = code + "_weights_2015"
        r = next(x for x in json.loads((raw / "receipt.json").read_text()) if x["id"] == ident)
        w = read_frozen_response(raw / (ident + ".json"), r["sha256"])
        sources.append({"id": ident, "sha256": r["sha256"]})
        members = set(w.loc[w.trade_date == w.trade_date.max(), "con_code"])
        missing = sorted(members - good)
        classified = []
        for symbol in missing:
            ident = symbol.replace(".", "_") + "_fy2025"
            folder = owner / "raw"
            retry = owner / ("retry-02" if symbol == "600705.SH" else "retry-01")
            if retry.exists() and any(
                x["id"] == ident for x in json.loads((retry / "receipt.json").read_text())
            ):
                folder = retry
            data = response(folder, ident)
            valid = (
                (
                    data.end_date.astype(str).eq("20251231")
                    & data.report_type.astype(str).eq("1")
                    & np.isfinite(pd.to_numeric(data.n_income_attr_p, errors="coerce"))
                ).any()
                if not data.empty
                else False
            )
            status = classify_member(master.get(symbol), bool(valid))
            row = {
                "cohort": code,
                "ts_code": symbol,
                "master": master.get(symbol),
                "classification": status,
                "api_rows": len(data),
            }
            details.append(row)
            classified.append(status)
        cohorts[code] = {
            "initial_members": len(members),
            "missing_original_profit": len(missing),
            "classifications": dict(sorted(Counter(classified).items())),
        }
    blob = etf_monthly.read_bytes()
    sources.append({"id": "512100_monthly", "sha256": hashlib.sha256(blob).hexdigest()})
    etf = annual_etf_audit(
        pd.read_csv(etf_monthly), {2018: -0.3549, 2019: 0.3460, 2020: 0.3136, 2025: 0.2923}
    )
    # The strict rounded-report comparison retains all discrepancies.
    # Do not widen tolerance or infer the cause of a historical NAV mismatch.
    result = {
        "schema_version": 1,
        "cohorts": cohorts,
        "member_details": details,
        "etf_years": etf,
        "sources": sources,
        "income_sha256": entry["sha256"],
        "income_manifest_sha256": hashlib.sha256(manifest_blob).hexdigest(),
        "revision_safety": manifest["revision_safety"],
        "code_sha256": {
            str(p.relative_to(Path(__file__).resolve().parents[1])): hashlib.sha256(
                p.read_bytes()
            ).hexdigest()
            for p in [
                Path(__file__).resolve(),
                Path(
                    __import__(
                        "market_research.studies.asset_returns.closure", fromlist=[""]
                    ).__file__
                ),
            ]
        },
        "interpretation": "Listing status is a vendor observation, not corporate-action continuity or a zero recovery/profit assumption.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("owner", "cohort-owner", "normalized", "etf-monthly", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.owner, args.cohort_owner, args.normalized, args.etf_monthly, args.output)
    print(json.dumps(result["cohorts"], indent=2))
