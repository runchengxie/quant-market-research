#!/usr/bin/env python3
"""Independently verify quintile membership and all public statistics with pandas/NumPy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from market_research.liquidity_relative_validation import verify_absolute_frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    args = parser.parse_args()
    raw = args.proposal.read_bytes()
    summary = json.loads(raw)
    base_raw = args.base.read_bytes()
    base = json.loads(base_raw)
    assert hashlib.sha256(base_raw).hexdigest() == summary["absolute_summary_sha256"]
    actual_receipts = []
    signatures = {}
    for m in summary["markets"]:
        p = args.features / f"features-{m['market']}.parquet"
        signatures[m["market"]] = (p.stat().st_size, p.stat().st_mtime_ns)
        h = hashlib.sha256()
        with p.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        actual_receipts.append(
            dict(market=m["market"], bytes=p.stat().st_size, sha256=h.hexdigest())
        )
    assert actual_receipts == summary["feature_receipts"], "feature checksum mismatch"
    absolute_views = [{"markets": [m]} for m in base["markets"]] + base["periods"]
    absolute_cells = 0
    cells = 0
    views = [
        dict(
            markets=[m],
            common_start=m["as_of"],
            common_end=m["as_of"],
            included_markets=[m["market"]],
        )
        for m in summary["markets"]
    ] + summary["periods"]
    dates = {}
    # Read only calendar/eligibility first so each multi-market view has exact shared dates.
    for m in summary["markets"]:
        frame = pq.read_table(
            args.features / f"features-{m['market']}.parquet", columns=["date", "eligible"]
        ).to_pandas()
        dates[m["market"]] = set(frame.loc[frame.eligible, "date"])
    checked = 0
    for market in dates:
        frame = pq.read_table(
            args.features / f"features-{market}.parquet",
            columns=["date", "symbol", "eligible", "market_cap_usd", "adv20_usd", "median20_usd"],
        ).to_pandas()
        frame = (
            frame.loc[frame.eligible]
            .sort_values(["date", "market_cap_usd", "symbol"], kind="mergesort")
            .reset_index(drop=True)
        )
        groups = frame.groupby("date", sort=False)
        position = groups.cumcount().to_numpy()
        n = groups.symbol.transform("size").to_numpy()
        q, r = n // 5, n % 5
        cutoff = (q + 1) * r
        frame["bucket"] = np.where(
            position < cutoff, position // (q + 1), r + (position - cutoff) // np.maximum(q, 1)
        )
        for view_index, view in enumerate(views):
            item = next((m for m in view["markets"] if m["market"] == market), None)
            if item is None:
                continue
            common = set.intersection(*(dates[m] for m in view["included_markets"]))
            first = pd.Timestamp(view["common_start"]).date()
            last = pd.Timestamp(view["common_end"]).date()
            common = {d for d in common if first <= d <= last}
            selected = frame.loc[frame.date.isin(common)]
            if "common_dates" in view:
                assert len(common) == view["common_dates"]
            assert len(selected) == item["eligible_observations"]
            assert selected.symbol.nunique() == item["unique_stocks"]
            checked += len(selected)
            original = next(
                m for m in absolute_views[view_index]["markets"] if m["market"] == market
            )
            absolute_cells += verify_absolute_frame(selected, original)
            for index, b in enumerate(item["buckets"]):
                rows = selected.loc[selected.bucket.eq(index)]
                assert len(rows) == b["observations"] and rows.symbol.nunique() == b["count"]
                cells += 2
                for col, prefix in [("adv20_usd", ""), ("median20_usd", "median20_")]:
                    values = rows[col].to_numpy()
                    for key, fn in [
                        ("median_usd", np.median),
                        ("mean_usd", np.mean),
                        ("p10_usd", lambda a: np.quantile(a, 0.1)),
                        ("p25_usd", lambda a: np.quantile(a, 0.25)),
                        ("p75_usd", lambda a: np.quantile(a, 0.75)),
                        ("p90_usd", lambda a: np.quantile(a, 0.9)),
                    ]:
                        actual = b[prefix + key]
                        assert (
                            actual is None
                            if not len(values)
                            else np.isclose(actual, fn(values), rtol=1e-10, atol=1e-6)
                        )
                        cells += 1
                zero_count = int(rows.adv20_usd.eq(0).sum())
                assert b["zero_adv20_observations"] == zero_count
                zero_share = zero_count / len(rows) if len(rows) else None
                assert (
                    b["zero_adv20_share"] is None
                    if zero_share is None
                    else np.isclose(b["zero_adv20_share"], zero_share)
                )
                cells += 2
                for key, fn in [("cap_min_usd", np.min), ("cap_max_usd", np.max)]:
                    actual = b[key]
                    assert (
                        actual is None
                        if rows.empty
                        else np.isclose(actual, fn(rows.market_cap_usd), rtol=1e-10, atol=1e-6)
                    )
                    cells += 1
        print(market, "independently reconciled", flush=True)
        p = args.features / f"features-{market}.parquet"
        assert signatures[market] == (p.stat().st_size, p.stat().st_mtime_ns), (
            "feature changed during review"
        )
        del frame
    receipt = dict(
        schema_version="liquidity.relative-review.v1",
        reviewed_summary_sha256=hashlib.sha256(raw).hexdigest(),
        review_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        aggregate_cells_reconciled=cells,
        absolute_aggregate_cells_reconciled=absolute_cells,
        feature_checksums_verified=True,
        base_verification_code_sha256=hashlib.sha256(
            (
                Path(__file__).resolve().parents[1]
                / "src/market_research/liquidity_relative_validation.py"
            ).read_bytes()
        ).hexdigest(),
        security_day_entries_across_overlapping_views=checked,
        independent_daily_membership_checked=True,
        full_raw_warehouse_audited=False,
    )
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
