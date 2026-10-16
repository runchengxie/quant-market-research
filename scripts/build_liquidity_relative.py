#!/usr/bin/env python3
"""Repartition reviewed external liquidity features into market-relative quintiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb

from market_research.liquidity_relative import rank_features, summarize_relative


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    out = args.output.resolve()
    if out == repo or repo in out.parents:
        raise ValueError("research outputs must stay outside repository")
    out.mkdir(parents=True, exist_ok=True)
    base_raw = args.base.read_bytes()
    base = json.loads(base_raw)
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='1GB'")
    con.execute("SET temp_directory='" + str(out / "spill").replace("'", "''") + "'")
    files = [args.features / f"features-{m['market']}.parquet" for m in base["markets"]]
    signatures = {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in files}
    literals = ",".join("'" + str(p).replace("'", "''") + "'" for p in files)
    con.execute(f"CREATE VIEW features AS SELECT * FROM read_parquet([{literals}])")
    rank_features(con, "features", "ranked")
    latest = []
    for m in base["markets"]:
        t = dict(
            included_markets=[m["market"]],
            missing_markets=[],
            common_start=m["as_of"],
            common_end=m["as_of"],
            common_dates=1,
            markets=[m],
        )
        latest.extend(summarize_relative(con, "ranked", t)["markets"])
    periods = [summarize_relative(con, "ranked", p) for p in base["periods"]]
    receipts = []
    for m, p in zip(base["markets"], files, strict=True):
        h = hashlib.sha256()
        with p.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        if signatures[str(p)] != (p.stat().st_size, p.stat().st_mtime_ns):
            raise ValueError("input changed during calculation")
        receipts.append(dict(market=m["market"], bytes=p.stat().st_size, sha256=h.hexdigest()))
    result = dict(
        schema_version="liquidity.relative.v1",
        absolute_summary_sha256=hashlib.sha256(base_raw).hexdigest(),
        method="Within each eligible market/day, NTILE(5) by prior-session USD market cap ascending, ties by symbol. Historical views pool security-days; relative size is not equal dollar size.",
        code_receipts={
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__), repo / "src/market_research/liquidity_relative.py"]
        },
        feature_receipts=receipts,
        markets=latest,
        periods=periods,
    )
    (out / "relative.proposed.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    print("Relative proposal ready for independent review", flush=True)


if __name__ == "__main__":
    main()
