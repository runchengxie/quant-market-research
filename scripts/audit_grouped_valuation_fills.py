#!/usr/bin/env python3
"""Independent SQL check of saved hypothetical fills against frozen daily inputs."""

import argparse
import json
from pathlib import Path

import duckdb
import pandas as pd

from run_grouped_valuation_ledger import digest, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve().is_relative_to(
        Path(__file__).resolve().parents[1]
    ):
        raise ValueError("new external audit directory required")
    receipt = json.loads((args.run / "receipt.json").read_text())
    # This audit must stand alone, rather than relying on a prior replay audit.
    for rel, sha in receipt["outputs"].items():
        if digest(args.run / rel) != sha:
            raise ValueError("persisted artifact hash mismatch: " + rel)
    summaries = json.loads((args.run / "summary.json").read_text())["portfolios"]
    args.output.mkdir(parents=True)
    con = duckdb.connect(str(args.output / "daily_audit.duckdb"))
    con.execute("SET threads=2")
    con.execute("SET memory_limit='512MB'")
    con.execute("SET temp_directory=?", [str(args.output / "spill")])
    paths = [
        p
        for p in receipt["inputs"]
        if "/data/" in p and p.endswith(".parquet") and "daily_clean_" in p
    ]
    if not paths:
        raise ValueError("frozen quote file inventory absent")
    for path in paths:
        if digest(path) != receipt["inputs"][path]:
            raise ValueError("frozen quote changed")
    start = min(x["entry_date"] for x in summaries)
    end = max(x["last_date"] for x in summaries)
    con.execute(
        """CREATE TABLE prices AS SELECT ts_code,trade_date,adj_close,high,low,
                up_limit,down_limit,amount,is_suspended,is_limit_up,is_limit_down
                FROM read_parquet(?) WHERE trade_date BETWEEN ? AND ?""",
        [paths, start, end],
    )
    members_path = next(
        p for p in receipt["inputs"] if p.endswith("private_factor_members.parquet")
    )
    if digest(members_path) != receipt["inputs"][members_path]:
        raise ValueError("frozen member hash mismatch")
    members = pd.read_parquet(members_path, columns=["ts_code", "delist_date"]).drop_duplicates()
    if members.groupby("ts_code").delist_date.nunique().gt(1).any():
        raise ValueError("conflicting terminal dates")
    con.register("members_input", members)
    con.execute(
        "CREATE TABLE terminal AS SELECT ts_code,min(delist_date) AS delist_date FROM members_input GROUP BY ts_code"
    )
    duplicate_prices = con.execute(
        "SELECT count(*) FROM (SELECT ts_code,trade_date FROM prices GROUP BY ts_code,trade_date HAVING count(*)>1)"
    ).fetchone()[0]
    if duplicate_prices:
        raise ValueError("duplicate quote identity")
    rows = []
    for portfolio in summaries:
        path = args.run / portfolio["portfolio"] / "orders.parquet"
        fills = pd.read_parquet(path)
        fills = fills.loc[fills.status.eq("filled")]
        con.register("fills", fills)
        violations = con.execute(
            """SELECT count(*) FROM fills f
          LEFT JOIN prices p ON f.symbol=p.ts_code AND f.date=p.trade_date
          LEFT JOIN terminal t ON f.symbol=t.ts_code
          WHERE f.side IS NULL OR f.side NOT IN ('buy','sell')
          OR f.price IS NULL OR NOT isfinite(f.price) OR f.price<=0
          OR f.units IS NULL OR NOT isfinite(f.units) OR f.units<=0
          OR f.notional IS NULL OR NOT isfinite(f.notional) OR f.notional<=0
          OR f.fee IS NULL OR NOT isfinite(f.fee) OR f.fee<0
          OR p.ts_code IS NULL OR p.adj_close IS NULL OR NOT isfinite(p.adj_close)
          OR p.adj_close<=0 OR abs(f.price-p.adj_close)>1e-9*greatest(1,abs(p.adj_close))
          OR p.amount IS NULL OR NOT isfinite(p.amount) OR p.amount<=0
          OR p.is_suspended IS DISTINCT FROM FALSE
          OR p.is_limit_up IS NULL OR p.is_limit_down IS NULL
          OR (t.delist_date IS NOT NULL AND f.date>=t.delist_date)
          OR (f.side='buy' AND p.is_limit_up) OR (f.side='sell' AND p.is_limit_down)
          OR (? AND ((f.side='buy' AND (p.high IS NULL OR NOT isfinite(p.high) OR p.high<=0
                       OR p.up_limit IS NULL OR NOT isfinite(p.up_limit) OR p.up_limit<=0 OR p.high>=p.up_limit))
                  OR (f.side='sell' AND (p.low IS NULL OR NOT isfinite(p.low) OR p.low<=0
                       OR p.down_limit IS NULL OR NOT isfinite(p.down_limit) OR p.down_limit<=0 OR p.low<=p.down_limit))))
          """,
            [portfolio["scenario"] != "close10"],
        ).fetchone()[0]
        if violations:
            raise AssertionError(
                f"{portfolio['portfolio']}: {violations} ineligible hypothetical fills"
            )
        rows.append(
            dict(portfolio=portfolio["portfolio"], filled_orders=len(fills), violations=violations)
        )
        print("source_fill_audit_pass", portfolio["portfolio"], len(fills), flush=True)
    con.close()
    for path in paths + [members_path]:
        if digest(path) != receipt["inputs"][path]:
            raise ValueError("input changed during fill audit")
    for rel, sha in receipt["outputs"].items():
        if digest(args.run / rel) != sha:
            raise ValueError("artifact changed during fill audit")
    write_json(
        args.output / "receipt.json",
        dict(
            status="passed",
            run_receipt_sha256=digest(args.run / "receipt.json"),
            source_sha256=digest(__file__),
            quote_files_verified=len(paths),
            portfolios=rows,
            scope="Independent SQL confirms hypothetical fill price and daily eligibility against retained inputs. Daily data do not prove queue execution, intraday funding order or real capacity.",
        ),
    )


if __name__ == "__main__":
    main()
