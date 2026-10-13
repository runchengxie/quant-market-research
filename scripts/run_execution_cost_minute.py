"""Prepare and run bounded public small-cap minute execution comparisons."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import inspect
import json
from pathlib import Path
import uuid

import duckdb
import pandas as pd

from market_research.microcap_execution import load_clean_panel
from market_research.studies.ashare_execution_costs.minute import (
    add_suspension_marks, apply_dividend_overrides, assert_unowned_events, audit_adjustment_events,
    build_targets, measure_arrival_shortfall, normalize_dividends, prepare_minute_bars,
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as file:
        for part in iter(lambda: file.read(8 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def prepare(args):
    output = args.output
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('prepare output must be new or empty')
    output.mkdir(parents=True, exist_ok=True)
    current_path = args.data_root / 'metadata/current_assets/a_share_current.json'
    current = json.loads(current_path.read_text())
    def asset(key):
        return Path(current['assets'][key]['resolved_path'])
    daily_asset, instruments = asset('daily_clean'), asset('instruments')
    panel = load_clean_panel(daily_asset, instruments, args.start, args.end)
    names = pd.read_parquet(asset('namechange'))
    variants = {}
    symbols = set()
    for key, sessions, buffer in [('daily', 1, 1), ('weekly', 5, 1), ('buffer', 5, 2)]:
        targets = build_targets(panel, count=args.count, rebalance_sessions=sessions,
                                buffer_multiple=buffer, namechange=names)
        # The first native minute may include auction information. Wait for its
        # conservative availability before sizing at 09:32.
        targets['entry_time'] += pd.Timedelta(minutes=1)
        targets.to_parquet(output / f'targets-{key}.parquet', index=False)
        variants[key] = {'rebalance_sessions': sessions, 'buffer_multiple': buffer,
                         'targets': len(targets), 'symbols': targets.symbol.nunique()}
        symbols.update(targets.symbol)
    write_json(output / 'symbols.json', sorted(symbols))
    coverage = json.loads(args.dividend_coverage.read_text())
    covered = {symbol for symbol, row in coverage['unit_evidence'].items()
               if row.get('status') == 'completed'}
    if sha(args.dividends) != coverage['source_sha256']:
        raise ValueError('dividend coverage source hash mismatch')
    if symbols - covered:
        raise ValueError('selected dividend histories have incomplete download coverage')
    print('targets prepared', len(symbols), flush=True)
    selected = pd.DataFrame({'ts_code': sorted(symbols)})
    days = sorted(panel.trade_date.astype(str).unique())
    calendar = pd.read_parquet(asset('trade_cal'))
    expected_days = sorted(calendar.loc[calendar.exchange.eq('SSE') & calendar.is_open.eq(1)
                                        & calendar.cal_date.astype(str).between(args.start, args.end),
                                        'cal_date'].astype(str).unique())
    if days != expected_days:
        raise ValueError('daily panel does not cover the authoritative trading calendar')
    minute_root = asset('minute_1m_tushare')
    files = [p for day in days for p in sorted((minute_root / f'trade_date={day}').glob('*.parquet'))]
    missing_days = [day for day in days if not (minute_root / f'trade_date={day}').is_dir()]
    if missing_days:
        write_json(output / 'blocked.json', {'reason': 'missing_minute_partitions', 'days': missing_days})
        raise ValueError('missing minute partitions: cannot claim a continuous backtest')
    con = duckdb.connect()
    con.execute("SET memory_limit='2GB'")
    con.execute('SET threads=2')
    con.register('selected', selected)
    base = None
    if args.base_prepared:
        base = json.loads((args.base_prepared / 'inputs.json').read_text())
        if (base['start'], base['end'], base['count']) != (days[0], days[-1], args.count):
            raise ValueError('cached input window or selection differs')
        for name, digest in base['input_sha256'].items():
            if sha(args.base_prepared / name) != digest:
                raise ValueError('cached input hash mismatch')
        for key, path in [('current', current_path), ('daily', daily_asset / 'manifest.yml'),
                           ('minute', minute_root / '_operational_receipt.json'),
                           ('namechange', asset('namechange'))]:
            if sha(path) != base['source_manifest_sha256'][key]:
                raise ValueError('cached source manifest differs')
    try:
        marks = con.execute('''SELECT d.ts_code,d.trade_date,d.close,d.up_limit,d.down_limit,d.is_suspended,d.adj_factor
                               FROM read_parquet(?) d JOIN selected s USING(ts_code)
                               WHERE trade_date BETWEEN ? AND ?''',
                            [str(daily_asset / 'data/*.parquet'), args.start, args.end]).df()
        if base is None:
            raw = con.execute('''SELECT d.* FROM read_parquet(?) d JOIN selected s USING(ts_code)''',
                              [[str(p) for p in files]]).df()
    finally:
        con.close()
    if base is not None:
        bars = pd.read_parquet(args.base_prepared / 'bars.parquet')
        bar_audit = base['bar_audit']
        if set(bars.symbol.unique()) != symbols:
            raise ValueError('cached bars do not match selected symbols')
        bar_audit['reused_validated_bars_sha256'] = sha(args.base_prepared / 'bars.parquet')
    else:
        bars, bar_audit = prepare_minute_bars(raw, marks)
        terminal = raw.loc[pd.to_datetime(raw.trade_time).dt.strftime('%H:%M').eq('15:00')].copy()
        terminal['trade_date'] = pd.to_datetime(terminal.trade_time).dt.strftime('%Y%m%d')
        expected = marks.loc[marks.is_suspended.eq(False), ['ts_code', 'trade_date']]
        terminal_missing = expected.merge(terminal[['ts_code', 'trade_date']], how='left',
                                          on=['ts_code', 'trade_date'], indicator=True)
        terminal_missing = terminal_missing.loc[terminal_missing._merge.eq('left_only')]
        bar_audit['missing_active_terminal_books'] = len(terminal_missing)
        if len(terminal_missing):
            terminal_missing.to_parquet(output / 'missing-terminal.parquet', index=False)
            raise ValueError('active symbols missing closing minute marks')
        del raw
    panel.loc[panel.ts_code.isin(symbols)].to_parquet(output / 'daily-panel.parquet', index=False)
    dividends = pd.read_parquet(args.dividends)
    overrides = {'overrides': []}
    if args.action_overrides:
        overrides = json.loads(args.action_overrides.read_text())
        if overrides['source_sha256'] != sha(args.dividends):
            raise ValueError('corporate override source hash mismatch')
        # The retained PDFs establish the exact decisions, not just URL labels.
        for row in overrides['overrides']:
            if sha(Path(row['source_pdf_path'])) != row['source_pdf_sha256']:
                raise ValueError('primary announcement hash mismatch')
        dividends = apply_dividend_overrides(dividends, overrides['overrides'])
        write_json(output / 'corporate-action-overrides.json', overrides)
    relevant = dividends.loc[dividends.ts_code.isin(symbols)
                             & dividends.div_proc.str.strip().eq('实施')
                             & dividends.ex_date.astype(str).between(days[0], days[-1])]
    events, blocked = [], []
    for (symbol, ex_day), group in relevant.groupby(['ts_code', 'ex_date']):
        try:
            normalized, _ = normalize_dividends(group, {symbol}, start=days[0], end=days[-1])
            events.extend(normalized)
        except ValueError as error:
            blocked.append({'symbol': symbol, 'ex_date': ex_day,
                            'record_dates': sorted(group.record_date.dropna().unique().tolist()),
                            'reason': str(error)})
    # Unknown ex dates cannot be omitted by the in-window group filter.
    unknown = dividends.loc[dividends.ts_code.isin(symbols)
                            & dividends.div_proc.str.strip().eq('实施')
                            & dividends.ex_date.isna()
                            & dividends.imp_ann_date.astype(str).between(days[0], days[-1])]
    if len(unknown):
        raise ValueError('unknown implemented ex date')
    explained = {(row['symbol'], row['ex_date']) for row in events + blocked}
    explained.update((row['symbol'], row['ex_date']) for row in overrides['overrides'])
    adjustment_audit = audit_adjustment_events(marks, explained)
    suspensions = pd.read_parquet(args.suspensions)
    bars, suspension_audit = add_suspension_marks(bars, suspensions, days, events)
    bars.to_parquet(output / 'bars.parquet', index=False)
    del bars
    action_audit = {'events': len(events), 'unverified_events': len(blocked),
                    'withholding_rate_assumption': 0., 'pit_class': 'reconstructed_pit',
                    'revision_safe': False}
    write_json(output / 'unverified-corporate-actions.json', blocked)
    write_json(output / 'corporate-actions.json', events)
    receipt = {'schema_version': 'execution-minute-inputs.v1', 'evidence': 'research_input_preparation',
               'start': days[0], 'end': days[-1], 'sessions': len(days), 'count': args.count,
               'variants': variants, 'bar_audit': bar_audit, 'corporate_action_audit': action_audit,
               'adjustment_event_audit': adjustment_audit,
               'suspension_valuation_audit': suspension_audit,
               'source_manifest_sha256': {'current': sha(current_path),
                                          'daily': sha(daily_asset / 'manifest.yml'),
                                          'minute': sha(minute_root / '_operational_receipt.json'),
                                          'namechange': sha(asset('namechange')),
                                          'instruments': sha(instruments),
                                          'trade_cal': sha(asset('trade_cal')),
                                          'suspensions': sha(args.suspensions),
                                          'dividends': sha(args.dividends),
                                          'dividend_coverage': sha(args.dividend_coverage)},
               'input_sha256': {p.name: sha(p) for p in sorted(output.iterdir())
                                if p.suffix in ('.parquet', '.json')},
               'pit_class': 'reconstructed_pit', 'revision_safe': False}
    write_json(output / 'inputs.json', receipt)
    print('minute inputs prepared', receipt['bar_audit'], flush=True)


def scenarios():
    return [
        ('gross_1m', 'daily', 1_000_000, 330, 1, 0., 0.),
        ('fees_1m', 'daily', 1_000_000, 330, 1, 1., 6.),
        ('fees_10m', 'daily', 10_000_000, 330, 1, 1., 6.),
        ('fees_100m', 'daily', 100_000_000, 330, 1, 1., 6.),
        ('fast_10m', 'daily', 10_000_000, 30, 1, 1., 6.),
        ('split_10m', 'daily', 10_000_000, 120, 5, 1., 6.),
        ('weekly_10m', 'weekly', 10_000_000, 330, 1, 1., 6.),
        ('buffer_10m', 'buffer', 10_000_000, 330, 1, 1., 6.),
        ('minimum_1m', 'daily', 1_000_000, 330, 1, 1., 6.),
    ]


def run(args):
    from portfolio_backtester.corporate_actions import CorporateAction
    from portfolio_backtester.minute_execution import MinuteExecutionConfig, simulate_minute_execution

    output = args.output
    inputs = json.loads((output / 'inputs.json').read_text())
    for name, digest in inputs['input_sha256'].items():
        if sha(output / name) != digest:
            raise ValueError('prepared input hash mismatch')
    actions = [CorporateAction(**row) for row in json.loads((output / 'corporate-actions.json').read_text())]
    bars = pd.read_parquet(output / 'bars.parquet')
    summaries = []
    engine_hash = sha(Path(inspect.getfile(simulate_minute_execution)))
    source_hash = sha(Path(__file__))
    implementation_hashes = {
        'engine': engine_hash, 'runner': source_hash,
        'corporate_contract': sha(Path(inspect.getfile(CorporateAction))),
        'research_methods': sha(Path(inspect.getfile(build_targets))),
    }
    for name, variant, capital, minutes, slices, buy, sell in scenarios():
        target = pd.read_parquet(output / f'targets-{variant}.parquet')
        config = MinuteExecutionConfig(initial_cash=capital, participation_rate=.05,
                                       buy_fee_bp=buy, sell_fee_bp=sell, execution_minutes=minutes,
                                       release_slices=slices, sell_tax_bp=5. if sell else 0.,
                                       commission_minimum_cny=5. if name == 'minimum_1m' else 0.)
        final = output / name
        if final.exists():
            receipt = json.loads((final / 'receipt.json').read_text())
            if (receipt['config'] != asdict(config) or receipt['engine_sha256'] != engine_hash
                    or receipt['inputs_sha256'] != sha(output / 'inputs.json')
                    or receipt['runner_sha256'] != source_hash
                    or receipt.get('implementation_sha256') != implementation_hashes):
                raise ValueError('completed scenario provenance differs: use a new run directory')
            for filename, digest in receipt['output_sha256'].items():
                if sha(final / filename) != digest:
                    raise ValueError('completed scenario output hash mismatch')
            summaries.append(receipt['summary'])
            print(name, 'verified existing scenario', flush=True)
            continue
        result = simulate_minute_execution(target, bars, config, corporate_actions=actions)
        private = output / f'.{name}-inprogress-{uuid.uuid4().hex[:8]}'
        private.mkdir(exist_ok=False)
        for field in ('daily', 'orders', 'fills', 'holdings'):
            getattr(result, field).to_parquet(private / f'{field}.parquet', index=False)
        daily = result.daily
        blocked = json.loads((output / 'unverified-corporate-actions.json').read_text())
        unowned = assert_unowned_events(result.holdings,
                                        pd.to_datetime(daily.date).dt.strftime('%Y%m%d').tolist(), blocked)
        filled = result.fills
        if daily.nav.isna().any():
            raise ValueError(f'{name}: missing held-symbol valuation; retain private incomplete run')
        if (daily.cash < -1e-6).any():
            raise ValueError('negative funded cash')
        if not ((daily.nav - daily.cash - daily.positions_value - daily.cash_receivable
                 - daily.stock_receivable_value).abs() < .01).all():
            raise ValueError('NAV accounting mismatch')
        if abs(filled.transaction_cost.sum() - daily.transaction_cost.iloc[-1]) > .01:
            raise ValueError('fee accounting mismatch')
        orders = result.orders
        if (orders.filled_quantity > orders.quantity + 1e-6).any():
            raise ValueError('order quantity mismatch')
        measured, shortfall = measure_arrival_shortfall(orders, filled, bars)
        measured.to_parquet(private / 'shortfall.parquet', index=False)
        executed = float(filled.gross_amount.sum())
        average_nav = float(daily.nav.mean())
        summary = dict(scenario=name, variant=variant, capital_cny=capital,
                       execution_minutes=minutes, release_slices=slices, sessions=len(daily),
                       commission_minimum_cny=config.commission_minimum_cny,
                       terminal_nav=float(daily.nav.iloc[-1] / capital),
                       transaction_cost_cny=float(filled.transaction_cost.sum()),
                       mean_one_way_turnover=executed / average_nav / len(daily) / 2,
                       orders=len(orders), zero_fill_orders=int(orders.filled_quantity.eq(0).sum()),
                       partial_fill_orders=int((orders.filled_quantity.gt(0)
                                                & orders.filled_quantity.lt(orders.quantity)).sum()),
                       filled_orders=int(orders.status.eq('filled').sum()),
                       expired_orders=int(orders.status.eq('expired').sum()),
                       cancelled_orders=int(orders.status.eq('cancelled').sum()),
                       clipped_vwap_bars=result.summary['clipped_vwap_bars'],
                       fractional_position_count=len(result.summary['fractional_positions']),
                       negative_cash_sessions=int(daily.cash.lt(-1e-6).sum()))
        summary['unowned_unverified_events'] = unowned
        summary.update(shortfall)
        summaries.append(summary)
        write_json(private / 'receipt.json', {'config': asdict(config), 'summary': summary,
                   'engine_sha256': engine_hash, 'runner_sha256': source_hash,
                   'inputs_sha256': sha(output / 'inputs.json'),
                   'implementation_sha256': implementation_hashes,
                   'output_sha256': {p.name: sha(p) for p in private.glob('*.parquet')}})
        private.rename(final)
        proposal = {
            'schema_version': 'execution-minute-results.v1',
            'evidence': 'modeled_bar_execution_not_live_capacity', 'published': False,
            'complete': len(summaries) == len(scenarios()), 'expected_scenarios': len(scenarios()),
            'inputs': inputs, 'scenarios': summaries,
            'limits': ['reconstructed_PIT_not_revision_safe', 'bounded_bar_VWAP_not_fill_evidence',
                       'no_queue_or_self_impact', 'fee_rates_are_assumptions',
                       'zero_dividend_withholding', 'wall_clock_execution_windows']}
        write_json(output / 'summary.proposed.json', proposal)
        print(name, 'complete', summary['terminal_nav'], flush=True)
    if len(summaries) != len(scenarios()):
        raise ValueError('incomplete scenario matrix')
    # Also rewrite when every completed scenario was resumed through continue.
    write_json(output / 'summary.proposed.json', {
        'schema_version': 'execution-minute-results.v1',
        'evidence': 'modeled_bar_execution_not_live_capacity', 'published': False,
        'complete': True, 'expected_scenarios': len(scenarios()),
        'inputs': inputs, 'scenarios': summaries,
        'implementation_sha256': implementation_hashes,
        'limits': ['reconstructed_PIT_not_revision_safe', 'bounded_bar_execution_not_fill_evidence',
                   'no_queue_or_self_impact', 'fee_rates_and_parent_minimum_are_assumptions',
                   'zero_dividend_withholding', 'wall_clock_execution_windows',
                   'confirmed_suspensions_use_nontradable_carried_valuation'],
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dividends', type=Path)
    parser.add_argument('--dividend-coverage', type=Path)
    parser.add_argument('--action-overrides', type=Path)
    parser.add_argument('--suspensions', type=Path)
    parser.add_argument('--base-prepared', type=Path)
    parser.add_argument('--start')
    parser.add_argument('--end')
    parser.add_argument('--count', type=int, default=40)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--run-prepared', action='store_true')
    args = parser.parse_args()
    if not args.run_prepared:
        if any(v is None for v in (args.data_root, args.dividends, args.dividend_coverage,
                                   args.suspensions, args.start, args.end)):
            parser.error('preparation needs data root, dividends, start and end')
        prepare(args)
    if not args.prepare_only:
        run(args)


if __name__ == '__main__':
    main()
