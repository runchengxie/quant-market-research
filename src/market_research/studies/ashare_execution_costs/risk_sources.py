"""Hash-bound public termination decisions with conservative availability."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

from .minute import ZONE
from .risk_guards import _validated_events

RULE = 'next_exchange_trading_day_09:00_Asia/Shanghai_after_date_only_publication'
CORE = ['symbol', 'event_id', 'event_type', 'available_time']


def _read_json(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    try:
        value = json.loads(path.read_text(), object_pairs_hook=unique)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('unreadable risk source JSON') from exc
    if not isinstance(value, dict):
        raise ValueError('risk source JSON must be an object')
    return value


def _strings(values, label):
    if (not isinstance(values, list) or not values
            or any(not isinstance(v, str) or not v.strip() for v in values)
            or len(set(values)) != len(values)):
        raise ValueError(f'invalid {label}')
    return values


def load_risk_events(packet_path, sessions, expected_symbols=None) -> tuple[pd.DataFrame, dict]:
    """Verify every reference, exact normalized facts and named subset coverage.

    Supply a complete exchange-session calendar around each publication date.
    Date-only notices become available at 09:00 Shanghai on the next session.
    Coverage is a declared selected-baseline subset, never all-market coverage.
    Delisting dates and future security names do not generate event signals.
    """
    path = Path(packet_path).resolve()
    packet = _read_json(path)
    if packet.get('schema') != 'execution-risk-events-source.v1':
        raise ValueError('unsupported risk source schema')
    refs = packet.get('source_refs')
    if not isinstance(refs, list) or not refs:
        raise ValueError('missing risk source references')
    bound = {}
    for ref in refs:
        if (not isinstance(ref, dict) or set(ref) != {'name', 'path', 'sha256'}
                or any(not isinstance(ref[k], str) or not ref[k].strip() for k in ref)
                or re.fullmatch('[0-9a-f]{64}', ref['sha256']) is None
                or ref['name'] in bound):
            raise ValueError('invalid or duplicate risk source reference')
        source = Path(ref['path'])
        if not source.is_absolute():
            source = path.parent / source
        try:
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
        except OSError as exc:
            raise ValueError('unreadable risk source reference') from exc
        if digest != ref['sha256']:
            raise ValueError('risk source hash mismatch')
        bound[ref['name']] = ref
    fact_ref = packet.get('facts_ref')
    if not isinstance(fact_ref, dict) or bound.get(fact_ref.get('name')) != fact_ref:
        raise ValueError('facts reference is not exactly bound')
    fact_path = Path(fact_ref['path'])
    facts = _read_json(fact_path if fact_path.is_absolute() else path.parent / fact_path)
    if facts.get('schema') != 'execution-risk-event-facts.v1':
        raise ValueError('unsupported risk facts schema')
    events = packet.get('events')
    fact_events = facts.get('events')
    if (not isinstance(events, list) or not events or not isinstance(fact_events, list)
            or any(not isinstance(e, dict) for e in events + fact_events)):
        raise ValueError('invalid risk event records')
    frame = pd.DataFrame(events)
    _validated_events(frame)  # Strict independent identities and aware timestamps.
    fact_frame = pd.DataFrame(fact_events)
    _validated_events(fact_frame)
    if set(frame.event_id) != set(fact_frame.event_id):
        raise ValueError('risk packet and facts event identities differ')
    try:
        calendar = sorted({pd.Timestamp(str(day)) for day in sessions})
    except (ValueError, TypeError) as exc:
        raise ValueError('invalid exchange sessions') from exc
    if (not calendar or any(pd.isna(day) or day.tzinfo is not None
                            or day != day.normalize() for day in calendar)):
        raise ValueError('exchange sessions must be valid naive dates')
    fact_by_id = {fact['event_id']: fact for fact in fact_events}
    for event in events:
        fact = fact_by_id[event['event_id']]
        if any(event.get(field) != fact.get(field) for field in CORE):
            raise ValueError('risk packet and normalized facts disagree')
        source_names = _strings(event.get('source_refs'), 'event source references')
        if any(name not in bound or name == fact_ref['name'] for name in source_names):
            raise ValueError('event source reference is not bound primary evidence')
        primary_ref = fact.get('primary_file_ref')
        if primary_ref not in source_names:
            raise ValueError('fact primary reference does not match event')
        if Path(bound[primary_ref]['path']).suffix.lower() != '.pdf':
            raise ValueError('termination primary evidence must be a bound PDF')
        if 'source_refs' in fact and fact['source_refs'] != source_names:
            raise ValueError('fact source references do not match event')
        if (fact.get('availability_rule') != RULE
                or fact.get('publication_intraday_timestamp') is not None):
            raise ValueError('unsupported source availability rule')
        value = fact.get('primary_publication_date')
        if not isinstance(value, str) or re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) is None:
            raise ValueError('invalid primary publication date')
        try:
            publication = pd.Timestamp(value)
        except ValueError as exc:
            raise ValueError('invalid primary publication date') from exc
        if calendar[0] > publication:
            raise ValueError('exchange calendar does not cover publication')
        later = [day for day in calendar if day > publication]
        if not later:
            raise ValueError('exchange calendar has no next publication session')
        expected = later[0].tz_localize(ZONE) + pd.Timedelta(hours=9)
        if pd.Timestamp(event['available_time']).tz_convert(ZONE) != expected:
            raise ValueError('event availability is not conservative next-session 09:00')
    coverage = packet.get('coverage')
    if (not isinstance(coverage, dict)
            or coverage.get('scope') != 'selected_baseline_109_2024_delisted'
            or coverage.get('complete_for_scope') is not True
            or coverage.get('all_market_announcement_coverage') is not False):
        raise ValueError('risk coverage must declare the complete selected subset only')
    symbols = set(_strings(coverage.get('symbols'), 'coverage symbols'))
    if symbols != set(frame.symbol):
        raise ValueError('risk coverage symbols do not exactly match events')
    if expected_symbols is not None and symbols != set(expected_symbols):
        raise ValueError('risk coverage does not match expected selected symbols')
    flags = packet.get('source_flags', [])
    if not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags):
        raise ValueError('invalid source flags')
    return frame[CORE].copy(), dict(
        packet_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        source_refs=refs, facts_ref=fact_ref, verified_source_count=len(bound),
        coverage=coverage, source_flags=flags, event_count=len(frame),
        availability_rule=RULE, pit_class='reconstructed_pit', revision_safe=False,
        calendar_assumption='caller_supplies_complete_exchange_sessions',
    )
