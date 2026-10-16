#!/usr/bin/env python3
"""Independently recompute sampled source windows in pandas; publish no securities."""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    cfg=json.loads(args.config.read_text())
    sources={k:sorted(glob.glob(v)) for k,v in cfg['sources'].items()}
    summary=json.loads((args.run/'summary.proposed.json').read_text())
    observation=next(p['common_end'] for p in summary['periods'] if p['period']=='common snapshot')
    con=duckdb.connect()
    con.execute('SET threads=2')
    con.execute("SET memory_limit='1GB'")
    fx=pd.read_csv(sources['fx'][0],compression='zip')
    fx.columns=fx.columns.str.strip()
    fx=fx.loc[pd.to_datetime(fx.Date)<pd.Timestamp(observation)].sort_values('Date').iloc[-1]
    results=[]
    for market,currency in [('US','USD'),('HK','HKD'),('A-share','CNY'),('JP','JPY')]:
        feature=args.run/f'features-{market}.parquet'
        target=con.execute('SELECT * FROM read_parquet(?) WHERE eligible AND date=? ORDER BY market_cap_usd', [str(feature),observation]).fetchdf()
        indexes=np.linspace(0,len(target)-1,min(12,len(target)),dtype=int)
        chosen=target.iloc[indexes]
        symbols=chosen.symbol.tolist()
        common_dates=con.execute("SELECT DISTINCT date FROM read_parquet(?) WHERE date<? AND exclusion_reason IS DISTINCT FROM 'sparse_non_market_date' ORDER BY date DESC LIMIT 20",[str(feature),observation]).fetchdf().date.tolist()
        first=min(common_dates)
        placeholders=','.join('?' for _ in symbols)
        if market=='US':
            raw=con.execute(f'''SELECT Ticker symbol,try_cast(Date AS DATE) date,
              try_cast(Close AS DOUBLE)*try_cast(Volume AS DOUBLE) turnover,
              try_cast(Close AS DOUBLE)*try_cast("Shares Outstanding" AS DOUBLE) cap
              FROM read_csv(?,delim=';',header=true,all_varchar=true)
              WHERE Ticker IN ({placeholders}) AND try_cast(Date AS DATE)>=? AND try_cast(Date AS DATE)<?''', [sources['us'][0],*symbols,first,observation]).fetchdf()
        elif market=='A-share':
            files=[p for p in sources['a_clean'] if Path(p).stem in symbols]
            raw=con.execute('''SELECT ts_code symbol,try_strptime(trade_date,'%Y%m%d')::DATE date,
              amount*1000. turnover,total_mv*10000. cap FROM read_parquet(?)
              WHERE try_strptime(trade_date,'%Y%m%d')::DATE>=? AND try_strptime(trade_date,'%Y%m%d')::DATE<?''',[files,first,observation]).fetchdf()
        elif market=='HK':
            daily=[p for p in sources['hk_daily'] if Path(p).stem in symbols]
            value=[p for p in sources['hk_value'] if Path(p).stem in symbols]
            raw=con.execute('''SELECT d.symbol,try_strptime(d.trade_date,'%Y%m%d')::DATE date,
              d.total_turnover turnover,v.hk_total_market_val cap FROM read_parquet(?) d
              JOIN read_parquet(?) v USING(symbol,trade_date)
              WHERE try_strptime(d.trade_date,'%Y%m%d')::DATE>=? AND try_strptime(d.trade_date,'%Y%m%d')::DATE<?''',[daily,value,first,observation]).fetchdf()
        else:
            raw=con.execute(f'''SELECT lpad(d.Code,5,'0') symbol,d.Date date,d.Va turnover,d.C*s.shares_outstanding cap
              FROM read_parquet(?) d JOIN read_parquet(?) s ON lpad(d.Code,5,'0')=s.symbol AND d.Date=s.date
              WHERE lpad(d.Code,5,'0') IN ({placeholders}) AND d.Date>=? AND d.Date<?''',[sources['jp_daily'],sources['jp_shares'][0],*symbols,first,observation]).fetchdf()
        raw['date']=pd.to_datetime(raw.date)
        rate=float(fx.USD)/float(fx[currency])
        cells=0
        for _, row in chosen.iterrows():
            window=raw.loc[raw.symbol.eq(row.symbol)&raw.date.isin(common_dates)].sort_values('date')
            assert len(window)==20 and window.date.nunique()==20,market
            expected=[window.turnover.mean(),window.turnover.median(),window.cap.iloc[-1],rate]
            actual=[row.adv20_native,row.median20_native,row.market_cap_native,row.usd_per_native]
            assert np.allclose(expected,actual,rtol=1e-10,atol=1e-5),market
            assert np.allclose([expected[0]*rate,expected[1]*rate,expected[2]*rate],
                [row.adv20_usd,row.median20_usd,row.market_cap_usd],rtol=1e-10,atol=1e-5),market
            cells+=7
        results.append(dict(market=market,observation_date=observation,stocks_checked=len(chosen),
                            prior_source_rows_checked=len(chosen)*20,numeric_cells_reconciled=cells))
    report=dict(schema_version='liquidity.source-window-review.v1',markets=results,
                code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                full_warehouse_audited=False,eligibility_vintages_verified=False)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    main()
