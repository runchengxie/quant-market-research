#!/usr/bin/env python3
"""Independent pandas/NumPy check of lifecycle sensitivity and daily stock limits."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--master", type=Path, nargs="+", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    audit = json.loads((a.run / "universe-sensitivity.json").read_text())
    limits = json.loads((a.run / "scenario-limits.json").read_text())
    master = pd.concat([pd.read_parquet(x) for x in a.master], ignore_index=True).set_index(
        "ts_code"
    )
    assert not master.index.duplicated().any()
    dates = {}
    for market in ["US", "HK", "A-share", "JP"]:
        frame = pq.read_table(
            a.run / f"features-{market}.parquet", columns=["date", "eligible"]
        ).to_pandas(date_as_object=False)
        dates[market] = set(frame.loc[frame.eligible, "date"])
    checked = 0
    annual = []
    for market in dates:
        columns = ["date", "eligible", "market_cap_usd"]
        if market == "A-share":
            columns += ["symbol", "adv20_usd"]
        frame = pq.read_table(a.run / f"features-{market}.parquet", columns=columns).to_pandas(
            date_as_object=False
        )
        calendar = sorted(frame.date.unique())
        prior = dict(zip(calendar[1:], calendar[:-1]))
        frame = frame.loc[frame.eligible].copy()
        frame["bucket"] = np.searchsorted([1e7, 1e8, 1e9, 1e10], frame.market_cap_usd, side="right")
        if market == "A-share":
            frame["prior"] = frame.date.map(prior)
            frame["listed"] = pd.to_datetime(
                frame.symbol.map(master.list_date), format="%Y%m%d", errors="coerce"
            )
            frame["delisted"] = pd.to_datetime(
                frame.symbol.map(master.delist_date), format="%Y%m%d", errors="coerce"
            )
            frame["lifecycle"] = (frame.listed <= frame.prior) & (
                frame.delisted.isna() | (frame.delisted > frame.prior)
            )
            for year, group in frame.groupby(frame.date.dt.year):
                annual.append(
                    dict(
                        year=int(year),
                        base_observations=len(group),
                        lifecycle_observations=int(group.lifecycle.sum()),
                    )
                )
            for view in audit["periods"]:
                # Take exact common dates from the limits view, never infer continuity from bounds.
                template = next(
                    v
                    for v in limits["views"]
                    if v["period"] == view["period"]
                    and any(r["market"] == "A-share" for r in v["markets"])
                )
                markets = [r["market"] for r in template["markets"]]
                common = set.intersection(*(dates[m] for m in markets))
                common = {
                    d
                    for d in common
                    if pd.Timestamp(view["common_start"]) <= d <= pd.Timestamp(view["common_end"])
                }
                assert len(common) == view["common_dates"]
                selected = frame.loc[frame.date.isin(common)]
                for name, subset in [
                    ("base", selected),
                    ("lifecycle", selected.loc[selected.lifecycle]),
                ]:
                    expected = view[name]
                    assert len(subset) == expected["eligible_observations"]
                    for i, b in enumerate(expected["buckets"]):
                        g = subset.loc[subset.bucket.eq(i)]
                        assert len(g) == b["observations"] and g.symbol.nunique() == b["count"]
                        for key, fn in [("median_usd", np.median), ("mean_usd", np.mean)]:
                            assert (
                                b[key] is None
                                if g.empty
                                else np.isclose(fn(g.adv20_usd), b[key], rtol=1e-10, atol=1e-5)
                            )
                        checked += 4
        counts = (
            frame.groupby(["date", "bucket"])
            .size()
            .unstack(fill_value=0)
            .reindex(columns=range(5), fill_value=0)
        )
        for view in limits["views"]:
            row = next((r for r in view["markets"] if r["market"] == market), None)
            if row is None:
                continue
            common = set.intersection(*(dates[r["market"]] for r in view["markets"]))
            common = sorted(
                d
                for d in common
                if pd.Timestamp(view["common_start"]) <= d <= pd.Timestamp(view["common_end"])
            )
            daily = counts.reindex(index=common, fill_value=0)
            assert daily.min().tolist() == row["absolute_min_daily_stocks"]
            total = daily.sum(axis=1).to_numpy()
            assert [int(np.min(total // 5 + (i < total % 5))) for i in range(5)] == row[
                "relative_min_daily_stocks"
            ]
            checked += 10
        del frame

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    result = dict(
        schema_version="liquidity.universe-review.v1",
        aggregate_cells_checked=checked,
        independent_method="pandas lifecycle join and NumPy statistics; daily counts reindexed to exact common calendars including empty groups",
        annual_lifecycle_counts=annual,
        sensitivity_sha256=sha(a.run / "universe-sensitivity.json"),
        scenario_limits_sha256=sha(a.run / "scenario-limits.json"),
        review_code_sha256=sha(Path(__file__)),
        passed=True,
    )
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
