#!/usr/bin/env python3
"""Independently check month-weighted liquidity trends with pandas and NumPy."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from market_research.liquidity_rebuild import BUCKET_LABELS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--proposal", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    summary = json.loads(args.proposal.read_text())
    checked = 0
    for market in sorted({r["market"] for r in summary["summary"]}):
        frame = pq.read_table(
            args.features / f"features-{market}.parquet",
            columns=["date", "eligible", "market_cap_usd", "adv20_usd"],
        ).to_pandas(date_as_object=False)
        frame = frame.loc[frame.eligible].copy()
        frame["bucket"] = np.searchsorted([1e7, 1e8, 1e9, 1e10], frame.market_cap_usd, side="right")
        frame["rate"] = frame.adv20_usd / frame.market_cap_usd
        daily = (
            frame.groupby(["date", "bucket"])
            .agg(adv=("adv20_usd", "median"), rate=("rate", "median"), n=("rate", "size"))
            .reset_index()
        )
        daily["month"] = daily.date.dt.to_period("M").astype(str)
        daily["year"] = daily.date.dt.year
        monthly = (
            daily.groupby(["year", "month", "bucket"])
            .agg(adv=("adv", "median"), rate=("rate", "median"), n=("n", "sum"))
            .reset_index()
        )
        for row in (r for r in summary["summary"] if r["market"] == market):
            group = monthly.loc[
                (monthly.year == row["year"])
                & (monthly.bucket == BUCKET_LABELS.index(row["bucket"]))
            ]
            assert len(group) == row["months"] and int(group.n.sum()) == row["security_days"]
            for col, prefix in [("adv", "adv20"), ("rate", "turnover_rate")]:
                keys = (
                    [
                        f"{prefix}_median_of_months_usd",
                        f"{prefix}_monthly_p25_usd",
                        f"{prefix}_monthly_p75_usd",
                    ]
                    if col == "adv"
                    else [
                        "turnover_rate_median_of_months",
                        "turnover_rate_monthly_p25",
                        "turnover_rate_monthly_p75",
                    ]
                )
                for q, key in zip([0.5, 0.25, 0.75], keys, strict=True):
                    assert np.isclose(
                        np.quantile(group[col], q), row[key], rtol=1e-10, atol=1e-8
                    ), (market, row["year"], row["bucket"], key)
                    checked += 1
            checked += 2
        del frame
        print(market, "temporal summaries independently reconciled", flush=True)
    result = dict(
        schema_version="liquidity.stability-review.v1",
        passed=True,
        aggregate_cells_checked=checked,
        reviewed_summary_sha256=hashlib.sha256(args.proposal.read_bytes()).hexdigest(),
        review_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        method="Independent pandas daily medians, monthly medians and NumPy annual quantiles; no reuse of stability aggregation helper",
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
