"""Auditable static-book measurements for a bounded, descriptive L2 pilot.

Vendor projection remains with quant-market-data-platform. Inputs must explicitly
use integer cents, share quantities, and HHMMSSmmm clocks. No event replay,
queue model, fee engine or causal impact model is implemented here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from market_research.output_paths import resolve_output_root

LEVELS = range(1, 11)
SIZES = (10000, 100000, 1000000, 10000000)
BOOK_COLUMNS = [f'{side}{field}{i}' for side in ('Bid', 'Ask')
                for field in ('Price', 'Volume') for i in LEVELS]
COLUMNS = ['SecuCode', 'TradingDay', 'TickTime', 'Price', 'TotalTurnover',
           'TotalVolume', *BOOK_COLUMNS]


def clock_minutes(clock: np.ndarray) -> np.ndarray:
    """Minutes since midnight for continuous trading, else -1.

    Exclude auctions, the lunch break, 11:30 and the 14:57 closing auction.
    Never infer clock encoding from a renamed `time_ms` column.
    """
    h = clock // 10000000
    m = (clock // 100000) % 100
    s = (clock // 1000) % 100
    minute = h * 60 + m
    valid = (clock >= 0) & (h < 24) & (m < 60) & (s < 60)
    valid &= ((minute >= 570) & (minute < 690)) | ((minute >= 780) & (minute < 897))
    return np.where(valid, minute, -1)


def earliest_per_minute(frame: pd.DataFrame) -> pd.DataFrame:
    return (frame.sort_values(['TickTime', 'source_row'], kind='stable')
            .drop_duplicates(['TradingDay', 'SecuCode', 'minute'], keep='first'))


def book_metrics(bid, ask, bq, aq) -> dict[str, np.ndarray]:
    bid, ask, bq, aq = [np.asarray(x, dtype=float) for x in (bid, ask, bq, aq)]
    if not (bid.shape == ask.shape == bq.shape == aq.shape) or bid.ndim != 2:
        raise ValueError('books must have matching two-dimensional arrays')
    finite = np.isfinite(np.concatenate([bid, ask, bq, aq], axis=1)).all(axis=1)
    nonnegative = (np.concatenate([bid, ask, bq, aq], axis=1) >= 0).all(axis=1)
    present_bid, present_ask = (bid > 0) & (bq > 0), (ask > 0) & (aq > 0)
    # Empty levels must be trailing zero/zero pairs, never a gap or mixed sentinel.
    paired = (((bid == 0) == (bq == 0)).all(axis=1)
              & ((ask == 0) == (aq == 0)).all(axis=1))
    trailing = ((np.diff(present_bid.astype(int), axis=1) <= 0).all(axis=1)
                & (np.diff(present_ask.astype(int), axis=1) <= 0).all(axis=1))
    sorted_bid = ((np.diff(bid, axis=1) <= 0) | ~present_bid[:, 1:]).all(axis=1)
    sorted_ask = ((np.diff(ask, axis=1) >= 0) | ~present_ask[:, 1:]).all(axis=1)
    two_sided = present_bid[:, 0] & present_ask[:, 0]
    uncrossed = ask[:, 0] > bid[:, 0]  # locked books excluded too
    valid = finite & nonnegative & paired & trailing & sorted_bid & sorted_ask
    valid &= two_sided & uncrossed
    mid = (bid[:, 0] + ask[:, 0]) / 2
    with np.errstate(divide='ignore', invalid='ignore'):
        spread = (ask[:, 0] - bid[:, 0]) / mid * 10000
    return {'valid': valid, 'mid': mid, 'spread_bp': spread,
            'one_sided': ~two_sided, 'crossed_or_locked': two_sided & ~uncrossed,
            'malformed': ~(finite & nonnegative & paired & trailing & sorted_bid & sorted_ask),
            'bid_depth_cny': (bid * bq).sum(axis=1),
            'ask_depth_cny': (ask * aq).sum(axis=1)}


def walk_notional(prices, quantities, mid, notional: float, side: str):
    """Walk shares equal to reference notional / midpoint, allowing fractions.

    This is an analytical depth curve, not a cash budget or lot-sized order.
    Full-order costs are missing when the displayed ten levels cannot cover Q.
    """
    if not np.isfinite(notional) or notional <= 0 or side not in ('buy', 'sell'):
        raise ValueError('positive finite notional and buy/sell side required')
    prices, quantities, mid = [np.asarray(x, dtype=float) for x in (prices, quantities, mid)]
    if prices.shape != quantities.shape or prices.ndim != 2 or mid.shape != prices.shape[:1]:
        raise ValueError('prices, quantities and mid must have matching shapes')
    if not np.isfinite(mid).all() or (mid <= 0).any():
        raise ValueError('positive finite mid required')
    if not np.isfinite(prices).all() or not np.isfinite(quantities).all():
        raise ValueError('finite price and quantity required')
    if (prices < 0).any() or (quantities < 0).any():
        raise ValueError('negative price or quantity')
    target = notional / mid
    before = np.cumsum(quantities, axis=1) - quantities
    taken = np.minimum(quantities, np.maximum(target[:, None] - before, 0))
    filled = taken.sum(axis=1)
    coverage = np.minimum(filled / target, 1)
    with np.errstate(divide='ignore', invalid='ignore'):
        vwap = (taken * prices).sum(axis=1) / filled
        covered = (vwap / mid - 1) * 10000 * (1 if side == 'buy' else -1)
    full = coverage >= 1 - 1e-10
    return {'coverage': coverage, 'cost_bp': np.where(full, covered, np.nan),
            'covered_cost_bp': covered}


def quantiles(values) -> dict:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    return {'count': len(values), **{k: float(np.quantile(values, q)) if len(values) else None
                                    for k, q in [('p50', .5), ('p90', .9), ('p95', .95)]}}


def sample_source(source: Path, day: int, modulus: int, batch_size: int):
    # Import only when using real sources; tests do not need the provider checkout.
    from quant_market_data_platform.l2_views import iter_l2_batches

    f = pq.ParquetFile(source)
    # Reject mere aliases: the platform projection renames without converting clocks.
    if not {'SecuCode', 'TickTime'}.issubset(f.schema_arrow.names):
        raise ValueError('explicit SecuCode/HHMMSSmmm TickTime source required; aliases need audit')
    stats = {'metadata_rows': f.metadata.num_rows, 'rows_read': 0, 'day_mismatch': 0,
             'outside_continuous_session': 0, 'invalid_clock': 0,
             'selected_event_rows': 0, 'null_clock_or_identity': 0}
    samples = []
    offset = 0
    for batch in iter_l2_batches(source, 'snapshot', columns=COLUMNS,
                                 batch_size=batch_size, include_tagged=True):
        df = batch.to_pandas()
        stats['rows_read'] += len(df)
        identifiers = df[['SecuCode', 'TickTime', 'TradingDay']].notna().all(axis=1)
        stats['null_clock_or_identity'] += int((~identifiers).sum())
        df = df.loc[identifiers].copy()
        df['source_row'] = df.index.to_numpy() + offset
        offset += batch.num_rows
        code = pd.to_numeric(df['SecuCode'], errors='raise').to_numpy(dtype=np.int64)
        t = df['TickTime'].to_numpy(dtype=np.int64)
        # Raw encoding validity is separate from the continuous-session filter.
        invalid = (t < 0) | (t // 10000000 > 23) | ((t // 100000) % 100 > 59)
        invalid |= ((t // 1000) % 100 > 59)
        stats['invalid_clock'] += int(invalid.sum())
        minute = clock_minutes(t)
        stats['outside_continuous_session'] += int((minute < 0).sum())
        matching = df['TradingDay'].to_numpy() == day
        stats['day_mismatch'] += int((~matching).sum())
        # Shanghai/Shenzhen A-share prefixes only; no Beijing/funds/bonds.
        prefixes = code // 1000
        stocks = np.isin(prefixes, [0,1,2,3,300,301,600,601,603,605,688,689])
        keep = matching & (minute >= 0) & stocks & (code % modulus == 0)
        selected = df.loc[keep].copy()
        selected['minute'] = minute[keep]
        stats['selected_event_rows'] += len(selected)
        if len(selected):
            samples.append(earliest_per_minute(selected))
    if not samples:
        raise ValueError('no selected continuous-session A-share snapshots')
    selected = pd.concat(samples, ignore_index=True)
    sampled = earliest_per_minute(selected).reset_index(drop=True)
    stats.update({'sampled_snapshots': len(sampled),
                  'sampled_securities': int(sampled['SecuCode'].nunique()),
                  'selected_duplicate_timestamps': int(selected.duplicated(
                      ['SecuCode', 'TickTime'], keep=False).sum())})
    return sampled, stats


def measure(frame: pd.DataFrame):
    bid = frame[[f'BidPrice{i}' for i in LEVELS]].to_numpy(dtype=float) / 100
    ask = frame[[f'AskPrice{i}' for i in LEVELS]].to_numpy(dtype=float) / 100
    bq = frame[[f'BidVolume{i}' for i in LEVELS]].to_numpy(dtype=float)
    aq = frame[[f'AskVolume{i}' for i in LEVELS]].to_numpy(dtype=float)
    metrics = book_metrics(bid, ask, bq, aq)
    valid = metrics['valid']
    out = frame[['SecuCode','TradingDay','TickTime','minute','source_row']].loc[valid].copy()
    for key in ['spread_bp','mid','bid_depth_cny','ask_depth_cny']:
        out[key] = metrics[key][valid]
    for side, prices, qty in [('buy',ask,aq),('sell',bid,bq)]:
        for size in SIZES:
            walked = walk_notional(prices[valid],qty[valid],metrics['mid'][valid],size,side)
            for key in ['cost_bp','coverage']:
                out[f'{side}_{size}_{key}'] = walked[key]
    unit = frame.loc[(frame['Price'] > 0) & (frame['TotalVolume'] > 0)]
    ratio = unit['TotalTurnover'] / (unit['TotalVolume'] * unit['Price'] / 100)
    diagnostics = {'valid_books': int(valid.sum()), 'excluded_books': int((~valid).sum()),
                   'one_sided': int(metrics['one_sided'].sum()),
                   'crossed_or_locked': int(metrics['crossed_or_locked'].sum()),
                   'malformed': int(metrics['malformed'].sum()),
                   'price_volume_consistency_ratio': quantiles(ratio),
                   'ratio_between_0_8_and_1_2': float(ratio.between(.8,1.2).mean()) if len(ratio) else None}
    # Reasons can overlap; excluded_books is the union, not the sum of reasons.
    return out, diagnostics


def summarize(frame: pd.DataFrame, *, include_common: bool = True) -> dict:
    rows = []
    for side in ('buy','sell'):
        for size in SIZES:
            cost = frame[f'{side}_{size}_cost_bp']
            coverage = frame[f'{side}_{size}_coverage']
            rows.append({'side':side,'reference_notional_cny':size,
                         'full_coverage_rate':float(cost.notna().mean()) if len(cost) else None,
                         'coverage_fraction':quantiles(coverage),
                         'full_order_cost_bp':quantiles(cost)})
    result = {'snapshots':len(frame), 'security_days':int(frame.groupby(
        ['TradingDay','SecuCode']).ngroups), 'spread_bp':quantiles(frame['spread_bp']),
        'bid_depth_cny':quantiles(frame['bid_depth_cny']),
        'ask_depth_cny':quantiles(frame['ask_depth_cny']), 'cost_surface':rows}
    if include_common:
        cost_columns = [f'{side}_{size}_cost_bp' for side in ('buy','sell') for size in SIZES]
        matched = frame.loc[frame[cost_columns].notna().all(axis=1)]
        result['common_full_subset'] = summarize(matched, include_common=False)
    return result


def run(spec_path: Path, output_root: Path):
    spec = json.loads(spec_path.read_text())
    if spec.get('price_unit') != 'integer_cent' or spec.get('quantity_unit') != 'share':
        raise ValueError('explicit integer_cent/share unit contract required')
    if spec.get('clock_encoding') != 'HHMMSSmmm':
        raise ValueError('explicit HHMMSSmmm clock contract required')
    modulus = int(spec.get('security_modulus',37))
    if modulus <= 0:
        raise ValueError('security_modulus must be positive')
    output = resolve_output_root({'output_root':str(output_root)})
    output.mkdir(parents=True,exist_ok=False)
    all_frames, audit, inputs = [], [], []
    seen_days = set()
    for entry in spec['inputs']:
        day = int(entry['day'])
        if day in seen_days:
            raise ValueError('duplicate input day would double-weight the sample')
        seen_days.add(day)
        path = Path(entry['path']).resolve(strict=True)
        if not path.is_file():
            raise ValueError('input must be a file')
        print(f'Auditing {day}',flush=True)
        before = path.stat()
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(8*1024*1024),b''):
                digest.update(block)
        frame, profile = sample_source(path,day,modulus,int(spec.get('batch_size',65536)))
        measured, diagnostic = measure(frame)
        after = path.stat()
        if (before.st_size,before.st_mtime_ns) != (after.st_size,after.st_mtime_ns):
            raise ValueError('source changed during the audit')
        profile.update(diagnostic)
        if profile['rows_read'] != profile['metadata_rows'] or profile['day_mismatch']:
            raise ValueError('source row count or trading-day gate failed')
        audit.append({'day':day,**profile})
        inputs.append({'day':day,'path':str(path),'sha256':digest.hexdigest(),
                       'bytes':before.st_size,'schema':str(pq.ParquetFile(path).schema_arrow)})
        measured.to_parquet(output/f'sampled_measurements_{day}.parquet',index=False)
        all_frames.append(measured)
        print(f'{day}: {profile["rows_read"]} scanned, {len(measured)} valid sampled books',flush=True)
    combined = pd.concat(all_frames,ignore_index=True)
    summary = {'study_id':'ashare_execution_costs','evidence':'descriptive_static_book_pilot',
               'measurement_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'spec':spec,'inputs':inputs,'audit':audit,'pooled':summarize(combined),
               'by_day':{str(day):summarize(df) for day,df in combined.groupby('TradingDay')},
               'uncertainty':'quantiles describe the sample; no population confidence interval',
               'publication_status':'local_only_pending_vendor_derivative_permission'}
    # Daily depth groups describe these days, not PIT market-cap groups or trading signals.
    median = combined.groupby(['TradingDay','SecuCode'])[
        ['bid_depth_cny','ask_depth_cny']].median().mean(axis=1)
    groups = median.groupby(level=0).transform(lambda x: pd.qcut(
        x.rank(method='first'),3,labels=['shallow','middle','deep']))
    combined['depth_group'] = [groups.loc[(d,c)] for d,c in zip(
        combined['TradingDay'],combined['SecuCode'],strict=True)]
    summary['by_depth_group'] = {str(g):summarize(df) for g,df in combined.groupby('depth_group')}
    (output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(f'Local summary: {output / "summary.json"}',flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,required=True)
    parser.add_argument('--output-root',type=Path,required=True)
    args = parser.parse_args()
    run(args.spec,args.output_root)


if __name__ == '__main__':
    main()
