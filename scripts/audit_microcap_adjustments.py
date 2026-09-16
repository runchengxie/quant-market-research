#!/usr/bin/env python3
"""Audit stock-level adjusted-price jumps in early microcap baskets.

This is a diagnostic, not a return publication pipeline. It requires the
external quant-market-data-platform Tushare parquet assets and writes its
receipt outside the repository.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import duckdb

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--start', default='2013-01-01')
    ap.add_argument('--end', default='2016-12-31')
    a=ap.parse_args(); root=a.data_root.expanduser(); base=root/'assets/tushare/a_share'
    daily=str(base/'daily/a_share_all_20080102_20260821_union_daily/data/**/*.parquet')
    basic=str(base/'daily_basic/a_share_all_20080102_20260821_union_daily_basic/data/**/*.parquet')
    adj=str(base/'adj_factor/a_share_all_20080101_20141231_adj_factor/data/**/*.parquet')
    con=duckdb.connect()
    con.execute(f"""CREATE OR REPLACE TABLE panel AS SELECT d.ts_code symbol, try_strptime(cast(d.trade_date as varchar),'%Y%m%d') date, d.close raw_close, f.adj_factor, d.close*f.adj_factor adj_close, b.total_mv, d.amount FROM read_parquet('{daily}',union_by_name=true) d JOIN read_parquet('{basic}',union_by_name=true) b USING(ts_code,trade_date) JOIN read_parquet('{adj}',union_by_name=true) f USING(ts_code,trade_date) WHERE d.trade_date BETWEEN strftime(CAST(? AS DATE), '%Y%m%d')::INTEGER AND strftime(CAST(? AS DATE), '%Y%m%d')::INTEGER AND d.close>0 AND f.adj_factor>0 AND b.total_mv>0 AND d.amount>0""", [a.start,a.end])
    con.execute("CREATE OR REPLACE TABLE dts AS SELECT date, lead(date,1) over(order by date) entry_date, lead(date,2) over(order by date) return_date FROM (select distinct date from panel)")
    con.execute("CREATE OR REPLACE TABLE ranked AS SELECT p.date formation_date,d.entry_date,d.return_date,p.symbol,p.total_mv,p.adj_factor,p.raw_close,p.adj_close,row_number() over(partition by p.date order by p.total_mv,p.symbol) rn FROM panel p join dts d using(date)")
    results=[]
    for n in [50,100,200,400,800]:
        con.execute(f"CREATE OR REPLACE TABLE h AS SELECT r.*,e.adj_close entry_close,x.adj_close exit_close,(x.adj_close/e.adj_close-1) ret FROM ranked r LEFT JOIN panel e ON e.symbol=r.symbol AND e.date=r.entry_date LEFT JOIN panel x ON x.symbol=r.symbol AND x.date=r.return_date WHERE r.rn<={n} AND e.adj_close>0 AND x.adj_close>0")
        annual=con.execute("SELECT year(formation_date) AS calendar_year,exp(sum(ln(1+ret)))-1 AS cumulative_return FROM (SELECT formation_date,avg(ret) ret FROM h GROUP BY formation_date HAVING count(*)=?) GROUP BY calendar_year ORDER BY calendar_year",[n]).fetchall()
        jumps=con.execute("SELECT symbol,formation_date,adj_factor,prev,ratio FROM (SELECT symbol,formation_date,adj_factor,lag(adj_factor) OVER (PARTITION BY symbol ORDER BY formation_date) prev,adj_factor/nullif(lag(adj_factor) OVER (PARTITION BY symbol ORDER BY formation_date),0) ratio FROM h) WHERE ratio>1.5 OR ratio<0.667 ORDER BY abs(ln(ratio)) DESC LIMIT 20").fetchall()
        results.append({'constituent_count':n,'annual_returns':annual,'adjusted_factor_jumps':jumps,'observations':con.execute('select count(*) from h').fetchone()[0]})
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps({'start':a.start,'end':a.end,'method':'diagnostic only; no status, delist or execution constraints','results':results},default=str,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__': main()
