#!/usr/bin/env python3
"""Independent NumPy/pandas verification of DuckDB-derived public aggregates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads((args.run/'summary.proposed.json').read_text())
    files = {market: args.run/f'features-{market}.parquet' for market in ['US','HK','A-share','JP']}
    dates = {}
    for market, path in files.items():
        available = set()
        reasons = {}
        count = 0
        fx_violations = 0
        for batch in pq.ParquetFile(path).iter_batches(columns=['date','eligible','exclusion_reason','fx_date'],batch_size=100000):
            frame = batch.to_pandas()
            count += len(frame)
            reasons_in_batch = frame.exclusion_reason.fillna('included').value_counts().to_dict()
            for key, value in reasons_in_batch.items():
                reasons[key] = reasons.get(key,0)+int(value)
            eligible = frame.loc[frame.eligible]
            available.update(eligible.date)
            fx_violations += int((eligible.fx_date>=eligible.date).sum())
        assert fx_violations==0
        profile=summary['source_profiles'][market]
        assert count==profile['source_rows']
        assert reasons==profile['exclusions']
        dates[market]=available
    checked_cells=0
    checked_observations=0
    collections=[{'markets':[market], 'common_start':market['as_of'], 'common_end':market['as_of'],
                  'included_markets':[market['market']]} for market in summary['markets']]
    collections.extend(summary['periods'])
    for period in collections:
        included=period['included_markets']
        first=pd.Timestamp(period['common_start']).date()
        last=pd.Timestamp(period['common_end']).date()
        common=set.intersection(*(dates[market] for market in included))
        common={value for value in common if first<=value<=last}
        assert common
        if 'common_dates' in period:
            assert len(common)==period['common_dates']
        for item in period['markets']:
            buckets=[dict(values=[],medians=[],stocks=set(),n=0,zeros=0) for _ in range(5)]
            for batch in pq.ParquetFile(files[item['market']]).iter_batches(
                    columns=['date','eligible','symbol','market_cap_usd','adv20_usd','median20_usd'],batch_size=100000):
                frame=batch.to_pandas()
                frame=frame.loc[frame.eligible & frame.date.isin(common)]
                if frame.empty:
                    continue
                codes=np.searchsorted([1e7,1e8,1e9,1e10],frame.market_cap_usd.to_numpy(),side='right')
                for code in range(5):
                    selected=frame.loc[codes==code]
                    if selected.empty:
                        continue
                    entry=buckets[code]
                    entry['values'].append(selected.adv20_usd.to_numpy())
                    entry['medians'].append(selected.median20_usd.to_numpy())
                    entry['stocks'].update(selected.symbol)
                    entry['n']+=len(selected)
                    entry['zeros']+=int(selected.adv20_usd.eq(0).sum())
            assert sum(b['n'] for b in buckets)==item['eligible_observations']
            checked_observations+=item['eligible_observations']
            for expected, actual in zip(item['buckets'], buckets):
                assert actual['n']==expected['observations']
                assert len(actual['stocks'])==expected['count']
                checked_cells+=2
                for source, prefix in [('values',''),('medians','median20_')]:
                    values=np.concatenate(actual[source]) if actual[source] else np.array([])
                    for metric, func in [('median_usd',np.median),('mean_usd',np.mean),('p10_usd',lambda x:np.quantile(x,.1)),('p25_usd',lambda x:np.quantile(x,.25)),('p75_usd',lambda x:np.quantile(x,.75)),('p90_usd',lambda x:np.quantile(x,.9))]:
                        value=expected[prefix+metric]
                        if not len(values):
                            assert value is None
                        else:
                            assert np.isclose(func(values),value,rtol=1e-10,atol=1e-5), (item['market'],expected['label'],metric)
                        checked_cells+=1
                assert expected['zero_adv20_observations']==actual['zeros']
                zero_share=actual['zeros']/actual['n'] if actual['n'] else None
                assert (expected['zero_adv20_share'] is None if zero_share is None else np.isclose(expected['zero_adv20_share'],zero_share))
                checked_cells+=2
    result=dict(schema_version='liquidity.independent-review.v1',
                reviewed_summary_sha256=hashlib.sha256((args.run/'summary.proposed.json').read_bytes()).hexdigest(),
                review_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                aggregate_cells_reconciled=checked_cells,security_day_observations_checked=checked_observations,
                count_and_reason_conservation=True,strict_prior_fx_checked=True,
                full_raw_warehouse_audited=False,actual_execution_calibrated=False)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
