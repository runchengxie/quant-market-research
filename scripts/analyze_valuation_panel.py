"""Build descriptive monthly valuation ranks and retained-vintage comparisons."""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import yaml

from market_research.valuation_panel import METRICS, STATEMENT_FIELDS, make_panel, summarize


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_snapshot(root: Path, hashes: dict) -> dict:
    seal = json.loads((root / "SEALED.json").read_text())
    manifest_path = root / "manifest.yml"
    if digest(manifest_path) != seal["manifest_sha256"]:
        raise ValueError("vintage manifest seal mismatch")
    archive = yaml.safe_load(manifest_path.read_text())
    if archive.get("status") != "completed" or archive.get("immutable_snapshot") is not True:
        raise ValueError("incomplete owner vintage")
    hashes[root.name + "/manifest"] = seal["manifest_sha256"]
    result = {}
    for name, fields in STATEMENT_FIELDS.items():
        child = root / "normalized" / name
        child_manifest = child / "manifest.yml"
        expected = next(x for x in archive["children"]["normalized"] if x["path"] == f"normalized/{name}")
        if digest(child_manifest) != expected["manifest_sha256"]:
            raise ValueError("normalized manifest hash mismatch")
        manifest = yaml.safe_load(child_manifest.read_text())
        if manifest.get("status") != "completed" or manifest.get("immutable_snapshot") is not True:
            raise ValueError("incomplete normalized asset")
        frames = []
        for item in manifest["integrity"]["files"]:
            path = (child / item["path"]).resolve()
            if not path.is_relative_to(child.resolve()) or digest(path) != item["sha256"]:
                raise ValueError("normalized data hash mismatch")
            hashes[f"{root.name}/{name}/{item['path']}"] = item["sha256"]
            columns = [c for c in ["ts_code", "end_date", "ann_date", "f_ann_date", "report_type", "_source_retrieved_at", *fields] if c in pq.read_schema(path).names]
            frames.append(pd.read_parquet(path, columns=columns))
        result[name] = pd.concat(frames, ignore_index=True)
        observed = pd.to_datetime(result[name]["_source_retrieved_at"], utc=True, errors="coerce")
        if observed.isna().any() or (observed > pd.Timestamp.now(tz="UTC")).any():
            raise ValueError("invalid or future actual observation timestamp")
    return result


def archive_inventory(root):
    """Audit metadata chains without accepting failed archives or changing their seals."""
    result = []
    for vintage in sorted(root.glob("vintage=*")):
        manifest, seal = vintage / "manifest.yml", vintage / "SEALED.json"
        row = {"vintage": vintage.name, "archive_complete": manifest.exists() and seal.exists()}
        if row["archive_complete"]:
            declared = yaml.safe_load(manifest.read_text())
            row["archive_seal_matches"] = digest(manifest) == json.loads(seal.read_text())["manifest_sha256"]
            mismatches = []
            for child in declared["children"]["normalized"]:
                if child["path"].split("/")[-1] not in STATEMENT_FIELDS:
                    continue
                path = vintage / child["path"] / "manifest.yml"
                if not path.exists() or digest(path) != child["manifest_sha256"]:
                    mismatches.append(child["path"])
            row["normalized_manifest_mismatches"] = mismatches
        result.append(row)
    return result


def compare_versions(reconstructed, observed, date, vintage):
    left = reconstructed.set_index("ts_code")
    right = observed.set_index("ts_code")
    common = left.index.intersection(right.index)
    a, b = left.loc[common], right.loc[common]
    both = a.common_five & b.common_five
    changes = []
    for metric in METRICS:
        valid = a[metric].notna() & b[metric].notna()
        changed = valid & ~np.isclose(a[metric], b[metric], rtol=1e-10, atol=1e-10, equal_nan=True)
        changes.append({"metric": metric, "both_available": int(valid.sum()), "different_values": int(changed.sum()),
                        "availability_disagreements": int((a[metric].notna() != b[metric].notna()).sum())})
    ranks = []
    for metric in METRICS:
        x, y = a.loc[both, metric].rank(), b.loc[both, metric].rank()
        rho = x.corr(y) if len(x) > 1 else np.nan
        ranks.append({"metric": metric, "n": len(x), "spearman": float(rho) if np.isfinite(rho) else None})
    return {"date": date, "vintage": vintage, "shared_quote_records": len(common),
            "different_balance_report_period": int((a.end_date.fillna("") != b.end_date.fillna("")).sum()),
            "observed_common_five": int(b.common_five.sum()), "both_common_five": int(both.sum()),
            "metric_changes": changes, "same_metric_version_rank_correlations": ranks}


def run(args):
    output = args.output.resolve()
    repo = Path(__file__).resolve().parents[1]
    if output.exists() or output.is_relative_to(repo):
        raise ValueError("output must be a new directory outside the repository")
    dates = sorted(p.parent.name.split("=", 1)[1] for p in args.daily_basic.glob("data/trade_date=*/part.parquet"))
    dates = [d for d in dates if args.start <= d <= args.end]
    if not dates or args.end > datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d"):
        raise ValueError("invalid or future sample")
    by_month = {}
    for date in dates:
        by_month[date[:6]] = date
    selected = sorted(by_month.values())
    hashes = {}
    current = load_snapshot(args.vintages / args.reference_vintage, hashes)
    output.mkdir(parents=True)
    panels, summaries = [], []
    def prices_for(date):
        path = args.daily_basic / "data" / f"trade_date={date}" / "part.parquet"
        hashes[f"daily_basic/{date}"] = digest(path)
        return pq.ParquetFile(path).read(columns=["ts_code", "trade_date", "total_mv"]).to_pandas()
    for date in selected:
        panel = make_panel(current, prices_for(date), date, require_observed=False)
        if date[4:6] == "12" or date == selected[-1]:
            print("completed formation", date, flush=True)
        panels.append(panel)
        summaries.append(summarize(panel))
    pd.concat(panels, ignore_index=True).to_parquet(output / "reconstructed_panel.parquet", index=False)
    observed_summaries, version_checks, attempts = [], [], []
    # Retained snapshots precede these dates and remain within their stated freshness windows.
    for date, vintage in [("20260831", "vintage=20260829"), ("20260928", "vintage=20260926"), ("20261016", "vintage=20261016")]:
        try:
            retained = load_snapshot(args.vintages / vintage, hashes)
        except ValueError as error:
            attempts.append({"date": date, "vintage": vintage, "admitted": False, "reason": str(error)})
            continue
        attempts.append({"date": date, "vintage": vintage, "admitted": True})
        price = prices_for(date)
        observed = make_panel(retained, price, date, require_observed=True)
        reconstructed = make_panel(current, price, date, require_observed=False)
        observed.to_parquet(output / f"observed_panel_{date}.parquet", index=False)
        observed_summaries.append(summarize(observed))
        version_checks.append(compare_versions(reconstructed, observed, date, vintage))
    public = {"schema_version": "valuation_panel_reviewed.v1", "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "evidence_status": "descriptive_reconstructed_monthly_panel_with_retained_vintage_checks",
              "historical_pit_certified": False, "returns_backtested": False, "ownership_scope_certified": False,
              "source_market_value": "A-price-implied total_mv in yuan; multiclass economic equity value not certified",
              "sample_start": selected[0], "sample_end": selected[-1], "formation_count": len(selected),
              "panel_records": sum(x["quote_records"] for x in summaries),
              "reference_vintage": args.reference_vintage,
              "input_sha256": hashes, "monthly": summaries, "retained_vintage": observed_summaries,
              "version_comparisons": version_checks, "retained_vintage_attempts": attempts,
              "archive_metadata_audit": archive_inventory(args.vintages)}
    (output / "reviewed_summary.json").write_text(json.dumps(public, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: public[k] for k in ["sample_start", "sample_end", "formation_count", "panel_records"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vintages", type=Path, required=True)
    parser.add_argument("--reference-vintage", default="vintage=20261018")
    parser.add_argument("--daily-basic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", default="20160101")
    parser.add_argument("--end", default="20261016")
    run(parser.parse_args())
