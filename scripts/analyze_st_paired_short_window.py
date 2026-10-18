#!/usr/bin/env python3
"""Audit historical support and measure matched descriptive monthly ST baskets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd
import yaml

from market_research.st_paired import classify_status, pair_period


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--start', default='20221201')
    p.add_argument('--frequency', choices=('monthly', 'daily'), default='monthly')
    p.add_argument('--execution-year', help='optional calendar year of the entry close')
    p.add_argument('--end', default='20260105')
    args = p.parse_args()
    a = args.data_root / 'assets/tushare/a_share'
    pointer = a / 'daily/a_share_all_daily_clean_latest/manifest.yml'
    manifest = yaml.safe_load(pointer.read_text())
    asset = Path(manifest['output_dir'])
    if manifest['schema_version'] != 'tushare.a_share.daily_clean.v2':
        raise ValueError('versioned ST availability contract required')
    if manifest.get('contracts', {}).get('st_availability') != 'daily_clean.st_available_from.v1':
        raise ValueError('missing ST availability contract')
    st_reference = Path(manifest['inputs']['st_history_file']).with_suffix('.receipt.json')
    st_receipt = json.loads(st_reference.read_text())
    if st_receipt.get('quality_status') != 'complete' or st_receipt.get('source_receipt_schema_version') != 'market-data-platform.reconstructed-st-history.v2':
        raise ValueError('complete v2 reconstructed ST source required')
    instruments = a / 'instruments/a_share_all_instruments_20260928.parquet'
    name_path = a / 'namechange/a_share_all_namechange_20260928.parquet'
    truth_manifest = args.data_root / 'assets/derived/a_share/st_truth_2015_2025_observed_20261002_v1/manifest.json'
    truth_meta = json.loads(truth_manifest.read_text())
    truth_path = truth_manifest.parent / truth_meta['path']
    if digest(truth_path) != truth_meta['sha256']:
        raise ValueError('positive state source hash mismatch')
    c = duckdb.connect()
    c.execute('set threads=4')
    files = str(asset / 'data/*.parquet')
    dates = c.execute('select distinct trade_date from read_parquet(?) where trade_date between ? and ? order by trade_date', [files, args.start, args.end]).fetchdf().trade_date.tolist()
    calendar_path = a / 'trade_cal/a_share_trade_cal_latest.parquet'
    calendar = pd.read_parquet(calendar_path)
    expected = calendar.loc[calendar.exchange.eq('SSE') & calendar.is_open.eq(1)
                            & calendar.cal_date.between(args.start, args.end), 'cal_date']
    if set(expected) != set(dates):
        raise ValueError('clean observed dates differ from SSE open calendar')
    schedule = pd.DataFrame({'date': dates})
    schedule['month'] = schedule.date.str[:6]
    ends = schedule.groupby('month').date.last().tolist()
    # A month is admitted only if its next month's execution close is in inventory.
    windows = [(day, dates[dates.index(day)+1], dates[dates.index(nxt)+1])
               for day, nxt in zip(ends, ends[1:]) if dates.index(nxt)+1 < len(dates)]
    if args.frequency == 'daily':
        windows = list(zip(dates[:-2], dates[1:-1], dates[2:]))
    if args.execution_year:
        windows = [w for w in windows if w[1].startswith(args.execution_year)]
    if not windows:
        raise ValueError('no complete measurement windows')
    if any(not truth_meta['coverage_start'] <= w[0] <= truth_meta['coverage_end'] for w in windows):
        raise ValueError('formation outside verified positive-state cross-check dates')
    needed = sorted({d for row in windows for d in row})
    c.register('needed', pd.DataFrame({'trade_date': needed}))
    panel = c.execute('select ts_code, trade_date, total_mv, amount, adj_close, is_suspended, is_st, st_available_from from read_parquet(?) join needed using(trade_date)', [files]).fetchdf()
    if panel.duplicated(['ts_code', 'trade_date']).any():
        raise ValueError('duplicate security/date prices')
    basic = pd.read_parquet(instruments)[['ts_code', 'list_date', 'delist_date']]
    if basic.ts_code.duplicated().any():
        raise ValueError('duplicate instrument identity')
    basic = basic.replace({'None': None, '': None})
    names = pd.read_parquet(name_path)
    formation = panel.loc[panel.trade_date.isin([r[0] for r in windows])].merge(basic, on='ts_code', how='left', validate='many_to_one')
    classified = classify_status(formation, names)
    truth = pd.read_parquet(truth_path)[['ts_code', 'trade_date']].drop_duplicates()
    truth['positive_crosscheck'] = True
    classified = classified.merge(truth, on=['ts_code', 'trade_date'], how='left', validate='many_to_one')
    classified['positive_crosscheck'] = classified.positive_crosscheck.fillna(False).astype(bool)
    classified['positive_disagreement'] = classified.positive_crosscheck.ne(classified.is_st)
    # Cross-check disagreement remains unknown; absence alone never establishes non-ST.
    classified.loc[classified.positive_disagreement, 'status'] = 'unknown'
    coverage = []
    records, selections = [], []
    price_days = dict(tuple(panel.groupby('trade_date', sort=False)))
    for day, execution, endpoint in windows:
        period_prices = pd.concat([price_days[execution], price_days[endpoint]], ignore_index=True)
        block = classified.loc[classified.trade_date.eq(day)]
        alive = basic.loc[basic.list_date.notna() & basic.list_date.le(day)
                          & (basic.delist_date.isna() | basic.delist_date.gt(day))]
        coverage.append({'formation': day, 'master_alive': len(alive),
                         'daily_rows': len(block),
                         'master_alive_missing_daily': len(set(alive.ts_code)-set(block.ts_code)),
                         'daily_missing_master': int((~block.ts_code.isin(basic.ts_code)).sum()),
                         'name_known': int(block.name_known.sum()),
                         'status_unknown': int(block.status.eq('unknown').sum()),
                         'status_st': int(block.status.eq('st').sum()),
                         'status_non_st': int(block.status.eq('non_st').sum()),
                         'positive_disagreement': int(block.positive_disagreement.sum()),
                         'positive_not_available': int(block.positive_not_available.sum())})
        for n in (50, 100, 200):
            record, selected = pair_period(block, period_prices, n=n, execution=execution, endpoint=endpoint)
            records.append(record)
            selections.append(selected)
    periods = pd.DataFrame(records)
    periods['year'] = periods.execution.str[:4]
    summary = []
    for n, group in periods.groupby('n'):
        for year in ['all', *sorted(group.year.unique())]:
            g = group if year == 'all' else group.loc[group.year.eq(year)]
            valid = g.loc[g.complete_pair]
            summary.append({'n': int(n), 'year': year, 'attempted_pairs': len(g),
                            'complete_pairs': len(valid), 'incomplete_pairs': len(g)-len(valid),
                            'mean_include_st_count': float(g.include_st_count.mean()),
                            'mean_common_weight': float(g.common_weight.mean()),
                            'mean_difference_pp': float(100*valid.difference.mean()) if len(valid) else None,
                            'mean_include_return_pct': float(100*valid.include_st_return.mean()) if len(valid) else None,
                            'mean_exclude_return_pct': float(100*valid.exclude_st_return.mean()) if len(valid) else None,
                            'positive_difference_pairs': int(valid.difference.gt(0).sum()),
                            'unresolved_selected_rows': int(g.unresolved_selected_rows.sum()),
                            'terminal_selected_rows': int(g.terminal_selected_rows.sum())})
    args.output.mkdir(parents=True, exist_ok=False)
    periods.to_csv(args.output / 'periods.csv', index=False)
    pd.DataFrame(coverage).to_csv(args.output / 'coverage.csv', index=False)
    pd.DataFrame(summary).to_csv(args.output / 'summary.csv', index=False)
    pd.concat(selections, ignore_index=True).to_parquet(args.output / 'selection_audit.parquet', index=False)
    provenance = {'schema_version': 'market-research.st-paired-descriptive.v1',
                  'revision_safe': False, 'historical_pit_certified': False,
                  'frequency': args.frequency, 'start': args.start, 'end': args.end,
                  'execution_year': args.execution_year,
                  'calendar_sha256': digest(calendar_path),
                  'missing_market_sessions': 0,
                  'script_sha256': digest(Path(__file__)),
                  'module_sha256': digest(Path(__file__).parents[1]/'src/market_research/st_paired.py'),
                  'clean_asset': str(asset), 'clean_manifest_sha256': digest(asset/'manifest.yml'),
                  'st_reference_receipt': str(st_reference), 'st_receipt_sha256': digest(st_reference),
                  'st_version_path': st_receipt['version_path'], 'st_version_sha256': st_receipt['sha256'],
                  'instruments': str(instruments), 'instruments_sha256': digest(instruments),
                  'namechange': str(name_path), 'namechange_sha256': digest(name_path),
                  'positive_source_manifest_sha256': digest(truth_manifest),
                  'positive_source_sha256': truth_meta['sha256'],
                  'positive_source_historical_pit_eligible': truth_meta['historical_pit_eligible'],
                  'window_selection': '2023-2025 recent retrospective cross-check coverage; no performance-based selection',
                  'formation': f'{args.frequency}; monthly last observed market session or every session; rank ascending total_mv then ts_code; N=50/100/200',
                  'measurement': 'next market session adjusted close to session after next formation; fixed equal initial weights; zero assumed cost; no fills or ledger',
                  'status': 'known active name announced strictly before formation; daily reconstructed state agrees; positive available_from <= formation; same-provider positive state cross-check agrees; unknown excluded identically',
                  'missing_marks': 'require positive price and amount and non-suspended at both endpoints; invalidate entire paired period without renormalization; no terminal settlement assumption',
                  'limitations': 'retrospective master and name history; revision_safe=false; same-provider cross-check is not independent truth; complete-pair conditional selection; adjusted closes are price proxies, not total shareholder return or cash settlement',
                  'outputs': {p.name: digest(p) for p in args.output.iterdir()}}
    (args.output / 'receipt.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(pd.DataFrame(summary).to_string(index=False))
    print(pd.DataFrame(coverage).sum(numeric_only=True).to_string())


if __name__ == '__main__':
    main()
