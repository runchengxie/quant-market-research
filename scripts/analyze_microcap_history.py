#!/usr/bin/env python3
"""Reconstruct historical equal-weight small-cap returns from local Tushare parquet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import pandas as pd

from market_research.underwater import build_underwater_episodes, summarize_underwater
from market_research.microcap_history import build_daily_portfolio_returns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True, help="quant-market-data-platform data root")
    parser.add_argument("--output", type=Path, required=True, help="external directory for research outputs")
    parser.add_argument("--start", default="2008-01-02")
    parser.add_argument("--end", default="2026-09-14")
    args = parser.parse_args()
    data_root = args.data_root.expanduser()
    a = data_root / "assets/tushare/a_share"
    historical_daily = a / "daily/a_share_all_20080102_20260821_union_daily/data/**/*.parquet"
    historical_basic = a / "daily_basic/a_share_all_20080102_20260821_union_daily_basic/data/**/*.parquet"
    historical_adj = a / "adj_factor/a_share_all_20080101_20141231_adj_factor/data/**/*.parquet"
    clean_daily = a / "daily/a_share_all_20150101_20260914_daily_clean/data/*.parquet"
    status = data_root / "staging/tushare_constraints_20260802/st_intervals_reconstructed.parquet"
    suspensions = data_root / "staging/tushare_constraints_20260802/suspend_d.parquet"
    instruments = a / "instruments/a_share_all_instruments_latest.parquet"
    for path in (status, suspensions, instruments):
        if not path.exists():
            raise SystemExit(f"required source is missing: {path}")
    args.output.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET disabled_optimizers='statistics_propagation'")
    con.execute(f"""
        CREATE TEMP VIEW old_panel AS
        SELECT d.ts_code AS symbol, try_strptime(CAST(d.trade_date AS VARCHAR), '%Y%m%d')::DATE AS date,
               b.total_mv AS market_cap, d.amount AS amount, d.close*f.adj_factor AS adj_close,
               false AS is_suspended, false AS is_st, 'legacy_tushare'::VARCHAR AS price_source
        FROM read_parquet('{historical_daily}', union_by_name=true) d
        JOIN read_parquet('{historical_basic}', union_by_name=true) b USING(ts_code, trade_date)
        JOIN read_parquet('{historical_adj}', union_by_name=true) f USING(ts_code, trade_date)
        WHERE d.trade_date < 20150101 AND d.close>0 AND f.adj_factor>0
    """)
    con.execute(f"""
        CREATE TEMP VIEW new_panel AS
        SELECT ts_code AS symbol, try_strptime(trade_date, '%Y%m%d')::DATE AS date, total_mv AS market_cap,
               amount, adj_close, is_suspended, is_st, 'daily_clean'::VARCHAR AS price_source
        FROM read_parquet('{clean_daily}', union_by_name=true)
        WHERE try_strptime(trade_date, '%Y%m%d')::DATE >= DATE '2015-01-01'
    """)
    con.execute(f"""
        CREATE TEMP VIEW suspension_events AS
        SELECT ts_code AS symbol, coalesce(try_cast(trade_date AS DATE), try_strptime(trade_date, '%Y%m%d')::DATE) AS date, suspend_type
        FROM read_parquet('{suspensions}')
        WHERE coalesce(try_cast(trade_date AS DATE), try_strptime(trade_date, '%Y%m%d')::DATE) BETWEEN DATE '{args.start}' AND DATE '{args.end}'
    """)
    con.execute(f"""
        CREATE TEMP VIEW market_panel AS
        WITH all_rows AS (SELECT * FROM old_panel UNION ALL SELECT * FROM new_panel),
        instruments AS (SELECT ts_code,
                              coalesce(try_cast(list_date AS DATE), try_strptime(list_date, '%Y%m%d')::DATE) AS list_date,
                              coalesce(try_cast(nullif(delist_date,'None') AS DATE), try_strptime(nullif(delist_date,'None'), '%Y%m%d')::DATE) AS delist_date
                        FROM read_parquet('{instruments}')),
        intervals AS (SELECT ts_code,
                            coalesce(try_cast(interval_start AS DATE), try_strptime(interval_start, '%Y%m%d')::DATE) AS starts,
                            coalesce(try_cast(interval_end AS DATE), try_strptime(interval_end, '%Y%m%d')::DATE) AS ends,
                            coalesce(try_cast(ann_date AS DATE), try_strptime(ann_date, '%Y%m%d')::DATE) AS announced
                     FROM read_parquet('{status}'))
        SELECT p.date, p.symbol, p.market_cap, p.amount, p.adj_close, p.price_source, p.is_suspended,
               (i.ts_code IS NOT NULL AND (i.list_date IS NULL OR i.list_date<=p.date)
                AND (i.delist_date IS NULL OR i.delist_date>p.date)
                AND NOT coalesce(p.is_st, false)
                AND NOT EXISTS (SELECT 1 FROM intervals x WHERE x.ts_code=p.symbol
                  AND x.starts<=p.date AND (x.ends IS NULL OR x.ends>=p.date)
                  AND x.announced<p.date)
                AND p.market_cap>0 AND p.amount>0 AND p.adj_close>0) AS is_eligible
        FROM all_rows p LEFT JOIN instruments i ON i.ts_code=p.symbol
        WHERE p.date BETWEEN DATE '{args.start}' AND DATE '{args.end}'
    """)
    returns = build_daily_portfolio_returns(con, constituent_counts=(50, 100, 200, 400, 800))
    returns.to_csv(args.output / "daily_returns.csv", index=False)
    nav_rows, episode_rows, summaries = [], [], {}
    for count, frame in returns.groupby("constituent_count", sort=True):
        for scenario in ("return_unknown_flat", "return_unknown_total_loss"):
            nav = frame[["return_date", scenario]].rename(columns={"return_date": "date", scenario: "ret"}).copy()
            nav["nav"] = (1 + nav.ret).cumprod()
            nav_rows.extend({"date": r.date, "constituent_count": int(count), "scenario": scenario, "nav": r.nav} for r in nav.itertuples())
            episodes = build_underwater_episodes(nav[["date", "nav"]])
            episodes.insert(0, "scenario", scenario)
            episodes.insert(0, "constituent_count", int(count))
            episode_rows.extend(episodes.to_dict("records"))
            summaries[f"{count}:{scenario}"] = summarize_underwater(episodes)
    pd.DataFrame(nav_rows).to_csv(args.output / "daily_nav.csv", index=False)
    pd.DataFrame(episode_rows).to_csv(args.output / "underwater_episodes.csv", index=False)
    (args.output / "underwater_summary.json").write_text(json.dumps(summaries, indent=2, default=str) + "\n")
    coverage = con.execute("""
        SELECT year(date) AS calendar_year, count(*) AS rows, count(*) FILTER (WHERE market_cap>0) positive_cap,
               count(*) FILTER (WHERE adj_close>0) valid_adj_close,
               count(*) FILTER (WHERE is_eligible) eligible_rows,
               count(*) FILTER (WHERE is_suspended) suspended_rows
        FROM market_panel GROUP BY calendar_year ORDER BY calendar_year
    """).fetchdf()
    coverage.to_csv(args.output / "coverage_by_year.csv", index=False)
    manifest = {"start": args.start, "end": args.end, "sources": [str(historical_daily), str(historical_basic), str(historical_adj), str(clean_daily), str(status), str(suspensions), str(instruments)],
                "formation": "close-date point-in-time market cap; smallest N; equal weight; execute at next observed market close and measure return from execution close through the following market close; skip execution-to-return intervals whose prices cross source vintages",
                "marking": "confirmed S suspension missing close marked stale-flat; unknown missing close separately flat and -100% sensitivity",
                "limitations": "reconstructed ST intervals, local Tushare data, index-style marks; no costs, limit execution, capacity, or cash ledger"}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "return_rows": len(returns), "coverage_years": len(coverage), "summary": summaries}, indent=2, default=str))


if __name__ == "__main__":
    main()
