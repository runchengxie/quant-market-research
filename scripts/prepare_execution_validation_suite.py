"""Freeze full-universe rule ablations without changing historical inputs."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pandas as pd

from market_research.microcap_execution import load_clean_panel
from market_research.studies.ashare_execution_costs.minute import build_targets
from market_research.studies.ashare_execution_costs.risk_guards import build_risk_targets
from market_research.studies.ashare_execution_costs.risk_sources import load_risk_events

MODES = {'baseline': (False, False, False), 'price_only': (True, False, False),
         'st_only': (False, True, False), 'termination_only': (False, False, True),
         'combined': (True, True, True), 'price_st': (True, True, False)}


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(part)
    return value.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                   allow_nan=False, default=str) + '\n')


def mode_flags(mode):
    if mode not in MODES:
        raise ValueError('unknown validation mode')
    return MODES[mode]


def verify_selected_panel(full, original, symbols):
    selected = full.loc[full.ts_code.isin(symbols)]
    if set(selected.columns) != set(original.columns):
        raise ValueError('selected panel schema differs')
    keys = ['trade_date', 'ts_code']
    pd.testing.assert_frame_equal(
        selected[original.columns].sort_values(keys).reset_index(drop=True),
        original.sort_values(keys).reset_index(drop=True), check_exact=True)


def freeze_targets(targets, original_path, output_path):
    original = pd.read_parquet(original_path)
    try:
        pd.testing.assert_frame_equal(targets, original, check_exact=True)
    except AssertionError:
        targets.to_parquet(output_path, index=False)
        return False
    os.link(original_path, output_path)
    return True


def prepare(args):
    parent = args.base_prepared.resolve()
    receipt = json.loads((parent / 'inputs.json').read_text())
    for name, digest in receipt['input_sha256'].items():
        if Path(name).name != name or sha(parent / name) != digest:
            raise ValueError('parent input hash mismatch or unsafe filename')
    year = receipt['start'][:4]
    if year not in {'2024', '2025'} or receipt['end'][:4] != year:
        raise ValueError('validation supports the registered annual windows only')
    modes = args.mode
    if not modes or len(set(modes)) != len(modes):
        raise ValueError('explicit unique modes required')
    if year == '2025' and any(mode_flags(m)[2] for m in modes):
        raise ValueError('2025 termination announcement coverage not established')
    output = args.output.resolve()
    if output == parent or output in parent.parents or parent in output.parents:
        raise ValueError('new preparation must not overlap parent')
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('validation preparation needs a new output root')
    protocol = json.loads(args.protocol.read_text())
    if protocol.get('schema') != 'execution-validation-protocol.v1':
        raise ValueError('unsupported experiment protocol')
    current_path = args.data_root / 'metadata/current_assets/a_share_current.json'
    current = json.loads(current_path.read_text())
    def asset(name):
        return Path(current['assets'][name]['resolved_path']).resolve()
    source_paths = {'daily': asset('daily_clean') / 'manifest.yml',
                    'namechange': asset('namechange'), 'instruments': asset('instruments'),
                    'trade_cal': asset('trade_cal')}
    current_hashes = {key: sha(path) for key, path in source_paths.items()}
    changed = [key for key, digest in current_hashes.items()
               if digest != receipt['source_manifest_sha256'][key]]
    if changed and not (year == '2025' and args.allow_daily_manifest_revision and changed == ['daily']):
        raise ValueError('source leaves changed outside declared daily-manifest lineage treatment')
    if 'full-selection-panel.parquet' in receipt['input_sha256']:
        full = pd.read_parquet(parent / 'full-selection-panel.parquet')
    else:
        full = load_clean_panel(asset('daily_clean'), asset('instruments'),
                                receipt['start'], receipt['end'])
    symbols = set(json.loads((parent / 'symbols.json').read_text()))
    verify_selected_panel(full, pd.read_parquet(parent / 'daily-panel.parquet'), symbols)
    names = pd.read_parquet(source_paths['namechange'])
    calendar = pd.read_parquet(source_paths['trade_cal'])
    sessions = sorted(calendar.loc[calendar.exchange.eq('SSE') & calendar.is_open.eq(1)
                      & calendar.cal_date.astype(str).between(receipt['start'], receipt['end']),
                      'cal_date'].astype(str).unique())
    if sessions != sorted(full.trade_date.astype(str).unique()):
        raise ValueError('full selection panel calendar differs')
    baseline = build_targets(full, count=receipt['count'], namechange=names)
    baseline['entry_time'] += pd.Timedelta(minutes=1)
    pd.testing.assert_frame_equal(baseline, pd.read_parquet(parent / 'targets-daily.parquet'),
                                  check_exact=True)
    events, source_audit, valuation_rows = None, None, None
    if year == '2024':
        if args.source_packet is None:
            raise ValueError('2024 requires the common termination valuation source')
        events, source_audit = load_risk_events(args.source_packet, sessions,
            expected_symbols={'600321.SH', '002621.SZ', '000982.SZ', '600836.SH'})
        valuation_rows = [dict(event_id=f'termination_decision_full_impairment:{row.event_id}',
            symbol=row.symbol, effective_time=row.available_time, available_time=row.available_time,
            value_per_share=0., basis='declared_full_impairment_hypothesis',
            source=f'packet_sha256:{source_audit["packet_sha256"]}') for row in events.itertuples(index=False)]
    elif args.source_packet is not None:
        raise ValueError('2025 must not use the 2024 announcement packet')
    spec = importlib.util.spec_from_file_location('validation_runner',
        Path(__file__).with_name('run_execution_validation_suite.py'))
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    implementation = runner.implementation_hashes()
    profiles = [p for p in protocol['profiles'] if p['scenario'] in args.profile]
    if len(profiles) != len(set(args.profile)) or not profiles:
        raise ValueError('profiles must match the frozen protocol')
    runner.validate_profiles(profiles)
    output.mkdir(parents=True, exist_ok=True)
    for mode in modes:
        target, selection = build_risk_targets(full, count=receipt['count'], namechange=names,
            risk_events=events, guard_price=mode_flags(mode)[0],
            guard_st_availability=mode_flags(mode)[1], guard_termination=mode_flags(mode)[2])
        target['entry_time'] += pd.Timedelta(minutes=1)
        if set(target.symbol) - symbols:
            raise ValueError('new selected symbols need additional execution evidence')
        path = output / mode
        path.mkdir()
        for filename in receipt['input_sha256']:
            if filename not in {'targets-daily.parquet', 'full-selection-panel.parquet'}:
                os.link(parent / filename, path / filename)
        identical = freeze_targets(target, parent / 'targets-daily.parquet', path / 'targets-daily.parquet')
        full_path = path / 'full-selection-panel.parquet'
        if 'full-selection-panel.parquet' in receipt['input_sha256']:
            os.link(parent / full_path.name, full_path)
        elif mode == modes[0]:
            full.to_parquet(full_path, index=False)
        else:
            os.link(output / modes[0] / full_path.name, full_path)
        os.link(args.protocol.resolve(), path / 'protocol.json')
        write_json(path / 'session-dates.json', sessions)
        fresh = copy.deepcopy(receipt)
        fresh.pop('risk_comparison', None)
        fresh['variants'] = {'daily': dict(rebalance_sessions=1, buffer_multiple=1,
                                          targets=len(target), symbols=target.symbol.nunique())}
        fresh['experiment_study'] = dict(
            schema='execution-validation-study.v1', year=year, mode=mode,
            protocol_profile=protocol['schema'],
            authorized_profiles=profiles, protocol_sha256=sha(args.protocol),
            implementation_sha256=implementation, preparation_sha256=sha(Path(__file__)),
            valuation_events=valuation_rows, selection_audit=selection,
            termination_announcement_coverage='selected_2024_subset' if events is not None else 'not_tested',
            valuation_source_packet_path=str(args.source_packet.resolve()) if events is not None else None,
            valuation_source_packet_sha256=source_audit['packet_sha256'] if events is not None else None,
            source_audit=source_audit, selected_symbols=sorted(target.symbol.unique()),
            target_exact_parent=identical, parent_path=str(parent),
            parent_receipt_sha256=sha(parent / 'inputs.json'), parent_input_sha256=receipt['input_sha256'],
            source_refs=[dict(name=key, path=str(value), sha256=current_hashes[key])
                         for key, value in source_paths.items()],
            source_manifest_changes=changed, selected_panel_exact_parent=True,
            original_full_universe_archived=False, revision_safe=False,
            validation_kind='development' if year == '2024' else 'retrospective_cross_year_not_unseen_OOS')
        fresh['input_sha256'] = {p.name: sha(p) for p in path.iterdir()
                                if p.suffix in {'.json', '.parquet'}}
        write_json(path / 'inputs.json', fresh)
        print(year, mode, 'targets', len(target), 'symbols', target.symbol.nunique(),
              'exact_parent', identical, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('data-root', 'base-prepared', 'output', 'protocol'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source-packet', type=Path)
    parser.add_argument('--mode', action='append', choices=sorted(MODES), required=True)
    parser.add_argument('--profile', action='append', required=True)
    parser.add_argument('--allow-daily-manifest-revision', action='store_true')
    prepare(parser.parse_args())


if __name__ == '__main__':
    main()
