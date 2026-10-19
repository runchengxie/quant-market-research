"""Compare one formation before/after a quarantined statement-template repair."""

import argparse
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from analyze_valuation_panel import digest, load_snapshot
from market_research.valuation_panel import METRICS, make_panel, summarize


def load_diagnostics(vintage: Path, diagnostic: Path, hashes: dict) -> tuple[dict, dict]:
    """Verify diagnostic content, baseline lineage and actual observation clocks."""
    receipt_path = diagnostic / "diagnostic_receipt.json"
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("published_asset") is not False or receipt.get("historical_pit_certified") is not False:
        raise ValueError("expected non-published diagnostic receipt")
    repaired = {}
    for name in ["income", "balancesheet"]:
        path = diagnostic / f"{name}_diagnostic.parquet"
        if digest(path) != receipt["datasets"][name]["diagnostic_sha256"]:
            raise ValueError("diagnostic data hash differs")
        old_manifest = vintage / "normalized" / name / "manifest.yml"
        if digest(old_manifest) != receipt["datasets"][name]["old_normalized_manifest_sha256"]:
            raise ValueError("diagnostic baseline differs")
        raw_manifest = vintage / "raw" / name / "manifest.yml"
        if digest(raw_manifest) != receipt["datasets"][name]["raw_manifest_sha256"]:
            raise ValueError("diagnostic raw vintage differs")
        repaired[name] = pd.read_parquet(path)
        if "_source_retrieved_at" not in repaired[name]:
            raise ValueError("diagnostic observation timestamp is missing")
        observed = pd.to_datetime(repaired[name]["_source_retrieved_at"], utc=True, errors="coerce")
        if observed.isna().any() or (observed > pd.Timestamp.now(tz="UTC")).any():
            raise ValueError("invalid or future diagnostic observation timestamp")
        hashes[f"diagnostic/{name}"] = digest(path)
    hashes["diagnostic_receipt"] = digest(receipt_path)
    return repaired, receipt


def run(args):
    args.output = args.output.resolve()
    repo = Path(__file__).resolve().parents[1]
    if args.output.exists() or args.output.is_relative_to(repo):
        raise ValueError("output must be new and outside the repository")
    hashes = {}
    original = load_snapshot(args.vintage, hashes)
    diagnostic, receipt = load_diagnostics(args.vintage, args.diagnostic, hashes)
    repaired = {**original, **diagnostic}
    prices = pq.ParquetFile(args.prices).read(columns=["ts_code", "trade_date", "total_mv"]).to_pandas()
    hashes["daily_basic"] = digest(args.prices)
    before = make_panel(original, prices, args.date, require_observed=False)
    after = make_panel(repaired, prices, args.date, require_observed=False)
    groups = {
        "all_quotes": before.ts_code,
        "baseline_financial_templates": before.loc[before.reporting_group.eq("financial_reporting"), "ts_code"],
        "baseline_general_template": before.loc[before.reporting_group.eq("general_reporting"), "ts_code"],
    }
    comparison = {}
    for name, codes in groups.items():
        rows = {}
        for label, frame in [("before", before), ("after", after)]:
            sample = frame.loc[frame.ts_code.isin(codes)].copy()
            sample.attrs = {}
            rows[label] = summarize(sample)
        comparison[name] = rows
    aligned = before.set_index("ts_code").join(after.set_index("ts_code"), lsuffix="_before", rsuffix="_after")
    changes = []
    for metric in METRICS:
        a, b = aligned[metric + "_before"], aligned[metric + "_after"]
        changes.append({"metric": metric, "gained": int((a.isna() & b.notna()).sum()),
                        "lost": int((a.notna() & b.isna()).sum())})
    result = {
        "schema_version": "financial_template_coverage_review.v1",
        "formation_date": args.date,
        "historical_pit_certified": False,
        "returns_backtested": False,
        "published_owner_asset": False,
        "new_api_requests": 0,
        "comparison": comparison,
        "availability_changes": changes,
        "input_sha256": hashes,
        "quarantine": {n: {k: v for k, v in d.items() if k in ["quarantined_keys", "quarantined_rows"]}
                       for n, d in receipt["datasets"].items()},
    }
    args.output.mkdir(parents=True)
    before.to_parquet(args.output / "before.parquet", index=False)
    after.to_parquet(args.output / "after.parquet", index=False)
    (args.output / "reviewed_coverage.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({n: {v: {"common_five": s["common_five"], "metrics": s["metrics"]} for v, s in x.items()}
                      for n, x in comparison.items()}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vintage", type=Path, required=True)
    parser.add_argument("--diagnostic", type=Path, required=True)
    parser.add_argument("--prices", type=Path, required=True)
    parser.add_argument("--date", default="20261016")
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args())
