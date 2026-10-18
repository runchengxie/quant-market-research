#!/usr/bin/env python3
"""Independently verify source joins and annual frozen-name budget statistics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    a = p.parse_args()
    run = a.run
    if run.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("review output must remain external")
    inputs = json.loads((run / "inputs.private.json").read_text())
    raw = (run / "summary.proposed.json").read_bytes()
    out = json.loads(raw)
    receipts = out["source_receipts"]
    assert sha(inputs["features"]) == out["feature_sha256"]
    assert sha(inputs["suspensions"]) == next(
        r["sha256"] for r in receipts if r["source"] == "suspensions"
    )
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    con.execute("SET temp_directory='" + str(run / "review-spill").replace("'", "''") + "'")
    con.read_parquet(inputs["features"]).create_view("f")
    con.read_parquet(str(run / "paths.private.parquet")).create_view("p")
    for label in ["daily", "limit"]:
        files = []
        for r in receipts:
            if r["source"] != label:
                continue
            path = Path(inputs[label + "_root"]) / ("trade_date=" + r["date"]) / "part.parquet"
            assert sha(path) == r["sha256"]
            files.append(str(path))
        con.read_parquet(files, hive_partitioning=False).create_view(label)
    con.read_parquet(inputs["suspensions"]).create_view("susp")
    # Rebuild full native-source join independently of the path-builder function.
    con.execute("""CREATE TEMP TABLE check_paths AS WITH suspensions AS (
      SELECT ts_code,trade_date,bool_or(suspend_type='S' AND coalesce(trim(suspend_timing),'')='') fs
      FROM susp GROUP BY ts_code,trade_date),
      fx AS (SELECT date,min(usd_per_native) rate FROM f GROUP BY date)
      SELECT p.formation,p.symbol,p.h,p.bucket,p.year,p.adv20_usd,p.date,
        d.amount,d.low,d.high,l.down_limit,coalesce(s.fs,false) fs,fx.rate,
        CASE WHEN coalesce(s.fs,false) AND d.amount>0 AND isfinite(d.amount) THEN 'suspension_conflict'
        WHEN coalesce(s.fs,false) THEN 'full_suspension'
        WHEN d.amount IS NULL OR isnan(d.amount) THEN 'missing_daily'
        WHEN NOT isfinite(d.amount) OR d.amount<0 THEN 'invalid_daily'
        WHEN d.low IS NULL OR d.high IS NULL OR NOT isfinite(d.low) OR NOT isfinite(d.high) OR d.low<=0 OR d.high<d.low THEN 'invalid_price'
        WHEN l.down_limit IS NULL OR NOT isfinite(l.down_limit) OR l.down_limit<=0 THEN 'unknown_limit'
        WHEN d.low<l.down_limit-.011 THEN 'price_limit_conflict'
        WHEN d.low<=l.down_limit+.005 THEN 'lower_touch' ELSE 'credited' END state
      FROM p LEFT JOIN daily d ON p.symbol=d.ts_code AND strftime(p.date,'%Y%m%d')=d.trade_date
      LEFT JOIN "limit" l ON p.symbol=l.ts_code AND strftime(p.date,'%Y%m%d')=l.trade_date
      LEFT JOIN suspensions s ON p.symbol=s.ts_code AND strftime(p.date,'%Y%m%d')=s.trade_date
      LEFT JOIN fx ON p.date=fx.date""")
    assert (
        con.execute("SELECT count(*) FROM check_paths").fetchone()[0] == out["quality"]["path_rows"]
    )
    con.execute("""CREATE TEMP TABLE checked AS SELECT *,
       CASE WHEN state='full_suspension' THEN 0 WHEN state IN ('missing_daily','invalid_daily','suspension_conflict') THEN NULL ELSE amount*1000*rate END raw,
       CASE WHEN state IN ('full_suspension','lower_touch') THEN 0 WHEN state='credited' THEN amount*1000*rate ELSE NULL END guarded
       FROM check_paths""")
    for col in ["amount", "low", "high", "down_limit", "state"]:
        assert (
            con.execute(
                f"SELECT count(*) FROM p JOIN checked c USING(formation,symbol,h) WHERE p.{col} IS DISTINCT FROM c.{col}"
            ).fetchone()[0]
            == 0
        ), col
    for col in ["raw", "guarded"]:
        assert (
            con.execute(f"""SELECT count(*) FROM p JOIN checked c USING(formation,symbol,h)
          WHERE (p.{col} IS NULL)<>(c.{col} IS NULL) OR abs(p.{col}-c.{col})>1e-9*greatest(1,abs(c.{col}))""").fetchone()[
                0
            ]
            == 0
        ), col
    data = con.execute("SELECT * FROM checked ORDER BY formation,symbol,h").fetchdf()
    # Reconstruct original membership and following source sessions via pandas.
    calendar = con.execute("SELECT DISTINCT date FROM f ORDER BY date").fetchdf().date
    ends = pd.DataFrame({"date": calendar})
    ends = (
        ends.loc[ends.date.dt.year.between(2024, 2025)]
        .groupby(ends.loc[ends.date.dt.year.between(2024, 2025), "date"].dt.to_period("M"))
        .date.max()
    )
    form = con.execute(
        "SELECT date,symbol,market_cap_usd,adv20_usd FROM f WHERE eligible AND date IN (SELECT DISTINCT formation FROM p)"
    ).fetchdf()
    actual = data.loc[data.h == 1].copy()
    assert set(actual.formation) == set(ends.tolist())
    assert set(zip(actual.formation, actual.symbol)) == set(zip(form.date, form.symbol))
    form["bucket"] = np.digitize(form.market_cap_usd, [1e7, 1e8, 1e9, 1e10])
    joined = actual.merge(
        form,
        left_on=["formation", "symbol"],
        right_on=["date", "symbol"],
        validate="one_to_one",
        suffixes=("", "_f"),
    )
    assert (joined.bucket == joined.bucket_f).all()
    assert np.allclose(joined.adv20_usd, joined.adv20_usd_f)
    positions = {d: i for i, d in enumerate(calendar)}
    for formation, g in data.groupby("formation"):
        expect = list(calendar.iloc[positions[formation] + 1 : positions[formation] + 21])
        assert len(expect) == 20
        for h, date in enumerate(expect, 1):
            assert (g.loc[g.h == h, "date"] == date).all()
        assert g.groupby("symbol").size().eq(20).all()
    checks = 0
    for row in out["rows"]:
        g = data.loc[(data.year == row["year"]) & (data.bucket == row["bucket"])]
        wide = g.pivot(index=["formation", "symbol"], columns="h", values=row["mode"]).iloc[
            :, : row["horizon"]
        ]
        credits = wide.fillna(0).cumsum(axis=1) * row["participation"]
        reached = credits.ge(row["position_usd"])
        covered = reached.iloc[:, -1]
        unknown = wide.isna().any(axis=1) & ~covered
        remain = (1 - credits.iloc[:, -1] / row["position_usd"]).clip(lower=0)
        first = reached.loc[covered].apply(lambda r: int(r.index[r][0]), axis=1)
        n = len(wide)
        vals = dict(
            stocks=n,
            covered=int(covered.sum()),
            unresolved=int(unknown.sum()),
            not_covered=int((~covered & ~unknown).sum()),
            formations=g.formation.nunique(),
            covered_day_p50=float(first.quantile(0.5)) if len(first) else None,
            covered_day_p95=float(first.quantile(0.95)) if len(first) else None,
            all_names_day_max=int(first.max()) if len(first) == n else None,
            uncredited_fraction=float(remain.mean()),
            top_decile_uncredited_share=float(
                remain.nlargest(int(np.ceil(0.1 * n))).sum() / remain.sum()
            )
            if remain.sum() > 0
            else None,
        )
        adv = g.loc[g.h == 1].adv20_usd
        vals["static_covered"] = int(
            (adv * row["participation"] * row["horizon"] >= row["position_usd"]).sum()
        )
        for key, value in vals.items():
            got = row[key]
            assert (got is None and value is None) or (
                got is not None
                and value is not None
                and np.isclose(got, value, rtol=1e-10, atol=1e-10)
            ), (key, got, value, row)
            checks += 1
    review = dict(
        schema_version="liquidity.exit-review.v1",
        passed=True,
        reviewed_summary_sha256=hashlib.sha256(raw).hexdigest(),
        review_code_sha256=sha(Path(__file__)),
        aggregate_cells_checked=checks,
        raw_path_rows_checked=len(data),
        formation_dates_checked=len(ends),
        source_partitions_checked=sum(r["source"] in ["daily", "limit"] for r in receipts),
        method="Independent raw-source SQL classification, pandas frozen membership/session reconstruction and pivoted cumulative-budget statistics.",
    )
    (run / "independent-review.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps(review))


if __name__ == "__main__":
    main()
