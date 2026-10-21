#!/usr/bin/env python3
"""Read persisted ledger files and independently replay cash, units and marks."""

import argparse
from itertools import groupby
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from market_research.studies.grouped_valuation_ledger import LedgerVerifier
from run_grouped_valuation_ledger import digest, write_json


def grouped_rows(path):
    rows = (
        row
        for batch in pq.ParquetFile(path).iter_batches(batch_size=16384)
        for row in batch.to_pylist()
    )
    for day, block in groupby(rows, key=lambda r: r["date"]):
        yield day, list(block)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or args.output.resolve().is_relative_to(
        Path(__file__).resolve().parents[1]
    ):
        raise ValueError("new external audit file required")
    receipt = json.loads((args.run / "receipt.json").read_text())
    for rel, sha in receipt["outputs"].items():
        if digest(args.run / rel) != sha:
            raise ValueError("persisted artifact hash mismatch: " + rel)
    summary = json.loads((args.run / "summary.json").read_text())
    audits = []
    for portfolio in summary["portfolios"]:
        root = args.run / portfolio["portfolio"]
        hs = iter(grouped_rows(root / "holdings.parquet"))
        os = iter(grouped_rows(root / "orders.parquet"))
        h = next(hs, None)
        o = next(os, None)
        verifier = LedgerVerifier(1_000_000.0)
        daily = pd.read_csv(root / "daily.csv", dtype={"date": str})
        for row in daily.to_dict("records"):
            day = row["date"]
            if pd.isna(row["strict_nav"]):
                row["strict_nav"] = None
            holdings = h[1] if h and h[0] == day else []
            orders = o[1] if o and o[0] == day else []
            verifier.check(row, holdings, orders)
            # Terminal and quote-missing valuation never create a cash event.
            for holding in holdings:
                if holding["mark_source"].startswith("unresolved_"):
                    assert holding["mark_price"] is None
                    assert holding["units"] > 0
            for order in orders:
                assert order["requested_date"] <= day
                if order["side"] == "sell":
                    assert order["cohort"] < day  # no same-day resale of new units
            if h and h[0] == day:
                h = next(hs, None)
            if o and o[0] == day:
                o = next(os, None)
        assert h is None and o is None
        assert verifier.days == portfolio["sessions"]
        audits.append(
            dict(
                portfolio=portfolio["portfolio"],
                days=verifier.days,
                max_cash_error=verifier.max_cash_error,
                passed=True,
            )
        )
        print("persisted_audit_pass", portfolio["portfolio"], flush=True)
    write_json(
        args.output,
        dict(
            status="passed",
            run_receipt_sha256=digest(args.run / "receipt.json"),
            audit_code_sha256=digest(__file__),
            portfolios=audits,
            scope="Persisted artifact hashes, order cash/fee/unit replay, daily mark identity, unresolved assets and no T+0 resale; not independent market fill evidence.",
        ),
    )


if __name__ == "__main__":
    main()
