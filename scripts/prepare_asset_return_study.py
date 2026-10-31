"""Prepare this study from frozen owner responses; no live API or alias writes.

Consumes receipt.json in raw/, retry-01/ and bond-probes/ below --owner-task.
This recipe is specific to the 20261031 acquisition. Request credentials and
private connection configuration are never read by this program.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from market_research.studies.asset_returns.analysis import chain_cpi
from market_research.studies.asset_returns.inputs import month_end_levels, read_frozen_response


def prepare(owner_task: Path, output: Path, source_revision: str) -> dict:
    if output.exists():
        raise FileExistsError('select a new output directory')
    # The study runner enforces the same source-output boundary.
    if any((p / '.git').exists() for p in [output.resolve(), *output.resolve().parents]
           if p not in {Path('/tmp'), Path.home()}):
        raise ValueError('prepared inputs must remain outside source repositories')
    frames: dict[str, list[pd.DataFrame]] = {}
    receipts = []
    for folder in ['raw', 'retry-01']:
        receipt_path = owner_task / folder / 'receipt.json'
        rows = json.loads(receipt_path.read_text())
        for row in rows:
            if row.get('code') != 0 or not row.get('rows'):
                continue
            path = receipt_path.parent / (row['id'] + '.json')
            frame = read_frozen_response(path, row['sha256'])
            # A full catalog is unnecessary; its 8000-row cap is not full coverage.
            if row['api'] == 'index_basic':
                continue
            key = row['params'].get('ts_code', row['id'])
            frames.setdefault(key, []).append(frame)
            receipts.append({'id': row['id'], 'sha256': row['sha256'], 'api': row['api']})
    calendar = pd.DatetimeIndex(pd.to_datetime(pd.concat(frames['calendar']).cal_date))
    calendar = calendar[(calendar >= '2004-12-31') & (calendar <= '2025-12-31')]
    monthly = {}
    codes = ['000985.CSI', 'H00985.CSI', '000300.SH', 'H00300.CSI',
             '000852.SH', 'H00852.CSI', 'Au99.99']
    for code in codes:
        data = pd.concat(frames[code], ignore_index=True)
        data['date'] = pd.to_datetime(data.trade_date)
        monthly[code] = month_end_levels(data, calendar).set_index('date').close
    cpi = pd.concat(frames['cpi_history']).sort_values('month')
    cpi['date'] = pd.to_datetime(cpi.month + '01') + pd.offsets.MonthEnd(0)
    cpi['mom_pct'] = cpi.nt_mom
    cpi_levels = chain_cpi(cpi)
    monthly['cpi'] = pd.Series(cpi_levels.to_numpy(), index=cpi.date)
    prepared = {}
    for name, price, total in [('all_share', '000985.CSI', 'H00985.CSI'),
                                ('large_cap', '000300.SH', 'H00300.CSI'),
                                ('small_cap', '000852.SH', 'H00852.CSI')]:
        frame = pd.DataFrame({'price': monthly[price], 'total': monthly[total],
                              'cpi': monthly['cpi'], 'gold': monthly['Au99.99'],
                              'benchmark': monthly['H00300.CSI']})
        prepared[name] = (frame, {'price': price, 'total': total, 'cpi': 'cn_cpi.nt_mom',
                                 'gold': 'Au99.99', 'benchmark': 'H00300.CSI'})
    bond_receipt_path = owner_task / 'bond-probes/receipt.json'
    bond_receipts = json.loads(bond_receipt_path.read_text())
    bond_row = next(r for r in bond_receipts if r['id'] == 'treasury_7_10_wealth')
    bond_raw = (bond_receipt_path.parent / 'treasury_7_10_wealth.json').read_bytes()
    if hashlib.sha256(bond_raw).hexdigest() != bond_row['sha256']:
        raise ValueError('bond frozen hash mismatch')
    bond = pd.Series(json.loads(bond_raw)['CFZS_00'], dtype=float)
    bond.index = pd.to_datetime(bond.index.astype('int64'), unit='ms', utc=True).tz_convert('Asia/Shanghai').tz_localize(None).normalize()
    bond_calendar = calendar[calendar >= '2007-01-01']
    bond_monthly = month_end_levels(pd.DataFrame({'date': bond.index, 'close': bond.values}), bond_calendar).set_index('date').close
    common = prepared['all_share'][0].loc[bond_monthly.index].copy()
    common['bond'] = bond_monthly
    prepared['multi_asset'] = (common, {**prepared['all_share'][1], 'bond': 'ChinaBond.7-10Y.treasury.CFZS'})
    all_hashes = receipts + [{'id': bond_row['id'], 'sha256': bond_row['sha256'], 'api': 'ChinaBond.public_index'}]
    payloads = {}
    for name, (frame, sources) in prepared.items():
        metadata = {'schema_version': 1, 'source_revision': source_revision,
                    'input_receipts': all_hashes,
                    'endpoint_validation': 'exact final SSE session each month; not daily completeness',
                    'cpi_method': 'chain rounded national month-on-month rates; approximate purchasing power',
                    'historical_vintage': 'retrieved 2026-10-31; backfills and revisions possible',
                    'series': {col: {'currency': 'dimensionless' if col == 'cpi' else 'CNY',
                        'return_basis': ('price' if col in ['price', 'gold'] else 'cpi_level' if col == 'cpi' else 'total_return'),
                        'source_id': src, 'coverage_verified': True} for col, src in sources.items()}}
        payloads[name] = (frame.rename_axis('date').reset_index(), metadata)
    output.mkdir(parents=True, exist_ok=False)
    for name, (frame, metadata) in payloads.items():
        frame.to_csv(output / (name + '.csv'), index=False)
        (output / (name + '.metadata.json')).write_text(json.dumps(metadata, indent=2) + '\n')
    return {name: {'observations': len(frame), 'start': str(frame.date.iloc[0].date()),
                    'end': str(frame.date.iloc[-1].date())} for name, (frame, _) in payloads.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner-task', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-revision', required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.owner_task, args.output, args.source_revision), indent=2))
