"""Read-only, hash-bound prepared-input checks; never a historical PIT certificate.

Passing this audit does not prove order fills or complete NAV. Those require
actual simulated holdings, missing-mark checks and per-run event ownership.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re

import pandas as pd
import pyarrow.parquet as pq

ZONE = 'Asia/Shanghai'


def _sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f'nonfinite JSON value: {value}')
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def _day(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{8}', value):
        raise ValueError('invalid session date')
    try:
        return pd.Timestamp(value).strftime('%Y%m%d')
    except ValueError as error:
        raise ValueError('invalid session date') from error


def _aware(frame, columns):
    for column in columns:
        if column not in frame or not isinstance(frame[column].dtype, pd.DatetimeTZDtype):
            raise ValueError(f'timezone-aware {column} required')
        if str(frame[column].dt.tz) != ZONE or frame[column].isna().any():
            raise ValueError(f'native timezone {ZONE} required: {column}')


def audit_prepared(prepared: Path, *, expected_implementation: dict | None = None) -> dict:
    """Reject invalid evidence before simulation; return a JSON-safe audit receipt.

    Source hashes are recorded lineage, not a claim that raw upstream snapshots
    were revalidated. The frozen daily panel supplies the local session calendar.
    """
    root = Path(prepared).resolve()
    inputs = _json(root / 'inputs.json')
    hashes = inputs.get('input_sha256', {})
    required = {'bars.parquet', 'daily-panel.parquet', 'symbols.json',
                'corporate-actions.json', 'unverified-corporate-actions.json'}
    variants = inputs.get('variants', {})
    if not isinstance(hashes, dict) or not variants:
        raise ValueError('missing input hashes or target variants')
    required.update(f'targets-{key}.parquet' for key in variants)
    if not required <= hashes.keys():
        raise ValueError('missing hash-bound prepared bars/calendar/targets/actions')
    for name, digest in hashes.items():
        if (not isinstance(name, str) or Path(name).name != name or name in {'.', '..'}
                or '\\' in name or (root / name).resolve().parent != root):
            raise ValueError('prepared input filename escapes directory')
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('invalid input sha256')
        if not (root / name).is_file() or _sha(root / name) != digest:
            raise ValueError(f'prepared input hash mismatch: {name}')
    # Parse all hash-bound JSON, including evidence packets, strictly.
    documents = {name: _json(root / name) for name in hashes if name.endswith('.json')}
    study = inputs.get('experiment_study') or {}
    source_refs = study.get('source_refs', [])
    if not isinstance(source_refs, list):
        raise ValueError('source references must be a list')
    references = {}
    for reference in source_refs:
        if not isinstance(reference, dict) or set(reference) != {'name', 'path', 'sha256'}:
            raise ValueError('invalid source reference schema')
        name, path, digest = (reference[k] for k in ['name', 'path', 'sha256'])
        if (not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_]*', name)
                or name in references or not isinstance(path, str)
                or not Path(path).is_absolute() or str(Path(path).resolve()) != path
                or not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest)):
            raise ValueError('invalid source reference name/path/sha256')
        if not Path(path).is_file() or _sha(Path(path)) != digest:
            raise ValueError('source reference hash mismatch')
        references[name] = Path(path)
    symbols = documents['symbols.json']
    if (not isinstance(symbols, list) or len(set(symbols)) != len(symbols) or not symbols
            or any(not isinstance(s, str) or not re.fullmatch(r'(00\d{4}\.SZ|60\d{4}\.SH)', s)
                   for s in symbols)):
        raise ValueError('invalid main-board symbol scope')
    scope = set(symbols)
    panel = pd.read_parquet(root / 'daily-panel.parquet')
    if not {'ts_code', 'trade_date', 'close'} <= set(panel) or panel.empty:
        raise ValueError('missing daily calendar/marks')
    panel['trade_date'] = panel.trade_date.astype(str).map(_day)
    if panel.duplicated(['ts_code', 'trade_date']).any():
        raise ValueError('duplicate daily panel keys')
    if set(panel.ts_code) != scope:
        raise ValueError('daily panel symbol scope differs')
    if not panel.close.map(lambda x: pd.notna(x) and math.isfinite(float(x)) and x > 0).all():
        raise ValueError('invalid daily mark price')
    days = sorted(panel.trade_date.unique())
    if (days[0] != inputs.get('start') or days[-1] != inputs.get('end')
            or len(days) != inputs.get('sessions')):
        raise ValueError('prepared session calendar differs from inputs')
    warnings = ['Historical source availability is reconstructed; revision-safe PIT is not established.',
                'Fill eligibility and complete NAV require the simulation and per-run held-inventory gates.']
    if 'session_dates' in inputs and inputs['session_dates'] != days:
        raise ValueError('declared session calendar differs')
    if 'session-dates.json' in documents and documents['session-dates.json'] != days:
        raise ValueError('declared session calendar differs')
    authoritative_calendar = 'trade_cal' in references
    if authoritative_calendar:
        calendar = pd.read_parquet(references['trade_cal'])
        if not {'exchange', 'is_open', 'cal_date'} <= set(calendar):
            raise ValueError('authoritative trading calendar schema missing')
        calendar['cal_date'] = calendar.cal_date.astype(str).map(_day)
        actual_days = sorted(calendar.loc[
            calendar.exchange.eq('SSE') & calendar.is_open.eq(1)
            & calendar.cal_date.between(days[0], days[-1]), 'cal_date'].unique())
        if actual_days != days:
            raise ValueError('authoritative trading calendar differs from prepared sessions')
        if 'session-dates.json' not in documents:
            raise ValueError('missing hash-bound declared session calendar')
    else:
        warnings.append('Authoritative upstream calendar is not independently reloaded; local daily-panel dates are checked.')
    # Stream bars in bounded batches. DuckDB handles cross-batch uniqueness.
    import duckdb
    with duckdb.connect() as con:
        duplicate = con.execute('SELECT count(*) FROM (SELECT symbol,time FROM read_parquet(?) '
                                'GROUP BY symbol,time HAVING count(*)>1)',
                                [str(root / 'bars.parquet')]).fetchone()[0]
    if duplicate:
        raise ValueError('duplicate minute bar keys')
    seen_symbols, seen_days, books = set(), set(), set()
    rows = 0
    for batch in pq.ParquetFile(root / 'bars.parquet').iter_batches(batch_size=65536):
        frame = batch.to_pandas()
        needed = {'symbol', 'time', 'interval_start', 'open', 'high', 'low', 'close',
                  'volume', 'amount', 'up_limit', 'down_limit', 'tradable'}
        if not needed <= set(frame):
            raise ValueError('missing minute bar schema')
        _aware(frame, ['time', 'interval_start'])
        if not set(frame.symbol) <= scope:
            raise ValueError('minute symbol scope differs')
        bar_days = frame.time.dt.strftime('%Y%m%d')
        if not set(bar_days) <= set(days):
            raise ValueError('minute bars outside session calendar')
        prices = frame[['open', 'high', 'low', 'close', 'up_limit', 'down_limit']]
        if (prices.isna().any().any() or not prices.map(math.isfinite).all().all()
                or prices.le(0).any().any()):
            raise ValueError('invalid native minute price')
        liquidity = frame[['volume', 'amount']]
        if (liquidity.isna().any().any() or not liquidity.map(math.isfinite).all().all()
                or liquidity.lt(0).any().any()
                or (frame.volume.eq(0) & frame.amount.gt(0)).any()):
            raise ValueError('invalid native minute liquidity')
        if (frame.interval_start >= frame.time).any():
            raise ValueError('minute availability is not causal')
        if not frame.tradable.isin([True, False]).all():
            raise ValueError('unknown tradability')
        if 'mark_basis' in frame:
            synthetic = frame.mark_basis.ne('observed_bar')
            if (not frame.mark_basis.isin(['observed_bar', 'confirmed_suspension_carry']).all()
                    or frame.loc[synthetic, 'tradable'].any()
                    or frame.loc[synthetic, ['volume', 'amount']].ne(0).any().any()):
                raise ValueError('invalid declared nontradable mark')
            _aware(frame, ['reference_source_time'])
            if (frame.reference_source_time > frame.time).any():
                raise ValueError('mark reference is not causal')
        seen_symbols.update(frame.symbol)
        seen_days.update(bar_days)
        books.update(zip(frame.symbol, bar_days))
        rows += len(frame)
    if not rows or seen_symbols != scope or seen_days != set(days):
        raise ValueError('missing bars for prepared symbol/session scope')
    missing_books = set(zip(panel.ts_code, panel.trade_date)) - books
    if missing_books:
        warnings.append(f'{len(missing_books)} symbol-session books absent; held-inventory NAV gate must resolve them.')
    if inputs.get('count') != 40:
        raise ValueError('prepared target count must equal 40')
    target_checks = {}
    full = None
    if 'full-selection-panel.parquet' in hashes:
        full = pd.read_parquet(root / 'full-selection-panel.parquet', columns=['ts_code', 'trade_date'])
        full['trade_date'] = full.trade_date.astype(str).map(_day)
        if full.duplicated(['ts_code', 'trade_date']).any():
            raise ValueError('duplicate full selection panel keys')
    elif inputs.get('experiment_study') is not None:
        raise ValueError('missing complete universe selection panel for experiment study')
    else:
        warnings.append('Complete selection universe is not retained; this audit does not independently reproduce ranking.')
    for key, metadata in variants.items():
        targets = pd.read_parquet(root / f'targets-{key}.parquet')
        if not {'symbol', 'decision_time', 'entry_time', 'weight'} <= set(targets) or targets.empty:
            raise ValueError('missing target schema')
        _aware(targets, ['decision_time', 'entry_time'])
        if study.get('protocol_profile') is not None and not targets.decision_time.dt.strftime(
                '%H:%M:%S').eq('20:02:00').all():
            raise ValueError('registered protocol requires prior-close 20:02 decision time')
        if targets.duplicated(['symbol', 'entry_time']).any():
            raise ValueError('duplicate target keys')
        if not set(targets.symbol) <= scope:
            raise ValueError('target symbol scope differs')
        prior = dict(zip(days[1:], days[:-1]))
        entry_days = targets.entry_time.dt.strftime('%Y%m%d')
        decision_days = targets.decision_time.dt.strftime('%Y%m%d')
        if ((targets.decision_time >= targets.entry_time).any()
                or not decision_days.eq(entry_days.map(prior)).all()
                or not targets.entry_time.dt.strftime('%H:%M:%S').eq('09:32:00').all()):
            raise ValueError('target selection is not causal prior-session 09:32 entry')
        if (not targets.weight.map(lambda x: pd.notna(x) and math.isfinite(float(x))
                                   and math.isclose(x, .025, abs_tol=1e-12)).all()
                or not targets.groupby('entry_time').size().eq(40).all()):
            raise ValueError('targets must contain 40 equal weights')
        cadence = metadata.get('rebalance_sessions')
        if cadence not in {1, 5} or sorted(set(decision_days)) != days[:-1:cadence]:
            raise ValueError('target rebalance sessions differ')
        if metadata.get('targets', len(targets)) != len(targets):
            raise ValueError('declared target rows differ')
        if full is not None:
            available = set(zip(full.ts_code, full.trade_date))
            if not set(zip(targets.symbol, decision_days)) <= available:
                raise ValueError('target absent from full selection panel on decision day')
        target_checks[key] = {'rows': len(targets), 'snapshots': int(targets.entry_time.nunique())}
    actions = documents['corporate-actions.json']
    event_ids, event_keys = set(), set()
    for event in actions:
        fields = {'event_id', 'symbol', 'available_date', 'record_date', 'ex_date', 'cash_pay_date',
                  'stock_tradable_date', 'cash_per_share', 'stock_per_share', 'withholding_rate'}
        if not fields <= event.keys() or event['symbol'] not in scope:
            raise ValueError('corporate action missing fields or symbol scope')
        available, record, ex = [_day(event[k]) for k in ['available_date', 'record_date', 'ex_date']]
        if not available <= record < ex:
            raise ValueError('corporate action availability is not causal')
        key = (event['symbol'], ex)
        if event['event_id'] in event_ids or key in event_keys:
            raise ValueError('duplicate corporate action keys')
        event_ids.add(event['event_id'])
        event_keys.add(key)
        for amount in ['cash_per_share', 'stock_per_share', 'withholding_rate']:
            value = event[amount]
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError('invalid corporate entitlement')
        if event['withholding_rate'] > 1:
            raise ValueError('invalid withholding rate')
        for amount, date in [('cash_per_share', 'cash_pay_date'), ('stock_per_share', 'stock_tradable_date')]:
            if event[amount] > 0 and (not event[date] or _day(event[date]) < ex):
                raise ValueError('corporate payment/listing date is not causal')
    blocked = documents['unverified-corporate-actions.json']
    if len(blocked) != inputs.get('corporate_action_audit', {}).get('unverified_events'):
        raise ValueError('unverified corporate action count differs')
    if blocked:
        warnings.append(f'{len(blocked)} unverified corporate events require per-run record-date ownership validation.')
    adjustment = inputs.get('adjustment_event_audit', {})
    if adjustment.get('unexplained_changes') != 0:
        raise ValueError('unexplained adjustment events')
    # Retained source references are verified without disclosing private locations.
    evidence_files = adjustment.get('evidence_files_sha256', {})
    for path, digest in evidence_files.items():
        if not re.fullmatch('[0-9a-f]{64}', digest) or _sha(Path(path)) != digest:
            raise ValueError('factor evidence source hash mismatch')
    if 'factor-evidence.json' in hashes:
        if hashes['factor-evidence.json'] != adjustment.get('evidence_manifest_sha256'):
            raise ValueError('factor evidence packet hash binding differs')
        packet = documents['factor-evidence.json']
        lineage = inputs.get('source_manifest_sha256', {})
        if (packet.get('daily_manifest_sha256') != lineage.get('daily')
                or packet.get('dividend_sha256') != lineage.get('dividends')):
            raise ValueError('factor evidence input lineage differs')
        if not evidence_files:
            raise ValueError('missing factor evidence source references')
        def iter_factor_references(value):
            if isinstance(value, dict):
                if 'path' in value and 'sha256' in value:
                    yield value['sha256']
                for child in value.values():
                    yield from iter_factor_references(child)
            elif isinstance(value, list):
                for child in value:
                    yield from iter_factor_references(child)
        if not set(iter_factor_references(packet)) <= set(evidence_files.values()):
            raise ValueError('factor evidence reference hash binding missing')
    lineage = inputs.get('source_manifest_sha256', {})
    if not lineage or any(not isinstance(v, str) or not re.fullmatch('[0-9a-f]{64}', v)
                          for v in lineage.values()):
        raise ValueError('missing or invalid source lineage hashes')
    if inputs.get('revision_safe') is not False or inputs.get('pit_class') != 'reconstructed_pit':
        raise ValueError('historical PIT limitations must be explicit')
    if expected_implementation is not None:
        actual = inputs.get('experiment_study', {}).get('implementation_sha256')
        if actual is None:
            actual = inputs.get('risk_comparison', {}).get('lineage', {}).get('implementation_sha256')
        if actual != expected_implementation:
            raise ValueError('prepared implementation differs')
    return {'schema': 'execution-preflight.v1', 'status': 'passed',
            'inputs_sha256': _sha(root / 'inputs.json'), 'input_sha256': hashes,
            'source_manifest_sha256': lineage, 'pit_class': 'reconstructed_pit',
            'revision_safe': False, 'fill_eligibility_proven': False, 'complete_nav_proven': False,
            'checks': {'bar_rows': rows, 'sessions': len(days), 'symbols': len(scope),
                       'targets': target_checks, 'corporate_events': len(actions),
                       'unverified_corporate_events': len(blocked),
                       'missing_symbol_session_books': len(missing_books),
                       'factor_evidence_sources_verified': len(evidence_files),
                       'source_references_verified': len(references),
                       'authoritative_calendar_verified': authoritative_calendar,
                       'complete_selection_universe_retained': full is not None},
            'warnings': warnings}
