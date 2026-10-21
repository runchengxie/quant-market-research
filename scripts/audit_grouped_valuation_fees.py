#!/usr/bin/env python3
"""Independently check configured fee arithmetic in a frozen ledger run."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve().is_relative_to(
        Path(__file__).resolve().parents[1]
    ):
        raise ValueError("new external audit directory required")
    receipt_path = args.run / "receipt.json"
    run_sha = digest(receipt_path)
    receipt = json.loads(receipt_path.read_text())
    if digest(args.run / "summary.json") != receipt["outputs"]["summary.json"]:
        raise ValueError("summary hash mismatch")
    portfolios = json.loads((args.run / "summary.json").read_text())["portfolios"]
    rates = {"touch0": 0.0, "touch10": 0.001, "touch30": 0.003, "close10": 0.001}
    rows, hashes = [], {}
    for portfolio in portfolios:
        rate = rates[portfolio["scenario"]]
        relative = portfolio["portfolio"] + "/orders.parquet"
        path = args.run / relative
        before = digest(path)
        if before != receipt["outputs"][relative]:
            raise ValueError("orders hash mismatch: " + relative)
        orders = pd.read_parquet(path, columns=["status", "fee", "notional"])
        filled = orders["status"].eq("filled").to_numpy()
        fees = orders["fee"].to_numpy(dtype=float)
        notional = orders["notional"].to_numpy(dtype=float)
        if not np.isfinite(fees).all() or not np.isfinite(notional[filled]).all():
            raise AssertionError("nonfinite fee or filled notional")
        expected = np.where(filled, notional * rate, 0.0)
        matches = np.isclose(fees, expected, rtol=1e-12, atol=1e-9)
        if not matches.all():
            raise AssertionError(f"{relative}: {int((~matches).sum())} fee mismatches")
        if digest(path) != before:
            raise ValueError("orders changed during audit")
        hashes[relative] = before
        rows.append(
            dict(
                portfolio=portfolio["portfolio"],
                fee_rate=rate,
                orders=len(orders),
                filled_orders=int(filled.sum()),
                violations=0,
                max_abs_error=float(np.abs(fees - expected).max(initial=0)),
            )
        )
    if (
        digest(receipt_path) != run_sha
        or digest(args.run / "summary.json") != receipt["outputs"]["summary.json"]
    ):
        raise ValueError("receipt or summary changed during audit")
    args.output.mkdir(parents=True)
    result = dict(
        status="passed",
        run_receipt_sha256=run_sha,
        source_sha256=digest(__file__),
        order_file_sha256=hashes,
        portfolios=rows,
        absolute_tolerance=1e-9,
        relative_tolerance=1e-12,
        scope="Checks configured scenario fee multiplication and zero fees for unfilled orders; does not validate actual broker fees, taxes, lots or execution.",
    )
    (args.output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                status="passed",
                portfolios=len(rows),
                orders=sum(x["orders"] for x in rows),
                filled_orders=sum(x["filled_orders"] for x in rows),
                max_abs_error=max(x["max_abs_error"] for x in rows),
            )
        )
    )


if __name__ == "__main__":
    main()
