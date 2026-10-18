"""Illustrate valuation denominators using an observed owner snapshot, not a backtest."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import yaml

SAMPLE = ["000651.SZ", "002027.SZ", "002415.SZ", "300059.SZ", "600519.SH", "600900.SH"]
FIELDS = {
    "income": ["n_income_attr_p"],
    "fina_indicator": ["profit_dedt"],
    "balancesheet": ["total_hldr_eqy_exc_min_int", "goodwill", "intan_assets"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive_multiple(market_value: float, denominator: float) -> float | None:
    if not np.isfinite(market_value) or market_value <= 0:
        raise ValueError("market value must be positive and finite")
    return float(market_value / denominator) if np.isfinite(denominator) and denominator > 0 else None


def trailing(current: float, annual: float, previous: float) -> float:
    """Cumulative current YTD plus prior full year minus matching prior YTD."""
    return float(current + annual - previous)


def load_statement(root: Path, name: str, now: pd.Timestamp, hashes: dict) -> pd.DataFrame:
    child = root / "normalized" / name
    manifest_path = child / "manifest.yml"
    manifest = yaml.safe_load(manifest_path.read_text())
    archive = yaml.safe_load((root / "manifest.yml").read_text())
    expected = next(x for x in archive["children"]["normalized"] if x["path"] == f"normalized/{name}")
    if sha(manifest_path) != expected["manifest_sha256"]:
        raise ValueError("child manifest hash differs from sealed archive")
    if manifest.get("status") != "completed" or not manifest.get("immutable_snapshot"):
        raise ValueError("unsealed or incomplete normalized data")
    files = []
    for item in manifest["integrity"]["files"]:
        path = (child / item["path"]).resolve()
        if not path.is_relative_to(child.resolve()) or sha(path) != item["sha256"]:
            raise ValueError("input integrity failure")
        hashes[f"{name}/{item['path']}"] = item["sha256"]
        files.append(path)
    # Push down the issuer selection and read only columns needed by this illustration.
    frames = []
    for path in files:
        available = pq.read_schema(path).names
        columns = [c for c in ["ts_code", "end_date", "ann_date", "f_ann_date", "report_type",
                               "_source_retrieved_at", *FIELDS[name]] if c in available]
        frames.append(pd.read_parquet(path, columns=columns, filters=[("ts_code", "in", SAMPLE)]))
    frame = pd.concat(frames, ignore_index=True)
    frame["observed"] = pd.to_datetime(frame["_source_retrieved_at"], utc=True, errors="raise")
    # Date-only disclosures are admitted only after their entire local calendar day.
    date_cols = [c for c in ["ann_date", "f_ann_date"] if c in frame]
    dates = [pd.to_datetime(frame[c], format="%Y%m%d", errors="coerce") for c in date_cols]
    frame["disclosed"] = pd.concat(dates, axis=1).max(axis=1)
    local_day = now.tz_convert("Asia/Shanghai").tz_localize(None).normalize()
    frame = frame.loc[(frame.observed <= now) & (frame.disclosed < local_day)].copy()
    if "report_type" in frame:
        # Accept only cumulative consolidated standard statements, never mix scopes.
        frame = frame.loc[frame.report_type.astype(str) == "1"]
    frame = frame.sort_values(["disclosed", "observed"])
    if frame.duplicated(["ts_code", "end_date", "disclosed", "observed"]).any():
        raise ValueError("ambiguous same-version financial records")
    return frame.drop_duplicates(["ts_code", "end_date"], keep="last")


def run(vintage: Path, daily: Path, output: Path) -> dict:
    repo = Path(__file__).resolve().parents[1]
    if output.resolve().is_relative_to(repo) or output.exists():
        raise ValueError("output must be a new directory outside the repository")
    now = pd.Timestamp.now(tz="UTC")
    seal = json.loads((vintage / "SEALED.json").read_text())
    if sha(vintage / "manifest.yml") != seal["manifest_sha256"]:
        raise ValueError("archive manifest seal mismatch")
    hashes = {"archive_manifest": seal["manifest_sha256"], "daily_basic": sha(daily)}
    statements = {name: load_statement(vintage, name, now, hashes) for name in FIELDS}
    prices = pd.read_parquet(daily)
    prices = prices.loc[prices.ts_code.isin(SAMPLE)].copy()
    if prices.ts_code.duplicated().any() or len(prices) != len(SAMPLE):
        raise ValueError("market-value partition must have exactly one row per sample issuer")
    price_dates = set(prices.trade_date.astype(str))
    if len(price_dates) != 1 or next(iter(price_dates)) > now.strftime("%Y%m%d"):
        raise ValueError("invalid or future market-value date")
    rows = []
    ledger = []
    for code in SAMPLE:
        tables = {n: d.loc[d.ts_code == code].set_index("end_date") for n, d in statements.items()}
        common = set.intersection(*(set(d.index) for d in tables.values()))
        candidates = []
        for period in sorted(common, reverse=True):
            y, md = int(period[:4]), period[4:]
            legs = [period] if md == "1231" else [period, f"{y-1}1231", f"{y-1}{md}"]
            if all(set(legs).issubset(tables[n].index) for n in ["income", "fina_indicator"]):
                candidates.append((period, legs))
        if not candidates:
            raise ValueError(f"no matched trailing period: {code}")
        period, legs = candidates[0]
        values = {}
        for name, field in [("income", "n_income_attr_p"), ("fina_indicator", "profit_dedt")]:
            series = pd.to_numeric(tables[name].loc[legs, field], errors="coerce")
            values[field] = float(series.iloc[0]) if len(legs) == 1 else trailing(*series)
            for leg in legs:
                record = tables[name].loc[leg]
                ledger.append({"code": code, "dataset": name, "period": leg,
                               "disclosure": str(record.disclosed.date()), "observed": str(record.observed)})
        book = tables["balancesheet"].loc[period]
        eq, goodwill, intangible = [float(book[f]) for f in FIELDS["balancesheet"]]
        # Missing assets remain missing, never silently become zero.
        if (np.isfinite(goodwill) and goodwill < 0) or (np.isfinite(intangible) and intangible < 0):
            raise ValueError("negative goodwill or intangible assets")
        mv = float(prices.set_index("ts_code").loc[code, "total_mv"]) * 10000
        row = {"code": code, "report_period": period,
               "pe_ttm": positive_multiple(mv, values["n_income_attr_p"]),
               "pe_ex_nonrecurring_ttm": positive_multiple(mv, values["profit_dedt"]),
               "pb_parent": positive_multiple(mv, eq),
               "pb_ex_goodwill_proxy": positive_multiple(mv, eq - goodwill),
               "pb_ex_goodwill_intangibles_proxy": positive_multiple(mv, eq - goodwill - intangible)}
        rows.append(row)
        ledger.append({"code": code, "dataset": "balancesheet", "period": period,
                       "disclosure": str(book.disclosed.date()), "observed": str(book.observed)})
    metrics = [k for k in rows[0] if k not in {"code", "report_period"}]
    common_rows = [r for r in rows if all(r[k] is not None for k in metrics)]
    for metric in metrics:
        ranks = pd.Series({r["code"]: r[metric] for r in common_rows}).rank(method="min")
        for row in rows:
            row[metric + "_common_rank"] = int(ranks[row["code"]]) if row["code"] in ranks else None
    result = {"schema_version": "valuation_denominators_illustration.v1",
              "observed_at_utc": now.isoformat(), "price_date": next(iter(price_dates)),
              "sample_selection": "six deliberately chosen A-only issuers; not a cheapness screen",
              "historical_pit_certified": False, "returns_backtested": False,
              "deducted_asset_scope": "consolidated assets deducted from parent equity: unallocated proxy",
              "common_rank_sample_count": len(common_rows), "input_sha256": hashes,
              "rows": rows, "source_dates": ledger}
    output.mkdir(parents=True)
    (output / "reviewed_summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vintage", type=Path, required=True)
    parser.add_argument("--daily-basic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.vintage, args.daily_basic, args.output)
    print(json.dumps({"rows": len(result["rows"]), "common_rank_sample_count": result["common_rank_sample_count"]}))
