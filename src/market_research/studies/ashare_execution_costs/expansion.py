"""Bounded historical L2 audit and descriptive static-cost expansion.

Explicit source bindings and clock profiles are research input gates. Canonical
projection and static cost mathematics remain with the existing provider/pilot.
No queue, cancellation, causal impact or generic execution engine is added.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from market_research.output_paths import resolve_output_root
from market_research.studies.ashare_execution_costs.pilot import COLUMNS, measure, summarize

OPEN_MS = 34_200_000
PREFIXES = (0, 1, 2, 3, 300, 301, 600, 601, 603, 605, 688, 689)
PROFILES = ('native_hhmmssmmm', 'relative_0930_ms')


def validate_spec(spec: dict):
    days = [int(day) for source in spec['snapshot_sources'] for day in source['days']]
    if len(days) != len(set(days)):
        raise ValueError('duplicate declared snapshot day would double-weight evidence')
    for day in days:
        datetime.strptime(str(day),'%Y%m%d')
    comparison = list(map(int,spec['comparison_days']))
    if len(comparison)!=2 or len(set(comparison))!=2 or not set(comparison).issubset(days):
        raise ValueError('comparison requires two unique declared snapshot days')
    events = [int(row['day']) for row in spec.get('event_sources',[])]
    if len(events)!=len(set(events)) or not set(events).issubset(days):
        raise ValueError('event days must be unique declared snapshot days')
    for row in spec.get('event_sources',[]):
        for kind in ('order','deal','preopen_order'):
            if kind in row and int(row[kind]['day'])!=int(row['day']):
                raise ValueError('event binding day mismatch')


def clock_ms(values, profile: str) -> np.ndarray:
    """Convert an explicit clock to wall-clock milliseconds, retaining lunch."""
    value = np.asarray(values, dtype=float)
    valid = np.isfinite(value) & (value == np.trunc(value))
    if profile == 'relative_0930_ms':
        absolute = value + OPEN_MS
    elif profile == 'native_hhmmssmmm':
        h, m, s = np.floor(value / 10_000_000), np.floor(value / 100_000) % 100, np.floor(value / 1000) % 100
        valid &= (value >= 0) & (h < 24) & (m < 60) & (s < 60)
        absolute = h * 3_600_000 + m * 60_000 + s * 1000 + value % 1000
    else:
        raise ValueError('explicit supported clock profile required')
    valid &= (absolute >= 0) & (absolute < 86_400_000)
    return np.where(valid, absolute, np.nan)


def minute_coverage(frame: pd.DataFrame, securities) -> dict:
    codes = set(int(code) for code in securities)
    unique = frame.loc[frame.SecuCode.isin(codes)].drop_duplicates(['SecuCode', 'minute'])
    expected = len(codes) * 237
    observed = len(unique)
    if observed > expected:
        raise ValueError('observed bins exceed continuous-session denominator')
    return {'securities': len(codes), 'expected_security_minutes': expected,
            'observed_security_minutes': observed, 'missing_security_minutes': expected - observed,
            'observed_fraction': observed / expected if expected else None}


def stream_audit(frame: pd.DataFrame, kind: str) -> dict:
    groups = ['SecuCode'] + (['Channel'] if 'Channel' in frame else [])
    event_id = 'OrderID' if kind == 'order' else 'DealID'
    identity = [*groups, event_id, 'time_ms_absolute', 'Price', 'Volume']
    for extra in ('OrderType', 'BuyID', 'SellID', 'Side', 'BizIndex'):
        if extra in frame:
            identity.append(extra)
    delta = frame.groupby(groups, dropna=False, sort=False).time_ms_absolute.diff()
    result = {'rows': len(frame), 'nonpositive_price_rows': int(frame.Price.le(0).sum()),
              'nonpositive_volume_rows': int(frame.Volume.le(0).sum()),
              'null_clock_rows': int(frame.time_ms_absolute.isna().sum()),
              'duplicate_event_rows': int(frame.duplicated(identity, keep=False).sum()),
              'timestamp_regressions': int(delta.lt(0).sum()),
              'sequence_available': 'BizIndex' in frame, 'channel_available': 'Channel' in frame}
    if 'BizIndex' in frame:
        sequence = frame.groupby(groups, dropna=False, sort=False).BizIndex.diff()
        result['sequence_regressions'] = int(sequence.lt(0).sum())
        result['duplicate_sequence_rows'] = int(frame.duplicated([*groups, 'BizIndex'], keep=False).sum())
        positive = frame.loc[frame.BizIndex.notna() & frame.BizIndex.gt(0)]
        result['nonpositive_sequence_rows'] = int(frame.BizIndex.le(0).sum())
        result['null_sequence_rows'] = int(frame.BizIndex.isna().sum())
        result['positive_sequence_regressions'] = int(positive.groupby(groups,dropna=False,sort=False).BizIndex.diff().lt(0).sum())
        result['duplicate_positive_sequence_rows'] = int(positive.duplicated([*groups,'BizIndex'],keep=False).sum())
    for category in ('OrderType', 'Side'):
        if category in frame:
            result[category + '_counts'] = {str(key): int(count) for key, count in frame[category].value_counts(dropna=False).items()}
    return result


def reference_audit(orders: pd.DataFrame, trades: pd.DataFrame, candidate: str) -> dict:
    """Report key presence/ambiguity, never interpret a match as queue replay."""
    scoped = 'Channel' in orders and 'Channel' in trades
    keys = ['SecuCode'] + (['Channel'] if scoped else [])
    order_keys = orders.loc[orders[candidate].notna() & orders[candidate].gt(0), [*keys, candidate]]
    counts = order_keys.groupby([*keys, candidate], dropna=False).size().rename('order_rows').reset_index()
    eligible = trades.loc[trades.Price.gt(0) & trades.Volume.gt(0)]
    result = {'candidate': candidate, 'eligible_positive_trade_rows': len(eligible),
              'identity_scope': 'security_channel' if scoped else 'security_only_channel_unavailable'}
    for side, column in [('buy', 'BuyID'), ('sell', 'SellID')]:
        joined = eligible[[*keys, column]].merge(counts.rename(columns={candidate: column}),
                                                on=[*keys, column], how='left', validate='many_to_one')
        match = joined.order_rows.notna()
        result[side] = {'references': len(joined), 'matched': int(match.sum()),
                        'unique': int(joined.order_rows.eq(1).sum()),
                        'ambiguous': int(joined.order_rows.gt(1).sum()),
                        'missing': int((~match).sum()),
                        'nonpositive_or_null_reference_rows':int((eligible[column].isna()|eligible[column].le(0)).sum()),
                        'match_rate': float(match.mean()) if len(joined) else None}
    return result


def lagged_features(daily: pd.DataFrame, basic: pd.DataFrame, day: str) -> pd.DataFrame:
    for label, frame in [('daily', daily), ('basic', basic)]:
        if frame.duplicated(['SecuCode', 'trade_date']).any():
            raise ValueError(f'{label} has duplicate security/date keys')
    prior = daily.loc[daily.trade_date.astype(str).lt(str(day))].copy()
    calendar = sorted(prior.trade_date.astype(str).unique())[-20:]
    prior = prior.loc[prior.trade_date.astype(str).isin(calendar)]
    prior['notional_cny'] = pd.to_numeric(prior.amount) * 1000
    with np.errstate(divide='ignore', invalid='ignore'):
        prior['return'] = np.log(prior.close / prior.pre_close)
    prior.loc[~np.isfinite(prior['return']), 'return'] = np.nan
    prior.loc[~np.isfinite(prior.notional_cny) | prior.notional_cny.lt(0), 'notional_cny'] = np.nan
    grouped = prior.groupby('SecuCode').agg(history_sessions=('trade_date', 'nunique'),
        adv20_cny=('notional_cny', 'mean'), liquidity_observations=('notional_cny', 'count'),
        volatility20=('return', 'std'), return_observations=('return', 'count'))
    grouped.loc[grouped.liquidity_observations.lt(20), 'adv20_cny'] = np.nan
    grouped.loc[grouped.return_observations.lt(20), 'volatility20'] = np.nan
    previous = basic.loc[basic.trade_date.astype(str).eq(calendar[-1])] if calendar else basic.iloc[:0]
    caps = previous.set_index('SecuCode').circ_mv * 10000
    grouped['market_cap_cny'] = caps
    grouped.loc[grouped.market_cap_cny.le(0), 'market_cap_cny'] = np.nan
    return grouped.reset_index()


def _fingerprint(path: Path) -> dict:
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return {'path': str(path.resolve()), 'bytes': before.st_size, 'mtime_ns': before.st_mtime_ns,
            'sha256': digest.hexdigest(), 'metadata_rows': pq.ParquetFile(path).metadata.num_rows}


def _source_unchanged(receipt: dict):
    stat = Path(receipt['path']).stat()
    if (stat.st_size, stat.st_mtime_ns) != (receipt['bytes'], receipt['mtime_ns']):
        raise ValueError('source changed during the study')


def _binding(profile: str, kind: str):
    if profile not in PROFILES:
        raise ValueError('explicit supported clock profile required')
    if profile == 'relative_0930_ms':
        return 'ticker', 'time_ms'
    return 'SecuCode', {'snapshot': 'TickTime', 'order': 'OrderTime', 'deal': 'DealTime'}[kind]


def _clock_sql(column: str, profile: str) -> str:
    value = f'TRY_CAST("{column}" AS BIGINT)'
    raw = f'TRY_CAST("{column}" AS DOUBLE)'
    integral = f'{raw}=trunc({raw})'
    if profile == 'relative_0930_ms':
        return f'CASE WHEN {integral} AND {value}+{OPEN_MS} BETWEEN 0 AND 86399999 THEN {value}+{OPEN_MS} END'
    return (f'CASE WHEN {integral} AND {value}>=0 AND {value}//10000000<24 AND ({value}//100000)%100<60 '
            f'AND ({value}//1000)%100<60 THEN ({value}//10000000)*3600000 '
            f'+(({value}//100000)%100)*60000+(({value}//1000)%100)*1000+{value}%1000 END')


def _connect(output: Path):
    connection = duckdb.connect()
    connection.execute("SET threads=2")
    connection.execute("SET memory_limit='3GB'")
    connection.execute("SET temp_directory=?", [str(output / 'sql_temp')])
    connection.execute("SET preserve_insertion_order=true")
    return connection


def _raw_view(con, entry: dict, kind: str):
    path = Path(entry['path']).resolve(strict=True)
    security, clock = _binding(entry['clock_profile'], kind)
    names = pq.ParquetFile(path).schema_arrow.names
    if security not in names or clock not in names or 'TradingDay' not in names:
        raise ValueError('source schema disagrees with explicit profile')
    con.from_parquet(str(path), file_row_number=True).create_view('source', replace=True)
    return path, security, clock, names


def sample_books(entry: dict, output: Path, *, modulus: int = 37):
    """Push selection into the file query, then reuse the canonical provider view."""
    from quant_market_data_platform.l2_views import iter_l2_batches

    with _connect(output) as con:
        path, security, clock, names = _raw_view(con, entry, 'snapshot')
        receipt = _fingerprint(path)
        days = ','.join(str(int(day)) for day in entry['days'])
        raw_columns = [security if name == 'SecuCode' else clock if name == 'TickTime' else name for name in COLUMNS]
        if set(raw_columns) - set(names):
            raise ValueError('snapshot measurement columns missing')
        columns = ','.join(f'"{name}"' for name in raw_columns)
        code = f'TRY_CAST("{security}" AS BIGINT)'
        milliseconds = _clock_sql(clock, entry['clock_profile'])
        prefixes = ','.join(map(str, PREFIXES))
        base = (f'SELECT file_row_number AS source_row,{columns},{code} AS code,{milliseconds} AS absolute_ms '
                f'FROM source WHERE TradingDay IN ({days}) AND {code}%{int(modulus)}=0 '
                f'AND {code}//1000 IN ({prefixes})')
        con.execute('CREATE TEMP VIEW selected AS ' + base)
        stats = con.execute('SELECT TradingDay,count(*) AS selected_source_rows,'
                            'count(*) FILTER(WHERE absolute_ms IS NULL) AS invalid_clock_rows,'
                            'count(*)-count(DISTINCT (code,absolute_ms)) AS duplicate_timestamp_excess '
                            'FROM selected GROUP BY TradingDay').df()
        con.execute('CREATE TEMP VIEW continuous AS SELECT *,absolute_ms//60000 AS minute FROM selected '
                    'WHERE (absolute_ms>=34200000 AND absolute_ms<41400000) '
                    'OR (absolute_ms>=46800000 AND absolute_ms<53820000)')
        count = con.execute('SELECT TradingDay,count(*) AS continuous_source_rows '
                            'FROM continuous GROUP BY TradingDay').df()
        stats = stats.merge(count, on='TradingDay', how='left').fillna(0)
        # Earliest event is chosen before any bid/ask validity or depth filter.
        selected = con.execute('SELECT * EXCLUDE(code,absolute_ms) FROM continuous '
            'QUALIFY row_number() OVER(PARTITION BY TradingDay,code,minute '
            'ORDER BY absolute_ms,source_row)=1 ORDER BY TradingDay,code,minute').df()
    raw = output / f"selected_books_{entry['days'][0]}.parquet"
    selected.to_parquet(raw, index=False)
    batches = list(iter_l2_batches(raw, 'snapshot', columns=COLUMNS, include_tagged=True))
    import pyarrow as pa
    canonical = pa.Table.from_batches(batches).to_pandas()
    canonical['SecuCode'] = pd.to_numeric(canonical.SecuCode).astype('int64')
    absolute = clock_ms(canonical.TickTime.to_numpy(), entry['clock_profile'])
    if not np.isfinite(absolute).all():
        raise ValueError('selected book has invalid explicit clock')
    canonical['minute'] = (absolute // 60000).astype('int64')
    h, m, s = absolute // 3600000, (absolute // 60000) % 60, (absolute // 1000) % 60
    canonical['TickTime'] = (h * 10000000 + m * 100000 + s * 1000 + absolute % 1000).astype('int64')
    canonical['source_row'] = selected.source_row.to_numpy()
    _source_unchanged(receipt)
    receipt['clock_profile'] = entry['clock_profile']
    return canonical, stats, receipt


def read_stream(entry: dict, kind: str, codes, output: Path):
    """Read all events for the declared common-security audit, preserving row order."""
    with _connect(output) as con:
        path, security, clock, names = _raw_view(con, entry, kind)
        receipt = _fingerprint(path)
        candidate = ['OrderID', 'DBOrderID', 'OrderType'] if kind == 'order' else ['DealID','BuyID','SellID','Side']
        columns = ['Price', 'Volume', *candidate, 'Channel', 'BizIndex']
        columns = [name for name in columns if name in names]
        projected = ','.join(f'"{name}"' for name in columns)
        code_list = ','.join(str(int(code)) for code in codes)
        frame = con.execute(f'SELECT TRY_CAST("{security}" AS BIGINT) AS SecuCode,'
            f'{_clock_sql(clock,entry["clock_profile"])} AS time_ms_absolute,{projected},file_row_number AS source_row '
            f'FROM source WHERE TradingDay=? AND TRY_CAST("{security}" AS BIGINT) IN ({code_list}) '
            'ORDER BY file_row_number', [int(entry['day'])]).df()
    _source_unchanged(receipt)
    receipt['clock_profile'] = entry['clock_profile']
    return frame, receipt


def _load_daily_features(spec: dict, day: int):
    daily_root, basic_root = Path(spec['daily_root']), Path(spec['daily_basic_root'])
    partitions = sorted(p.name.split('=')[-1] for p in daily_root.glob('trade_date=*') if p.is_dir())
    prior = [date for date in partitions if date < str(day)][-20:]
    if len(prior) < 20:
        raise ValueError('daily calendar has fewer than 20 prior sessions')
    frames, inputs = [], []
    for date in prior:
        files = sorted((daily_root / f'trade_date={date}').glob('*.parquet'))
        if not files:
            raise ValueError(f'empty prior daily partition {date}')
        for path in files:
            inputs.append(_fingerprint(path))
            frames.append(pd.read_parquet(path, columns=['symbol','trade_date','amount','close','pre_close']))
    daily = pd.concat(frames, ignore_index=True)
    daily['SecuCode'] = pd.to_numeric(daily.symbol.astype(str).str.split('.').str[0], errors='coerce')
    daily = daily.loc[daily.SecuCode.notna()].copy()
    daily['SecuCode'] = daily.SecuCode.astype('int64')
    daily['trade_date'] = daily.trade_date.astype(str).str.replace('-', '', regex=False)
    basic_paths = sorted((basic_root / f'trade_date={prior[-1]}').glob('*.parquet'))
    if not basic_paths:
        raise ValueError('previous-session market-cap partition missing')
    for path in basic_paths:
        inputs.append(_fingerprint(path))
    basic = pd.concat([pd.read_parquet(path, columns=['symbol','trade_date','circ_mv']) for path in basic_paths])
    basic['SecuCode'] = pd.to_numeric(basic.symbol.astype(str).str.split('.').str[0], errors='raise').astype('int64')
    basic['trade_date'] = basic.trade_date.astype(str).str.replace('-', '', regex=False)
    result = lagged_features(daily, basic, str(day))
    return result, inputs, {'day': day, 'history_start': prior[0], 'history_end': prior[-1],
                            'required_prior_sessions': 20, 'reconstructed_history_not_verified_release_times': True}


def _terciles(values: pd.Series) -> pd.Series:
    labels = pd.Series('unavailable', index=values.index, dtype='object')
    valid = values.notna() & np.isfinite(values)
    if valid.sum() >= 3:
        labels.loc[valid] = pd.qcut(values.loc[valid].rank(method='first'), 3, labels=['low','middle','high']).astype(str)
    return labels


def _aggregate_groups(frame: pd.DataFrame, column: str):
    return {str(group): summarize(rows) for group, rows in frame.groupby(column, observed=True)}


def run(spec_path: Path, output_root: Path):
    spec = json.loads(spec_path.read_text())
    validate_spec(spec)
    if spec.get('price_unit') != 'integer_cent' or spec.get('quantity_unit') != 'share':
        raise ValueError('explicit integer-cent/share units required')
    output = resolve_output_root({'output_root': str(output_root)})
    output.mkdir(parents=True, exist_ok=False)
    (output / 'spec.json').write_text(json.dumps(spec, indent=2) + '\n')
    all_books, frames, receipts, audits, feature_receipts, covariate_audits = {}, [], [], [], [], []
    for entry in spec['snapshot_sources']:
        print(f"Selecting earliest books: {entry['days']}", flush=True)
        books, stats, receipt = sample_books(entry, output, modulus=int(spec.get('security_modulus',37)))
        receipts.append(receipt)
        for day in entry['days']:
            sample = books.loc[books.TradingDay.eq(day)].copy()
            if sample.empty:
                raise ValueError(f'no sampled books for declared day {day}')
            all_books[int(day)] = sample
            measured, diagnostics = measure(sample)
            features, input_receipts, feature_audit = _load_daily_features(spec, int(day))
            feature_receipts.extend(input_receipts)
            covariate_audits.append(feature_audit)
            for column, label in [('adv20_cny','adv_group'),('market_cap_cny','cap_group'),('volatility20','volatility_group')]:
                features[label] = _terciles(features[column])
            measured = measured.merge(features, on='SecuCode', how='left', validate='many_to_one')
            for label in ['adv_group','cap_group','volatility_group']:
                measured[label] = measured[label].fillna('unavailable')
            measured['time_bucket'] = np.select([measured.minute.lt(600), measured.minute.lt(690),
                measured.minute.lt(840)], ['opening','late_morning','early_afternoon'], default='late_afternoon')
            measured.to_parquet(output / f'measurements_{day}.parquet', index=False)
            sample[['SecuCode','TradingDay','minute','TickTime','source_row']].to_parquet(output / f'book_bins_{day}.parquet', index=False)
            stats_row = stats.loc[stats.TradingDay.eq(day)].iloc[0].to_dict()
            coverage = minute_coverage(sample, sample.SecuCode.unique())
            audit = {'day':int(day), 'sampled_securities':int(sample.SecuCode.nunique()),
                'sampled_snapshots':len(sample), **{key:int(value) for key,value in stats_row.items() if key!='TradingDay'},
                **diagnostics, **coverage}
            audits.append(audit)
            frames.append(measured)
            print(f'{day}: {len(sample)} sampled, {len(measured)} valid books', flush=True)
    combined = pd.concat(frames, ignore_index=True)
    if combined.duplicated(['TradingDay','SecuCode','minute']).any():
        raise ValueError('duplicate measured security/day/minute')
    for receipt in receipts+feature_receipts:
        _source_unchanged(receipt)
    day_a, day_b = map(int, spec['comparison_days'])
    common = sorted(set(all_books[day_a].SecuCode) & set(all_books[day_b].SecuCode))
    common_frames = {str(day): combined.loc[combined.TradingDay.eq(day) & combined.SecuCode.isin(common)]
                     for day in [day_a,day_b]}
    paired = common_frames[str(day_a)][['SecuCode','minute']].merge(
        common_frames[str(day_b)][['SecuCode','minute']], on=['SecuCode','minute'], validate='one_to_one')
    comparisons = {'days':[day_a,day_b], 'common_securities':len(common),
        'minute_coverage':{str(day):minute_coverage(all_books[day],common) for day in [day_a,day_b]},
        'common_security_results':{day:summarize(frame) for day,frame in common_frames.items()},
        'paired_valid_security_minutes':len(paired),
        'paired_results':{day:summarize(frame.merge(paired,on=['SecuCode','minute'],validate='one_to_one'))
                          for day,frame in common_frames.items()}}
    event_results = {}
    for event in spec['event_sources']:
        day = int(event['day'])
        print(f'Auditing common-security orders/trades: {day}', flush=True)
        orders, order_receipt = read_stream(event['order'], 'order', common, output)
        trades, trade_receipt = read_stream(event['deal'], 'deal', common, output)
        receipts.extend([order_receipt,trade_receipt])
        result = {'orders':stream_audit(orders,'order'), 'trades':stream_audit(trades,'deal')}
        for label, frame in [('orders',orders),('trades',trades)]:
            frame.to_parquet(output / f'{label}_{day}_common.parquet', index=False)
        lookup = orders
        if 'preopen_order' in event:
            preopen, preopen_receipt = read_stream(event['preopen_order'],'order',common,output)
            receipts.append(preopen_receipt)
            identity = ['SecuCode','OrderID','time_ms_absolute','Price','Volume','OrderType']
            overlap = orders[identity].merge(preopen[identity].drop_duplicates(),on=identity,how='inner')
            result['preopening_orders'] = stream_audit(preopen,'order')
            result['preopening_overlap_rows'] = len(overlap)
            # Lookup presence is reported for the union; overlap is never silently removed.
            lookup = pd.concat([orders,preopen],ignore_index=True)
            preopen.to_parquet(output / f'preopening_orders_{day}_common.parquet',index=False)
        result['references'] = [reference_audit(lookup,trades,candidate)
                                 for candidate in ['OrderID','DBOrderID'] if candidate in lookup]
        result['dynamic_replay_gate'] = 'not_established_special_event_semantics_and_queue_order_unverified'
        event_results[str(day)] = result
        print(f'{day}: {len(orders)} selected orders, {len(trades)} selected trades',flush=True)
    summary = {'schema_version':'ashare_execution_costs.expansion.private.v1',
        'study_id':'ashare_execution_costs','evidence':'descriptive_historical_static_expansion',
        'measurement_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'pilot_code_sha256':hashlib.sha256(Path(measure.__code__.co_filename).read_bytes()).hexdigest(),
        'spec':spec,'inputs':receipts,'daily_inputs':list({row['path']:row for row in feature_receipts}.values()),
        'audit':audits,'covariate_audit':covariate_audits,'comparison':comparisons,'event_audit':event_results,
        'pooled':summarize(combined),
        'by_day':{str(day):summarize(rows) for day,rows in combined.groupby('TradingDay')},
        'by_adv_group':_aggregate_groups(combined,'adv_group'),
        'by_cap_group':_aggregate_groups(combined,'cap_group'),
        'by_volatility_group':_aggregate_groups(combined,'volatility_group'),
        'by_time_bucket':_aggregate_groups(combined,'time_bucket'),
        'covariate_missing':{column:int(combined[column].isna().sum()) for column in ['adv20_cny','market_cap_cny','volatility20']},
        'uncertainty':'selected-date/security descriptive quantiles; not population confidence intervals',
        'dynamic_impact_calibrated':False,'actual_order_calibrated':False}
    (output / 'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(f'Private expansion summary: {output / "summary.json"}',flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,required=True)
    parser.add_argument('--output-root',type=Path,required=True)
    args = parser.parse_args()
    run(args.spec,args.output_root)


if __name__ == '__main__':
    main()
