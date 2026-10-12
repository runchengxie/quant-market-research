"""Reconcile saved measurements and refine event diagnostics without rescanning raw L2."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from market_research.output_paths import resolve_output_root
from market_research.studies.ashare_execution_costs.expansion import (
    _source_unchanged, reference_audit, stream_audit, validate_spec,
)
from market_research.studies.ashare_execution_costs.pilot import SIZES, summarize


def event_diagnostics(orders, trades, preopen=None):
    result = {'orders':stream_audit(orders,'order'),'trades':stream_audit(trades,'deal')}
    positive = trades.loc[trades.Price.gt(0) & trades.Volume.gt(0)]
    result['positive_price_trades'] = stream_audit(positive,'deal')
    lookup = orders
    if preopen is not None:
        identity = ['SecuCode','OrderID','time_ms_absolute','Price','Volume','OrderType']
        overlap = orders[identity].merge(preopen[identity].drop_duplicates(),on=identity,how='inner')
        result['preopening_orders'] = stream_audit(preopen,'order')
        result['preopening_overlap_rows'] = len(overlap)
        lookup = pd.concat([orders,preopen],ignore_index=True)
    result['references'] = [reference_audit(lookup,trades,candidate)
                            for candidate in ('OrderID','DBOrderID') if candidate in lookup]
    result['dynamic_replay_gate'] = 'not_established_special_event_semantics_and_queue_order_unverified'
    return result


def review_saved_run(source: Path, output_root: Path):
    output = resolve_output_root({'output_root':str(output_root)})
    output.mkdir(parents=True,exist_ok=False)
    summary_path = source/'summary.json'
    summary = json.loads(summary_path.read_text())
    validate_spec(summary['spec'])
    for receipt in summary['inputs']+summary['daily_inputs']:
        _source_unchanged(receipt)
    files = sorted(source.glob('measurements_*.parquet'))
    frames = [pd.read_parquet(path) for path in files]
    combined = pd.concat(frames,ignore_index=True)
    if combined.duplicated(['TradingDay','SecuCode','minute']).any():
        raise ValueError('duplicate measured security/day/minute')
    recomputed = summarize(combined)
    if json.dumps(recomputed,sort_keys=True)!=json.dumps(summary['pooled'],sort_keys=True):
        raise ValueError('saved pooled metrics do not reproduce')
    for day, rows in combined.groupby('TradingDay'):
        if json.dumps(summarize(rows),sort_keys=True)!=json.dumps(summary['by_day'][str(day)],sort_keys=True):
            raise ValueError('saved daily metrics do not reproduce')
    for side in ('buy','sell'):
        for size in SIZES:
            coverage = combined[f'{side}_{size}_coverage']
            cost = combined[f'{side}_{size}_cost_bp']
            if not coverage.between(0,1).all() or not np.array_equal(cost.notna(),coverage.ge(1-1e-10)):
                raise ValueError('cost and coverage masks disagree')
    day_a,day_b = summary['comparison']['days']
    pair_frames = [combined.loc[combined.TradingDay.eq(day)] for day in (day_a,day_b)]
    paired = pair_frames[0][['SecuCode','minute']].merge(pair_frames[1][['SecuCode','minute']],
        on=['SecuCode','minute'],validate='one_to_one')
    if len(paired)!=summary['comparison']['paired_valid_security_minutes']:
        raise ValueError('paired valid-minute count does not reproduce')
    saved_events = {}
    event_files = []
    for day in summary['event_audit']:
        paths = {kind:source/f'{kind}_{day}_common.parquet' for kind in ('orders','trades')}
        orders,trades = [pd.read_parquet(paths[kind]) for kind in ('orders','trades')]
        preopen_path = source/f'preopening_orders_{day}_common.parquet'
        preopen = pd.read_parquet(preopen_path) if preopen_path.exists() else None
        if preopen is not None:
            event_files.append(preopen_path)
        event_files.extend(paths.values())
        result = event_diagnostics(orders,trades,preopen)
        result['by_market'] = {}
        for market, shanghai in [('shanghai',True),('shenzhen',False)]:
            order_slice = orders.loc[orders.SecuCode.ge(600000).eq(shanghai)]
            trade_slice = trades.loc[trades.SecuCode.ge(600000).eq(shanghai)]
            pre_slice = preopen.loc[preopen.SecuCode.ge(600000).eq(shanghai)] if preopen is not None else None
            result['by_market'][market] = event_diagnostics(order_slice,trade_slice,pre_slice)
        saved_events[day] = result
    summary['event_audit'] = saved_events
    input_files = [*files,*event_files]
    summary['review'] = {'source_summary_sha256':hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        'review_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'measurement_source_root':str(source.resolve()),
        'saved_file_sha256':{path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in input_files},
        'checks':['unique_declared_days','unique_security_day_minute','unchanged_source_stats',
                  'pooled_and_daily_quantiles','full_cost_coverage_masks','paired_valid_minutes',
                  'positive_sequence_diagnostics','exchange_segmented_reference_diagnostics']}
    (output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print('Reviewed saved measurements and segmented events; no raw sources rescanned.',flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path,required=True)
    parser.add_argument('--output-root',type=Path,required=True)
    args = parser.parse_args()
    review_saved_run(args.source_root,args.output_root)


if __name__ == '__main__':
    main()
