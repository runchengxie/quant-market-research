#!/usr/bin/env python3
"""External frozen-name sell-budget exploration from reviewed SH/SZ features."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd

from market_research.liquidity_exit import frozen_paths, sell_credit, summarize_budget
from market_research.liquidity_rebuild import BUCKET_LABELS


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["features", "base", "daily-root", "limit-root", "suspensions", "output"]:
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if a.output.resolve().is_relative_to(repo):
        raise ValueError("outputs must remain external")
    a.output.mkdir(parents=True, exist_ok=True)
    feature_sha = sha(a.features)
    base = json.loads(a.base.read_text())
    if feature_sha != next(
        r["sha256"] for r in base["source_receipts"] if r["source_id"] == "a_sh_sz_features"
    ):
        raise ValueError("feature version differs from published SH/SZ scope")
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    con.execute("SET temp_directory='" + str(a.output / "spill").replace("'", "''") + "'")
    con.read_parquet(str(a.features)).create_view("f")
    if con.execute(
        "SELECT count(*) FROM f WHERE market<>'A-share' OR symbol LIKE '%.BJ' OR (usd_per_native IS NOT NULL AND (fx_date>=date OR date-fx_date>7))"
    ).fetchone()[0]:
        raise ValueError("scope or prior-FX validation failed")
    dates = (
        con.execute(
            "SELECT DISTINCT strftime(date,'%Y%m%d') date FROM f WHERE date BETWEEN DATE '2024-01-01' AND DATE '2026-02-01' ORDER BY date"
        )
        .fetchnumpy()["date"]
        .tolist()
    )
    receipts = []
    for label, root in [("daily", a.daily_root), ("limit", a.limit_root)]:
        files = [root / f"trade_date={d}" / "part.parquet" for d in dates]
        for day, path in zip(dates, files):
            if not path.is_file():
                raise ValueError(f"missing {label} partition {day}")
            receipts.append(dict(source=label, date=day, sha256=sha(path)))
        con.read_parquet([str(f) for f in files], hive_partitioning=False).create_view(
            label + "_raw"
        )
    con.execute(
        "CREATE TEMP TABLE d AS SELECT ts_code symbol,strptime(trade_date,'%Y%m%d')::DATE date,amount,low,high FROM daily_raw"
    )
    con.execute(
        "CREATE TEMP TABLE l AS SELECT ts_code symbol,strptime(trade_date,'%Y%m%d')::DATE date,down_limit FROM limit_raw"
    )
    con.read_parquet(str(a.suspensions)).create_view("susp_raw")
    con.execute("""CREATE TEMP TABLE s AS SELECT ts_code symbol,strptime(trade_date,'%Y%m%d')::DATE date,
        bool_or(suspend_type='S' AND (suspend_timing IS NULL OR trim(suspend_timing)='')) full_suspension
        FROM susp_raw GROUP BY ALL""")
    print("Building frozen paths for 2024–2025 month ends", flush=True)
    paths = frozen_paths(con, 2024, 2025)
    paths["year"] = paths.formation.dt.year
    results = [
        sell_credit(v.amount, v.low, v.high, v.down_limit, v.full_suspension)
        for v in paths.itertuples()
    ]
    credits = pd.DataFrame(results, columns=["raw", "guarded", "state"])
    paths = pd.concat([paths.reset_index(drop=True), credits], axis=1)
    for mode in ["raw", "guarded"]:
        paths[mode] = paths[mode] * 1000 * paths.fx
    paths.to_parquet(a.output / "paths.private.parquet", index=False)
    rows = []
    for (year, bucket), g in paths.groupby(["year", "bucket"], sort=True):
        g = g.sort_values(["formation", "symbol", "h"])
        adv = g.loc[g.h.eq(1), "adv20_usd"].to_numpy()
        if len(g) != len(adv) * 20:
            raise ValueError("incomplete frozen path")
        for position in [100000, 1000000]:
            for participation in [0.01, 0.03, 0.05]:
                for horizon in [1, 5, 20]:
                    for mode in ["raw", "guarded"]:
                        values = g[mode].to_numpy().reshape(-1, 20)[:, :horizon]
                        row = dict(
                            year=int(year),
                            bucket=int(bucket),
                            position_usd=position,
                            participation=participation,
                            horizon=horizon,
                            mode=mode,
                            formations=int(g.formation.nunique()),
                            static_covered=int((adv * participation * horizon >= position).sum()),
                            **summarize_budget(values, position, participation),
                        )
                        rows.append(row)
        print(year, bucket, len(adv), "original stock-formations", flush=True)
    summary = dict(
        schema_version="liquidity.exit-exploration.v1",
        feature_sha256=feature_sha,
        historical_pit_eligible=False,
        actual_execution_calibrated=False,
        formation_years=[2024, 2025],
        horizon_sessions=20,
        buckets=list(BUCKET_LABELS),
        rows=rows,
        quality=dict(
            path_rows=len(paths),
            stock_formations=int((paths.h == 1).sum()),
            formation_dates=int(paths.formation.nunique()),
            formation_start=str(paths.formation.min().date()),
            formation_end=str(paths.formation.max().date()),
            future_end=str(paths.date.max().date()),
            states={k: int(v) for k, v in paths.state.value_counts().items()},
        ),
        source_receipts=[
            dict(source="features", sha256=feature_sha),
            dict(source="suspensions", sha256=sha(a.suspensions)),
            *receipts,
        ],
        producer_receipts=[
            dict(source=x, sha256=sha(repo / x))
            for x in ["scripts/build_liquidity_exit.py", "src/market_research/liquidity_exit.py"]
        ],
        methodology=dict(
            formation="All eligible names at each source month end in 2024–2025; original dollar-cap buckets frozen, later eligibility does not drop names.",
            budget="Fixed USD notional per original name, not a share-accounting liquidation or a strategy portfolio. Credit subsequent observed daily native amount × 1000 × strictly prior feature FX × participation.",
            guarded="Full-suspension dates credit zero unless contradicted by positive daily turnover. Any daily lower-limit touch discards the entire day for a conservative sell sensitivity. Other daily turnover is arithmetic only, not evidence of fillability.",
            missing="Unknown daily/limit/price evidence receives no credit and remains unknown. Sufficient known credit can cover a budget despite other missing days; otherwise unknowns remain unresolved.",
            pooling="Annual statistics pool original stock–formation observations. Day percentiles condition on covered names; maximum is missing unless every original name is covered. Top-decile share pools uncredited balances across formations.",
            limits="No fees, shares, board lots, endogenous price impact, price-path inventory valuation, queues or historical receive timestamps. Raw mode ignores price-limit constraints; guarded mode is a sensitivity, not a lower bound on actual execution.",
        ),
        sources=[
            "https://tushare.pro/document/2?doc_id=27",
            "https://tushare.pro/document/2?doc_id=183",
            "https://tushare.pro/document/2?doc_id=214",
        ],
    )
    write(a.output / "summary.proposed.json", summary)
    write(
        a.output / "inputs.private.json",
        dict(
            features=str(a.features.resolve()),
            daily_root=str(a.daily_root.resolve()),
            limit_root=str(a.limit_root.resolve()),
            suspensions=str(a.suspensions.resolve()),
        ),
    )
    print("Proposal ready for independent review", flush=True)


if __name__ == "__main__":
    main()
