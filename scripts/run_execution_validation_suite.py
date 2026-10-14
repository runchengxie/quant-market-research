"""Run explicit bounded profiles through the formal minute execution provider."""
from __future__ import annotations

import argparse
from dataclasses import asdict, fields
import hashlib
import inspect
import json
import math
import os
from pathlib import Path
import re
import uuid

import pandas as pd
from portfolio_backtester.corporate_actions import CorporateAction
from portfolio_backtester.minute_execution import MinuteExecutionConfig, ValuationEvent, simulate_minute_execution

from market_research.studies.ashare_execution_costs.minute import (
    assert_unowned_events, measure_arrival_shortfall,
)


REQUIRED_OUTPUTS = frozenset({'daily.parquet', 'orders.parquet', 'fills.parquet',
                              'holdings.parquet', 'valuation-ledger.parquet', 'shortfall.parquet'})


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def digest_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def validate_profiles(profiles):
    keys = {field.name for field in fields(MinuteExecutionConfig)}
    if not isinstance(profiles, list) or not profiles:
        raise ValueError('profiles must be an explicit nonempty list')
    result, seen = [], set()
    for row in profiles:
        if not isinstance(row, dict) or set(row) != keys | {'scenario'}:
            raise ValueError('profile must supply scenario and every execution config field')
        name = row['scenario']
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', name) or name in seen:
            raise ValueError('unsafe or duplicate scenario id')
        values = {key: row[key] for key in keys}
        for key, value in values.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'invalid finite numeric config: {key}')
        config = MinuteExecutionConfig(**values)
        if (config.participation_rate > .1 or config.lot_size != 100
                or config.commission_minimum_cny != 0 or config.buy_fee_bp != 1
                or config.sell_fee_bp != 6 or config.sell_tax_bp != 5):
            raise ValueError('profile violates bounded suite execution contract')
        seen.add(name)
        result.append((name, config))
    return result


def validate_profile_binding(prepared, inputs, selected):
    study = inputs['experiment_study']
    protocol_path = Path(prepared) / 'protocol.json'
    digest = sha(protocol_path)
    if digest != study.get('protocol_sha256') or digest != inputs['input_sha256'].get('protocol.json'):
        raise ValueError('profile protocol hash mismatch')
    protocol = json.loads(protocol_path.read_text())
    authorized = study.get('authorized_profiles')
    validate_profiles(authorized)
    global_profiles = protocol.get('profiles')
    validate_profiles(global_profiles)
    if any(row not in global_profiles for row in authorized) or any(row not in authorized for row in selected):
        raise ValueError('chosen profile differs from frozen authorized protocol')


def verify_outputs(path, receipt):
    outputs = receipt.get('output_sha256')
    if not isinstance(outputs, dict) or set(outputs) != REQUIRED_OUTPUTS:
        raise ValueError('completed scenario output hash roster must contain exactly six required ledgers')
    for name, digest in outputs.items():
        if Path(name).name != name or sha(Path(path) / name) != digest:
            raise ValueError('completed scenario output hash mismatch')


def matching_fingerprint(prepared, config, valuation_rows, implementation):
    return digest_json(dict(config=config, valuation_events=valuation_rows,
        execution_inputs={name: sha(Path(prepared) / name) for name in
                          ('bars.parquet', 'corporate-actions.json', 'targets-daily.parquet')},
        execution_implementation={key: implementation[key] for key in
                                  ('engine', 'corporate_contract', 'valuation_contract') if key in implementation}))


def verify_reuse_source(candidate, receipt, implementation):
    prepared = Path(candidate).parent
    if sha(prepared / 'inputs.json') != receipt.get('inputs_sha256'):
        raise ValueError('reuse source input receipt changed')
    inputs = json.loads((prepared / 'inputs.json').read_text())
    if inputs.get('input_sha256') != receipt.get('input_sha256'):
        raise ValueError('reuse source input binding differs')
    for name, digest in receipt['input_sha256'].items():
        if Path(name).name != name or sha(prepared / name) != digest:
            raise ValueError('reuse source prepared input changed')
    fingerprint = matching_fingerprint(prepared, receipt['config'], receipt['valuation_rows'], implementation)
    if fingerprint != receipt.get('simulation_fingerprint'):
        raise ValueError('reuse source simulation fingerprint differs')


def implementation_hashes():
    from market_research.studies.ashare_execution_costs import preflight, risk_sources, risk_guards
    objects = dict(engine=simulate_minute_execution, corporate_contract=CorporateAction,
                   valuation_contract=ValuationEvent, research_methods=measure_arrival_shortfall,
                   preflight=preflight.audit_prepared, risk_sources=risk_sources.load_risk_events,
                   risk_targets=risk_guards.build_risk_targets)
    return dict(runner=sha(Path(__file__)), **{key: sha(Path(inspect.getfile(value)))
                                          for key, value in objects.items()})


def valuation_rows(inputs, bars):
    study = inputs['experiment_study']
    rows = study.get('valuation_events')
    if rows is None:
        return []
    if not isinstance(rows, list):
        raise ValueError('valuation events must be explicit list or null')
    from market_research.studies.ashare_execution_costs.risk_sources import load_risk_events
    packet = Path(study['valuation_source_packet_path'])
    if sha(packet) != study['valuation_source_packet_sha256']:
        raise ValueError('valuation source packet hash mismatch')
    sessions = sorted(pd.Timestamp(day).strftime('%Y%m%d') for day in
                      bars.time.dt.tz_convert('Asia/Shanghai').dt.normalize().unique())
    expected = {'600321.SH', '002621.SZ', '000982.SZ', '600836.SH'}
    events, audit = load_risk_events(packet, sessions, expected_symbols=expected)
    confirmed = events.loc[events.event_type.eq('confirmed_termination')]
    canonical = [dict(event_id=f'termination_decision_full_impairment:{event.event_id}',
        symbol=event.symbol, effective_time=event.available_time, available_time=event.available_time,
        value_per_share=0., basis='declared_full_impairment_hypothesis',
        source=f'packet_sha256:{audit["packet_sha256"]}') for event in confirmed.itertuples(index=False)]
    # Normalize Timestamp values exactly as serialized preparation metadata.
    canonical = json.loads(json.dumps(canonical, default=str))
    if len(canonical) != 4 or set(confirmed.symbol) != expected or rows != canonical:
        raise ValueError('valuation differs from source-bound common four-event zero policy')
    return rows


def execute(prepared: Path, scenario_configs: list[dict], *, reuse_candidates=()):
    from market_research.studies.ashare_execution_costs.preflight import audit_prepared
    prepared = Path(prepared)
    profiles = validate_profiles(scenario_configs)
    implementation = implementation_hashes()
    preflight = audit_prepared(prepared, expected_implementation=implementation)
    inputs = json.loads((prepared / 'inputs.json').read_text())
    validate_profile_binding(prepared, inputs, scenario_configs)
    for name, digest in inputs['input_sha256'].items():
        if Path(name).name != name or sha(prepared / name) != digest:
            raise ValueError('prepared input hash mismatch')
    bars = pd.read_parquet(prepared / 'bars.parquet')
    targets = pd.read_parquet(prepared / 'targets-daily.parquet')
    actions = [CorporateAction(**row) for row in json.loads((prepared / 'corporate-actions.json').read_text())]
    rows = valuation_rows(inputs, bars)
    valuations = [ValuationEvent(**row) for row in rows]
    summaries = []
    candidates = list(map(Path, reuse_candidates))
    for name, config in profiles:
        final = prepared / name
        fingerprint = matching_fingerprint(prepared, asdict(config), rows, implementation)
        binding = dict(config=asdict(config), inputs_sha256=sha(prepared / 'inputs.json'),
                       input_sha256=inputs['input_sha256'], implementation_sha256=implementation,
                       simulation_fingerprint=fingerprint, valuation_rows=rows, profiles_sha256=digest_json(inputs['experiment_study']['authorized_profiles']))
        if final.exists():
            receipt = json.loads((final / 'receipt.json').read_text())
            if any(receipt.get(key) != value for key, value in binding.items()):
                raise ValueError('completed scenario provenance differs')
            verify_outputs(final, receipt)
            summaries.append(receipt['summary'])
            candidates.append(final)
            continue
        source = None
        for candidate in candidates:
            receipt_path = candidate / 'receipt.json'
            if not receipt_path.is_file():
                continue
            receipt = json.loads(receipt_path.read_text())
            if receipt.get('schema_version') != 'execution-validation-scenario.v1':
                continue
            verify_outputs(candidate, receipt)
            if (receipt.get('simulation_fingerprint') == fingerprint
                    and receipt.get('implementation_sha256') == implementation
                    and receipt.get('config') == asdict(config)):
                verify_reuse_source(candidate, receipt, implementation)
                source = (candidate, receipt)
                break
        private = prepared / f'.{name}-inprogress-{uuid.uuid4().hex}'
        private.mkdir()
        if source:
            candidate, old = source
            for filename in old['output_sha256']:
                os.link(candidate / filename, private / filename)
            summary = dict(old['summary'], scenario=name)
            method = dict(execution_method='verified_ledger_reuse', source_path=str(candidate.resolve()),
                          source_receipt_sha256=sha(candidate / 'receipt.json'), matching_fingerprint=fingerprint)
        else:
            result = simulate_minute_execution(targets, bars, config, corporate_actions=actions,
                                                valuation_events=valuations)
            daily, fills, orders = result.daily, result.fills, result.orders
            if (not daily.nav.map(math.isfinite).all() or (daily.cash < -1e-6).any()
                    or not ((daily.nav - daily.cash - daily.positions_value - daily.cash_receivable
                             - daily.stock_receivable_value).abs() < .01).all()
                    or abs(fills.transaction_cost.sum() - daily.transaction_cost.iloc[-1]) > .01
                    or (orders.filled_quantity > orders.quantity + 1e-6).any()):
                raise ValueError('execution accounting checks failed; incomplete private run retained')
            blocked = json.loads((prepared / 'unverified-corporate-actions.json').read_text())
            unowned = assert_unowned_events(result.holdings,
                pd.to_datetime(daily.date).dt.strftime('%Y%m%d').tolist(), blocked)
            for field in ('daily', 'orders', 'fills', 'holdings'):
                getattr(result, field).to_parquet(private / f'{field}.parquet', index=False)
            result.valuation_ledger.to_parquet(private / 'valuation-ledger.parquet', index=False)
            measured, shortfall = measure_arrival_shortfall(orders, fills, bars)
            measured.to_parquet(private / 'shortfall.parquet', index=False)
            summary = dict(scenario=name, variant='daily', capital_cny=config.initial_cash,
                           participation_rate=config.participation_rate, execution_minutes=config.execution_minutes,
                           release_slices=config.release_slices, commission_minimum_cny=config.commission_minimum_cny,
                           sessions=len(daily), terminal_nav=float(daily.nav.iloc[-1] / config.initial_cash),
                           transaction_cost_cny=float(fills.transaction_cost.sum()), orders=len(orders),
                           zero_fill_orders=int(orders.filled_quantity.eq(0).sum()),
                           partial_fill_orders=int((orders.filled_quantity.gt(0) & orders.filled_quantity.lt(orders.quantity)).sum()),
                           valuation_events=len(result.valuation_ledger), unowned_unverified_events=unowned,
                           filled_orders=int(orders.status.eq('filled').sum()),
                           expired_orders=int(orders.status.eq('expired').sum()),
                           cancelled_orders=int(orders.status.eq('cancelled').sum()),
                           mean_one_way_turnover=float(fills.gross_amount.sum() / daily.nav.mean() / len(daily) / 2),
                           clipped_vwap_bars=result.summary['clipped_vwap_bars'],
                           fractional_position_count=len(result.summary['fractional_positions']),
                           negative_cash_sessions=int(daily.cash.lt(-1e-6).sum()), **shortfall)
            method = dict(execution_method='formal_provider_simulation')
        receipt = dict(schema_version='execution-validation-scenario.v1', **binding, **method,
                       summary=summary, output_sha256={p.name: sha(p) for p in private.glob('*.parquet')})
        write_json(private / 'receipt.json', receipt)
        private.rename(final)
        candidates.append(final)
        summaries.append(summary)
        print(name, method['execution_method'], summary['terminal_nav'], flush=True)
    report = dict(schema_version='execution-validation-results.v1', published=False, complete=False,
                  requested_profiles_complete=True, requested_profiles=len(profiles), scenarios=summaries,
                  profiles=scenario_configs, profiles_sha256=digest_json(scenario_configs),
                  implementation_sha256=implementation, preflight=preflight,
                  evidence='modeled_bar_execution_not_live_capacity', valuation_cash_disposal=False,
                  termination_guard_coverage=bool(rows))
    write_json(prepared / 'validation-summary.proposed.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--profiles', required=True, type=Path)
    parser.add_argument('--reuse-candidate', action='append', type=Path, default=[])
    args = parser.parse_args()
    execute(args.output, json.loads(args.profiles.read_text()), reuse_candidates=args.reuse_candidate)


if __name__ == '__main__':
    main()
