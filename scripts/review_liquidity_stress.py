#!/usr/bin/env python3
"""Independent array-based frozen-cohort review and SQL minute-window reconstruction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pyarrow.parquet as pq


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def near(actual, expected):
    if expected is None or pd.isna(expected):
        assert actual is None or pd.isna(actual)
    else:
        assert np.isclose(actual, expected, rtol=1e-10, atol=1e-7), (actual, expected)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["features", "proposal", "minute-root", "daily-root", "output"]:
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    summary = json.loads(a.proposal.read_text())
    checked = 0
    assert sha(a.features) == summary["feature_sha256"]
    frame = pq.read_table(
        a.features, columns=["date", "symbol", "eligible", "market_cap_usd", "adv20_usd"]
    ).to_pandas(date_as_object=False)
    assert not frame.duplicated(["date", "symbol"]).any()
    di, dates = pd.factorize(frame.date, sort=True)
    si, symbols = pd.factorize(frame.symbol, sort=True)
    states = np.full((len(dates), len(symbols)), -2, dtype=np.int8)
    adv = np.full(states.shape, np.nan)
    states[di, si] = np.where(
        frame.eligible,
        np.searchsorted([1e7, 1e8, 1e9, 1e10], frame.market_cap_usd, side="right"),
        -1,
    )
    adv[di[frame.eligible], si[frame.eligible]] = frame.loc[frame.eligible, "adv20_usd"]
    del frame
    daily = []
    last_month = dates[-1].to_period("M")
    valid = (states >= 0).sum(axis=1)
    for i, day in enumerate(dates):
        if day.to_period("M") >= last_month or valid[i] < 100:
            continue
        for b in range(5):
            values = adv[i, states[i] == b]
            daily.append(
                dict(
                    date=day,
                    year=day.year,
                    month=day.strftime("%Y-%m"),
                    bucket=b,
                    n=len(values),
                    value=float(np.median(values)) if len(values) else np.nan,
                )
            )
    daily = pd.DataFrame(daily)
    months = []
    for (year, month, b), g in daily.groupby(["year", "month", "bucket"], sort=True):
        values = g.value.dropna()
        months.append(
            dict(
                year=int(year),
                month=month,
                bucket=int(b),
                market_days=len(g),
                active_days=int(g.n.gt(0).sum()),
                min_daily_stocks=int(g.n.min()),
                median_daily_adv=float(values.median()) if len(values) else np.nan,
                p10=float(values.quantile(0.1)) if len(values) else np.nan,
            )
        )
    months = pd.DataFrame(months)
    original = (
        pd.read_parquet(a.proposal.parent / "monthly.private.parquet")
        .sort_values(["year", "month", "bucket"])
        .reset_index(drop=True)
    )
    assert len(original) == len(months)
    for col in ["market_days", "active_days", "min_daily_stocks", "median_daily_adv", "p10"]:
        for x, y in zip(original[col], months[col], strict=True):
            near(x, y)
            checked += 1
    for row in summary["stress"]:
        group = months.loc[(months.year == row["year"]) & (months.bucket == row["bucket"])]
        good = group.loc[
            (group.active_days >= 10)
            & (group.active_days >= 0.8 * group.market_days)
            & group.median_daily_adv.notna()
        ]
        assert len(good) == row["months"]
        checked += 1
        if len(good) < 6:
            assert row["retained_budget_fraction"] is None
            continue
        ranked = good.sort_values(["median_daily_adv", "month"])
        n = math.ceil(0.2 * len(good))
        assert sorted(ranked.iloc[:n].month.tolist()) == row["stress_months"]
        low = ranked.iloc[:n].median_daily_adv.median()
        normal = ranked.iloc[n:].median_daily_adv.median()
        for key, value in [
            ("stress_median_usd", low),
            ("normal_median_usd", normal),
            ("retained_budget_fraction", low / normal if normal > 0 else None),
        ]:
            near(row[key], value)
            checked += 1
    expected = []
    for i, day in enumerate(dates):
        if day.to_period("M") >= last_month or i + 20 >= len(dates):
            continue
        if i + 1 < len(dates) and dates[i + 1].to_period("M") == day.to_period("M"):
            continue
        for b in range(5):
            members = np.flatnonzero(states[i] == b)
            if not len(members):
                continue
            path = states[i + 1 : i + 21, members]
            last = path[-1]
            coverage = (path >= 0).mean(axis=1)
            base = np.median(adv[i, members])
            ratio = None
            if coverage.min() >= 0.9 and base > 0:
                ratio = float(np.nanmedian(adv[i + 1 : i + 21, members], axis=1).min() / base)
            expected.append(
                dict(
                    formation_date=day,
                    year=day.year,
                    bucket=b,
                    stocks=len(members),
                    retained=int((last == b).sum()),
                    migrated=int(((last >= 0) & (last != b)).sum()),
                    ineligible=int((last == -1).sum()),
                    missing=int((last == -2).sum()),
                    continuous=int((path == b).all(axis=0).sum()),
                    usable_continuous=int((path >= 0).all(axis=0).sum()),
                    min_coverage=float(coverage.min()),
                    frozen_min_ratio=ratio,
                )
            )
    expected = (
        pd.DataFrame(expected).sort_values(["formation_date", "bucket"]).reset_index(drop=True)
    )
    original = (
        pd.read_parquet(a.proposal.parent / "cohorts.private.parquet")
        .sort_values(["formation_date", "bucket"])
        .reset_index(drop=True)
    )
    assert len(expected) == len(original)
    for key in [
        "stocks",
        "retained",
        "migrated",
        "ineligible",
        "missing",
        "continuous",
        "usable_continuous",
        "min_coverage",
        "frozen_min_ratio",
    ]:
        for x, y in zip(original[key], expected[key], strict=True):
            near(x, y)
            checked += 1
    for row in summary["cohorts"]:
        g = expected.loc[(expected.year == row["year"]) & (expected.bucket == row["bucket"])]
        n = g.stocks.sum()
        assert len(g) == row["formations"] and n == row["formation_stock_observations"]
        checked += 2
        for key in [
            "retained",
            "migrated",
            "ineligible",
            "missing",
            "continuous",
            "usable_continuous",
        ]:
            near(row[key + "_fraction"], g[key].sum() / n)
            checked += 1
        near(row["min_coverage"], g.min_coverage.min())
        near(row["frozen_min_ratio_median"], g.frozen_min_ratio.dropna().median())
        checked += 2
        assert row["frozen_valid_formations"] == int(g.frozen_min_ratio.notna().sum())
    del states, adv
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.read_parquet(str(a.features)).create_view("f")
    results = []
    conditions = dict(
        open30="clock>=570 AND clock<600",
        late_morning="clock>=600 AND clock<=690",
        afternoon="clock>=780 AND clock<=900",
        close30="clock>=870 AND clock<=900",
        core="(clock>=600 AND clock<=690) OR (clock>=780 AND clock<870)",
    )
    for receipt, quality in zip(summary["source_receipts"], summary["minute_quality"], strict=True):
        day = receipt["date"]
        minute = a.minute_root / f"trade_date={day}" / "part-00000.parquet"
        daily_path = a.daily_root / f"trade_date={day}" / "part.parquet"
        assert (
            sha(minute) == receipt["minute_sha256"] and sha(daily_path) == receipt["daily_sha256"]
        )
        expressions = ",".join(
            f"CASE WHEN count(*) FILTER(WHERE {condition})>0 THEN sum(amount) FILTER(WHERE {condition})/sum(amount) END {name}"
            for name, condition in conditions.items()
        )
        data = con.execute(
            f"""WITH bars AS (SELECT *,hour(trade_time)*60+minute(trade_time) clock FROM read_parquet(?)),
          totals AS (SELECT ts_code,count(*) bars,sum(amount) total,{expressions} FROM bars GROUP BY ts_code),
          joined AS (SELECT f.market_cap_usd,t.*,d.amount*1000 daily_cny FROM f
            LEFT JOIN totals t ON t.ts_code=f.symbol LEFT JOIN read_parquet(?) d ON d.ts_code=f.symbol
            WHERE f.eligible AND strftime(f.date,'%Y%m%d')=?)
          SELECT CASE WHEN market_cap_usd<1e7 THEN 0 WHEN market_cap_usd<1e8 THEN 1 WHEN market_cap_usd<1e9 THEN 2 WHEN market_cap_usd<1e10 THEN 3 ELSE 4 END bucket,
            {",".join(conditions)} FROM joined WHERE bars>=240 AND total>0 AND daily_cny>0 AND abs(total-daily_cny)/daily_cny<=.01""",
            [str(minute), str(daily_path), day],
        ).fetchdf()
        assert len(data) == quality["accepted"]
        assert sum(quality["reasons"].values()) == quality["eligible_candidates"]
        for name in conditions:
            part = data[["bucket", name]].rename(columns={name: "share"})
            part["year"] = int(day[:4])
            part["date"] = day
            part["window"] = name
            results.append(part)
        print(day, "raw minute windows independently reconciled", flush=True)
    windows = pd.concat(results, ignore_index=True)
    for row in summary["windows"]:
        g = windows.loc[
            (windows.year == row["year"])
            & (windows.bucket == row["bucket"])
            & (windows.window == row["window"])
        ]
        values = g.share.dropna()
        assert (
            len(values) == row["observations"]
            and int(g.share.isna().sum()) == row["missing_window_observations"]
            and g.date.nunique() == row["dates"]
        )
        checked += 3
        for key, q in [("p25", 0.25), ("median", 0.5), ("p75", 0.75)]:
            near(row[key], values.quantile(q) if len(values) else None)
            checked += 1
    result = dict(
        schema_version="liquidity.stress-review.v1",
        passed=True,
        reviewed_summary_sha256=sha(a.proposal),
        review_code_sha256=sha(Path(__file__)),
        aggregate_cells_checked=checked,
        cohort_formations_checked=len(expected),
        raw_minute_dates_checked=len(summary["minute_quality"]),
        method="Independent dense observation-state arrays and NumPy/pandas stress/cohort reconstruction; DuckDB raw-minute window and qualification reconstruction. Missing states remain separate.",
    )
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
