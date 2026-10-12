"""Bounded saved-data fitness audit and snapshot counterfactual execution."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

import duckdb
import pandas as pd
from market_research.studies.ashare_execution_costs.replay import replay_gate, snapshot_path


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError('output must be new or empty')
    con = duckdb.connect(config={'threads': '2', 'memory_limit': '1GB'})
    names = ['orders_20210104_common', 'preopening_orders_20210104_common',
             'trades_20210104_common', 'selected_books_20210104']
    sources = {}
    for name in names:
        path = args.saved / (name + '.parquet')
        sources[name] = {'path': str(path), 'sha256': sha256(path)}
        con.read_parquet(str(path)).create_view(name)
    con.execute('CREATE VIEW all_orders AS SELECT * FROM orders_20210104_common '
                'UNION ALL SELECT * FROM preopening_orders_20210104_common')
    order_profile = con.sql('SELECT OrderType,count(*) n, '
                            'count_if(Price<=0) nonpositive_price FROM all_orders '
                            'GROUP BY OrderType ORDER BY OrderType').df().to_dict('records')
    side_profile = con.sql('SELECT Side,count(*) n, count_if(Price<=0) nonpositive_price, '
                           'count_if(BuyID=0) zero_buy, count_if(SellID=0) zero_sell '
                           'FROM trades_20210104_common GROUP BY Side ORDER BY Side').df().to_dict('records')
    # Reference coverage describes existence, not side/semantics or sequence correctness.
    con.execute('CREATE VIEW unique_ids AS SELECT SecuCode,OrderID,min(time_ms_absolute) t, '
                'count(*) n FROM all_orders GROUP BY SecuCode,OrderID')
    references = con.sql('''SELECT count(*) trade_rows,
      count_if(b.OrderID IS NOT NULL) buy_reference_found,
      count_if(s.OrderID IS NOT NULL) sell_reference_found,
      count_if(b.t>t.time_ms_absolute) buy_reference_after_trade,
      count_if(s.t>t.time_ms_absolute) sell_reference_after_trade,
      count_if(t.Price<=0) special_price_rows
      FROM trades_20210104_common t
      LEFT JOIN unique_ids b ON t.SecuCode=b.SecuCode AND t.BuyID=b.OrderID
      LEFT JOIN unique_ids s ON t.SecuCode=s.SecuCode AND t.SellID=s.OrderID''').df().iloc[0].to_dict()
    duplicates = con.sql('SELECT count_if(n>1) duplicate_security_order_keys, '
                         'sum(n-1) excess_rows FROM unique_ids').df().iloc[0].to_dict()
    ties = con.sql('''SELECT count(*) shared_security_timestamp_pairs FROM
      (SELECT DISTINCT SecuCode,time_ms_absolute FROM all_orders) o JOIN
      (SELECT DISTINCT SecuCode,time_ms_absolute FROM trades_20210104_common) t
      USING(SecuCode,time_ms_absolute)''').df().iloc[0].to_dict()
    per_security = con.sql('''SELECT t.SecuCode,count(*) trade_rows,
      count_if(b.OrderID IS NOT NULL) buy_reference_found,
      count_if(s.OrderID IS NOT NULL) sell_reference_found,
      count_if(b.t>t.time_ms_absolute) buy_reference_after_trade,
      count_if(s.t>t.time_ms_absolute) sell_reference_after_trade
      FROM trades_20210104_common t
      LEFT JOIN unique_ids b ON t.SecuCode=b.SecuCode AND t.BuyID=b.OrderID
      LEFT JOIN unique_ids s ON t.SecuCode=s.SecuCode AND t.SellID=s.OrderID
      GROUP BY t.SecuCode ORDER BY t.SecuCode''').df().to_dict('records')
    sz = [r for r in per_security if int(r['SecuCode']) < 400000]
    sz_n = sum(r['trade_rows'] for r in sz)
    sz_coverage = {'trade_rows': sz_n,
                   'buy_reference_rate': sum(r['buy_reference_found'] for r in sz) / sz_n,
                   'sell_reference_rate': sum(r['sell_reference_found'] for r in sz) / sz_n,
                   'reference_after_trade_count': sum(r['buy_reference_after_trade'] +
                                                     r['sell_reference_after_trade'] for r in sz)}
    stream_clocks = {}
    for stream in names[:3]:
        stream_clocks[stream] = con.sql(f'''SELECT count_if(dt<0) source_clock_backwards
          FROM (SELECT time_ms_absolute-lag(time_ms_absolute) OVER
          (PARTITION BY SecuCode ORDER BY source_row) dt FROM {stream})''').df().iloc[0].to_dict()
    securities = con.sql('''SELECT DISTINCT ticker FROM selected_books_20210104
                          WHERE ticker LIKE '0%' OR ticker LIKE '3%'
                          ORDER BY ticker LIMIT 12''').df().ticker.tolist()
    rows = []
    for ticker in securities:
        path = con.execute('SELECT * FROM selected_books_20210104 WHERE ticker=? '
                           'AND time_ms BETWEEN 0 AND 300000 ORDER BY time_ms,source_row',
                           [ticker]).df()
        if path.empty:
            continue
        for side in ('buy', 'sell'):
            for mode in ('market', 'twap', 'limit_wait'):
                result = snapshot_path(path, quantity=10000, budget_cny=1000000,
                                       mode=mode, side=side)
                result.update(ticker=ticker, day=20210104, horizon_ms=300000)
                rows.append(result)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'private-paths.json').write_text(json.dumps(rows, indent=2)+'\n')
    audit = {'sources': sources, 'order_type_profile': order_profile,
             'trade_side_profile': side_profile, 'references': references,
             'shenzhen_reference_coverage': sz_coverage, 'order_keys': duplicates, 'per_security_references': per_security,
             'source_clock_diagnostics': stream_clocks, 'cross_stream_timestamp_ties': ties,
             'gate': replay_gate(semantics_verified=False, exchange_order_verified=False),
             'saved_order_columns': [r[0] for r in con.execute('DESCRIBE all_orders').fetchall()],
             'provider_version': importlib.metadata.version('quant-platform'),
             'research_source_sha256': {'runner': sha256(Path(__file__)),
                'scenario': sha256(Path(__file__).resolve().parents[1] /
                    'src/market_research/studies/ashare_execution_costs/replay.py')}}
    provider = Path(importlib.metadata.distribution('quant-platform').locate_file(
                    'ticknet/simulator/matching.py'))
    audit['provider_source_sha256'] = sha256(provider)
    (args.output / 'private-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    aggregates = []
    frame = pd.DataFrame(rows)
    for (side, mode), group in frame.groupby(['side', 'mode']):
        aggregates.append({'side': side, 'mode': mode, 'paths': len(group),
                           'full_fill_paths': int((group.remaining_quantity == 0).sum()),
                           'median_fill_fraction': float((group.filled_quantity / 10000).median()),
                           'costs': {key: {'observed_paths': int(group[key].notna().sum()),
                               'conditional_p50': float(group[key].dropna().median())
                               if group[key].notna().any() else None}
                               for key in ('execution_cost_cny', 'opportunity_cost_cny',
                                           'total_shortfall_bp', 'completion_duration_ms')}})
    public = {'schema_version': 2, 'data_quality': audit['gate'],
              'observed_diagnostics': {'shenzhen_reference_coverage': sz_coverage,
                  'shared_security_timestamp_pairs': int(ties['shared_security_timestamp_pairs']),
                  'numeric_order_types_are_unmapped': True},
              'simulation': {'status': 'snapshot_counterfactual_only',
                             'sample_paths': len(securities), 'day': '2021-01-04',
                             'requested_quantity_share': 10000, 'horizon_seconds': 300,
                             'buy_budget_cny': 1000000, 'aggregate_results': aggregates,
                             'participation': {'status': 'unavailable',
                                'reason': 'saved TotalVolume has no audited interval-volume contract or reset/auction treatment for a causal cap',
                                'needed_input': 'verified cumulative-volume units, clock and reset contract with trailing realized-volume baseline'},
                             'assumptions': ['first 12 saved Shenzhen securities in lexical order',
                                'first quote per timestamp; displayed depth refreshes at each clock',
                                'no own-impact, fees, lot rounding, queue reconstruction or participation cap',
                                'TWAP releases five fixed quantity slices at 0,60,120,180,240 seconds; next quote executes',
                                'limit wait uses arrival same-side best price; marketable crossing only',
                                'passive fill lower bound zero; upper bound requested quantity, no inferred cash',
                                'shortfall uses arrival mid and fixed-horizon past mid with 60-second freshness; fees zero excluded',
                                'future quotes are execution outcomes at their clock, never signal features']}}
    (args.output / 'replay.proposed.json').write_text(json.dumps(public, indent=2)+'\n')
    print(json.dumps(public, indent=2))


if __name__ == '__main__':
    main()
