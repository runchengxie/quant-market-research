"""Source-bound, nontrading delisted-share valuation hypotheses.

This module creates valuation marks only: it does not create fills, transfer
holdings, or infer cash recovery. Native observations remain unverified quotes.
"""
from bisect import bisect_left
from datetime import datetime, timedelta
import hashlib
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

ZONE = ZoneInfo('Asia/Shanghai')
MODES = {'full_impairment', 'impairment_then_observed',
         'termination_decision_full_impairment',
         'termination_decision_impairment_then_observed'}


def _time(value):
    try:
        result = datetime.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ValueError('invalid aware event time') from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError('event time must be timezone-aware')
    return result.astimezone(ZONE)


def _day(value):
    try:
        return datetime.strptime(value, '%Y%m%d').date()
    except (TypeError, ValueError) as error:
        raise ValueError('date must be YYYYMMDD') from error


def _at(day, hour=9):
    return datetime.combine(day, datetime.min.time(), ZONE).replace(hour=hour)


def build_valuation_policy(packet_path: Path, inputs: dict, mode: str) -> tuple[list, dict]:
    """Validate immutable evidence and create causal in-window valuation marks."""
    if mode not in MODES:
        raise ValueError('unsupported delist valuation mode')
    packet_path = Path(packet_path)
    packet_bytes = packet_path.read_bytes()
    packet = json.loads(packet_bytes)
    if packet.get('schema', packet.get('schema_version')) != 'execution-delist-policy-source.v1':
        raise ValueError('unsupported delist policy source schema')
    study = packet['study']
    if any(inputs.get(key) != study[key] for key in ('start', 'end')):
        raise ValueError('delist policy study window mismatch')
    start, end = _day(study['start']), _day(study['end'])
    if start > end:
        raise ValueError('reversed study window')
    session_values = inputs.get('session_dates')
    if not session_values or len(session_values) != len(set(session_values)):
        raise ValueError('unique actual session_dates are required')
    sessions = sorted(_at(_day(value)) for value in session_values
                      if start <= _day(value) <= end)
    if not sessions or sessions[0].date() != start or sessions[-1].date() != end:
        raise ValueError('actual sessions must cover the bound study window')
    selected = inputs.get('selected_symbols', study.get('selected_symbols'))
    if not selected or len(selected) != len(set(selected)):
        raise ValueError('selected symbols must be explicitly bound and unique')
    sources, hashes, verdict_rows, native_frames = {}, {}, [], []
    normalized_rows = []
    for ref in packet['source_refs']:
        name = ref['name']
        if name in sources:
            raise ValueError('duplicate source reference ID')
        source = Path(ref['path'])
        if not source.is_absolute():
            source = packet_path.parent / source
        raw = source.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != ref['sha256']:
            raise ValueError(f'source hash mismatch: {name}')
        sources[name], hashes[name] = source, digest
        if source.suffix == '.json':
            content = json.loads(raw)
            if name == 'normalized_facts':
                normalized_rows = content['symbols']
            if isinstance(content, dict) and isinstance(content.get('symbols'), list):
                rows = content['symbols']
                if rows and isinstance(rows[0], dict) and 'last_raw_close' in rows[0]:
                    verdict_rows.extend((name, row) for row in rows)
        elif source.suffix == '.parquet':
            columns = set(pd.read_parquet(source).columns)
            if {'successor_code', 'date', 'close'} <= columns:
                frame = pd.read_parquet(source, columns=['successor_code', 'date', 'close'])
                native_frames.append((name, frame))
    if not normalized_rows:
        raise ValueError('bound normalized source facts are required')
    if not verdict_rows or not native_frames:
        raise ValueError('bound investigation verdict and native quotes are required')
    decision_trigger = mode.startswith('termination_decision_')
    observed_mode = mode.endswith('impairment_then_observed')
    events, seen_symbols, seen_times = [], set(), set()
    effective_dates = {}
    legal_pit = True
    quote_rows = excluded_after = superseded = 0
    for instrument in packet['instruments']:
        symbol = instrument['symbol']
        if symbol not in selected or symbol in seen_symbols:
            raise ValueError('instrument is unselected or duplicated')
        seen_symbols.add(symbol)
        facts = [row for row in normalized_rows if row['symbol'] == symbol]
        if len(facts) != 1:
            raise ValueError('instrument requires one normalized source fact')
        fact = facts[0]
        bindings = {
            'decision_available_time': fact['termination_decision_available_time'],
            'legal_exact_delist_date_available_time': fact['legal_announcement_available_time'],
            'delist_date': fact['delist_date'], 'successor_code': fact['mapped_code'],
            'first_transfer_date': fact['first_transfer_date'],
            'last_exchange_close': fact['last_actual_price']['close'],
        }
        if any(instrument.get(key) != value for key, value in bindings.items()):
            raise ValueError('instrument disagrees with normalized source facts')
        if fact['tradable'] is not False:
            raise ValueError('normalized facts must explicitly retain nontrading status')
        ref_names = instrument.get('source_refs', [])
        if not ref_names or len(ref_names) != len(set(ref_names)) or not set(ref_names) <= sources.keys():
            raise ValueError('invalid instrument source bindings')
        verdicts = [row for name, row in verdict_rows if name in ref_names and row['symbol'] == symbol]
        if len(verdicts) != 1:
            raise ValueError('instrument requires exactly one bound investigation verdict')
        verdict = verdicts[0]
        if (verdict['delist_date'] != instrument['delist_date']
                or verdict['last_raw_close'] != instrument['last_exchange_close']
                or verdict['successor_confirmation_code'] != instrument['successor_code']):
            raise ValueError('instrument disagrees with investigation verdict')
        delist_day = _day(instrument['delist_date'])
        effective = _time(instrument['delist_effective_time'])
        legal_value = instrument.get('legal_exact_delist_date_available_time')
        legal_available = _time(legal_value) if legal_value else None
        decision = _time(instrument['decision_available_time'])
        legal_pit = legal_pit and legal_available is not None and legal_available <= effective
        if effective != _at(delist_day) or decision > effective:
            raise ValueError('invalid delist effective or decision time')
        if decision_trigger:
            if decision != _at(decision.date()):
                raise ValueError('termination decision hypothesis must start at session 09:00')
            effective, available = decision, decision
        else:
            if legal_available is None or legal_available > effective:
                raise ValueError('exact legal delist date must be known by delist 09:00')
            available = max(legal_available, decision)
        if start <= effective.date() <= end and effective not in sessions:
            raise ValueError('impairment trigger must belong to actual session_dates')
        effective_dates[symbol] = effective.isoformat()
        if not math.isfinite(instrument['last_exchange_close']) or instrument['last_exchange_close'] <= 0:
            raise ValueError('invalid last exchange close')

        def emit(moment, known, value, basis, source):
            key = (symbol, moment)
            if key in seen_times:
                raise ValueError('duplicate symbol effective time')
            seen_times.add(key)
            if start <= moment.date() <= end:
                events.append(dict(event_id=f'{mode}:{symbol}:{moment.isoformat()}', symbol=symbol,
                                   effective_time=moment.isoformat(), available_time=known.isoformat(),
                                   value_per_share=value, basis=basis, source=source))

        emit(effective, available, 0.0, 'declared_full_impairment_hypothesis',
             f'packet_sha256:{hashlib.sha256(packet_bytes).hexdigest()}')
        first_transfer = _day(instrument['first_transfer_date'])
        if instrument['quote_evidence_level'] != 'single_source_unverified':
            raise ValueError('unsupported quote evidence level')
        seen_dates = set()
        pending = {}
        for quote in instrument['quotes']:
            quote_rows += 1
            day = _day(quote['date'])
            known = _time(quote['available_time'])
            value = quote['close']
            if day in seen_dates or day < first_transfer or day < delist_day:
                raise ValueError('duplicate or premature successor quote')
            seen_dates.add(day)
            if known < _at(day + timedelta(days=1)):
                raise ValueError('quote cannot be available before next calendar day 09:00')
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError('invalid successor close')
            if quote['source_ref'] not in ref_names:
                raise ValueError('quote source is not bound to instrument')
            matches = []
            for name, frame in native_frames:
                if name in ref_names:
                    found = frame.loc[frame.successor_code.astype(str).eq(instrument['successor_code'])
                                      & frame.date.astype(str).eq(quote['date'])]
                    matches.extend(found.close.tolist())
            if len(matches) != 1 or matches[0] != value:
                raise ValueError('quote must exactly match one bound native row')
            index = bisect_left(sessions, known)
            if index == len(sessions):
                excluded_after += 1
            elif observed_mode:
                moment = sessions[index]
                candidate = (known, day, value, quote['source_ref'])
                if moment in pending:
                    superseded += 1
                    if candidate[:2] > pending[moment][:2]:
                        pending[moment] = candidate
                else:
                    pending[moment] = candidate
        for moment, (known, day, value, source) in sorted(pending.items()):
            emit(moment, known, value, 'observed_single_source_unverified_nontrading_quote', source)
    events.sort(key=lambda row: (row['effective_time'], row['symbol'], row['event_id']))
    audit = dict(mode=mode, hypothesis='Declared impairment; observed quotes are optional nontrading marks',
                 quote_verified=False, revision_safe=False, nontrading=True,
                 source_hashes=hashes, packet_sha256=hashlib.sha256(packet_bytes).hexdigest(),
                 trigger=('confirmed_termination_decision_first_session' if decision_trigger
                          else 'exact_legal_delist_date'),
                 impairment_assumption=True, effective_dates=effective_dates,
                 legal_exact_date_pit_verified=legal_pit,
                 retrospective_transfer_facts=True,
                 observed_quote_rows=quote_rows, excluded_after_window=excluded_after,
                 superseded_quote_rows=superseded,
                 session_dates_sha256=hashlib.sha256(json.dumps(
                     [moment.strftime('%Y%m%d') for moment in sessions]).encode()).hexdigest(),
                 events=len(events), start=study['start'], end=study['end'])
    return events, audit
