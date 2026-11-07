"""Third exploration on frozen owner inputs; only derived summaries are public."""
from __future__ import annotations

import argparse
import hashlib
import json
import io
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd

from .analysis import summarize
from .contract_trial import settlement_trial
from .followup_inputs import read_exports
from .followup_run import _endpoints, _metrics
from .inputs import _read_hashed, audit_pair, read_bundle
from .risk_controls import lagged_risk_control
from .robustness import index_account


def run_next(manifest_path: Path, output: Path) -> dict:
    output = output.resolve()
    if any((p / '.git').exists() for p in [output, *output.parents] if p not in {Path.home(), Path(gettempdir())}):
        raise ValueError('outputs must remain outside repositories')
    if output.exists():
        raise FileExistsError('select a new output directory')
    manifest = json.loads(manifest_path.read_text())
    baseline = Path(manifest['baseline_manifest_path'])
    _read_hashed(baseline, manifest['baseline_manifest_sha256'])
    series, calendars, _ = read_bundle(baseline)
    audit, levels = audit_pair(series['H00300.CSI'], series['NHCI.NH'], calendars['SSE'], calendars['SHFE'], pd.Timestamp('2006-12-29'), pd.Timestamp('2025-12-31'))
    if not audit['eligible']:
        raise ValueError('baseline calendar audit failed')
    endpoints = _endpoints(calendars['SSE'].intersection(calendars['SHFE']), levels)
    risk = lagged_risk_control(levels, endpoints)
    sub = levels.loc[risk['nav'].index]
    cash = sub.assign(commodity=1.0)
    mix = index_account(sub, .2, 'monthly', set(endpoints))['nav']
    stock = sub.equity / sub.equity.iloc[0]
    control = index_account(cash, .2, 'monthly', set(endpoints))['nav']
    ratio = min(1, mix.pct_change().std() / stock.pct_change().std())
    hindsight = index_account(cash, 1 - ratio, 'monthly', set(endpoints))['nav']
    accounts = {'equity': stock, 'commodity_20': mix, 'cash_20': control, 'lagged_risk_cash': risk['nav'], 'hindsight_vol_cash': hindsight}
    risk_result = {'lookback_sessions': 756, 'cash_yield': 0, 'fees': 0, 'hindsight_is_descriptive_only': True, 'hindsight_equity_weight': float(ratio), 'decision_equity_weight_range': [float(risk['decision_weights'].min()), float(risk['decision_weights'].max())], 'decision_count': len(risk['decision_weights']), 'cases': {k: _metrics(v) for k, v in accounts.items()}, 'realized_volatility_matching_error': float(risk['nav'].pct_change().std() / mix.pct_change().std() - 1)}
    exports, receipts = read_exports(manifest['exports'])
    basic = exports[('fut_basic', None)]
    parts = []
    for code in ['M2505.DCE', 'M2509.DCE', 'M2601.DCE']:
        b = basic.loc[basic.ts_code == code]
        if len(b) != 1 or b.iloc[0].per_unit != 10 or b.iloc[0].fut_code != 'M':
            raise ValueError('contract identity or trading unit mismatch')
        daily, params = exports[('fut_daily', code)], exports[('fut_settle', code)]
        if len(daily) >= 2000 or len(params) >= 1600:
            raise ValueError('possibly capped contract input')
        merged = daily.merge(params, on=['ts_code', 'trade_date'], validate='one_to_one', suffixes=('', '_parameter'))
        if not np.allclose(merged.settle, merged.settle_parameter):
            raise ValueError('settlement sources disagree')
        if merged.trading_fee_rate.fillna(0).ne(0).any():
            raise ValueError('percentage fee units not admitted')
        merged['trade_date'] = pd.to_datetime(merged.trade_date, format='%Y%m%d')
        parts.append(merged)
    frame = pd.concat(parts, ignore_index=True)
    calendar = exports[('trade_cal', None)]
    if not calendar.exchange.eq('DCE').all() or not calendar.is_open.astype(int).eq(1).all():
        raise ValueError('invalid DCE calendar')
    expected = pd.DatetimeIndex(pd.to_datetime(calendar.cal_date, format='%Y%m%d')).sort_values()
    reference = calendars['SHFE'][(calendars['SHFE'] >= pd.Timestamp('2024-12-01')) & (calendars['SHFE'] <= pd.Timestamp('2025-12-31'))]
    if expected.has_duplicates or expected.hasnans or not expected.equals(reference):
        raise ValueError('DCE calendar missing, duplicate or inconsistent sessions')
    if len(pd.DatetimeIndex(frame.trade_date.unique()).difference(expected)):
        raise ValueError('off-calendar contract marks')
    schedule = [(pd.Timestamp('2024-12-31'), 'M2505.DCE'), (pd.Timestamp('2025-04-01'), 'M2509.DCE'), (pd.Timestamp('2025-08-01'), 'M2601.DCE')]
    end = pd.Timestamp('2025-12-31')
    if any(d not in expected for d, _ in schedule) or end not in expected:
        raise ValueError('scheduled contract date absent from DCE calendar')
    for i, (start, code) in enumerate(schedule):
        finish = schedule[i + 1][0] if i + 1 < len(schedule) else end
        needed = expected[(expected >= start) & (expected <= finish)]
        if len(needed.difference(frame.loc[frame.ts_code == code, 'trade_date'])):
            raise ValueError('held contract has missing DCE sessions')
    results, ledgers = [], {}
    for slip in [0, 1, 2]:
        result = settlement_trial(frame, schedule, end, slippage_ticks=slip)
        ledger = result.pop('ledger')
        # Include pre-entry capital so initial fees and slippage enter the return.
        dates = pd.to_datetime([expected[expected < schedule[0][0]][-1], *[r['date'] for r in ledger]])
        nav = pd.Series([1.0, *[r['equity'] / result['initial_capital'] for r in ledger]], index=dates)
        ledgers[str(slip)] = ledger
        results.append({'slippage_ticks_per_traded_lot': slip, **result, 'return_from_pre_entry_capital': result['terminal_equity'] / result['initial_capital'] - 1, 'daily_max_drawdown_including_entry': summarize(nav)['max_drawdown'], 'traded_lots': sum(r['traded_lots'] for r in ledger)})
    m = exports[('fut_index_daily', 'M.NH')]
    m = m.set_index('trade_date').close
    comparison = float(m.loc['20251231'] / m.loc['20241231'] - 1)
    capture_path = Path(manifest['capture_path'])
    capture = json.loads(_read_hashed(capture_path, manifest['capture_sha256']))
    public_capture = []
    for item in capture['snapshots']:
        path = Path(item['path'])
        receipt = json.loads(_read_hashed(path / 'receipt.json', item['receipt_sha256']))
        raw = _read_hashed(path / 'raw.bin', receipt['sha256'])
        seal = json.loads((path / 'manifest.seal.json').read_text())
        if seal['files']['raw.bin'] != hashlib.sha256(raw).hexdigest() or seal['files']['receipt.json'] != item['receipt_sha256']:
            raise ValueError('macro seal mismatch')
        snapshot_frame = pd.read_csv(io.BytesIO(raw), dtype={'month': str})
        derived = {'dataset': receipt['dataset'], 'rows': len(snapshot_frame), 'periods': sorted(snapshot_frame.month.unique().tolist()), 'retrieved_at': receipt['retrieved_at'], 'raw_sha256': receipt['sha256'], 'receipt_sha256': item['receipt_sha256']}
        if any(item[k] != v for k, v in derived.items()):
            raise ValueError('macro capture index contradicts verified snapshot')
        public_capture.append(derived)
    result = {'schema_version': 1, 'study_id': 'china_commodity_equity', 'phase': 'risk_contract_prospective_exploration', 'source_revision': manifest['source_revision'], 'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(), 'code_sha256': {n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest() for n in ['next_run.py', 'risk_controls.py', 'contract_trial.py']}, 'risk_controls': risk_result, 'contract_trial': {'start': '2024-12-31', 'end': '2025-12-31', 'variety': 'DCE soymeal', 'unit_tonnes_per_lot': 10, 'initial_capital_CNY': 1000000, 'schedule': [{'date': str(d.date()), 'contract': c} for d, c in schedule], 'margin_buffer_percentage_points': 5, 'cash_yield': 0, 'calendar_verified': True, 'exchange_fee_per_lot_CNY': sorted(frame.trading_fee.unique().tolist()), 'cases': results, 'nanhua_soymeal_index_return_same_calendar_year': comparison, 'execution_established': False}, 'prospective_archive': {'snapshots': public_capture, 'forward_outcomes': 0, 'historical_vintages_certified': False, 'recurring_job_installed': False}, 'source_requests': len(receipts)}
    output.mkdir(parents=True)
    (output / 'reviewed-candidate.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    (output / 'private-ledgers.json').write_text(json.dumps({'contracts': ledgers, 'risk_decisions': {str(d.date()): float(w) for d, w in risk['decision_weights'].items()}}, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run_next(args.manifest, args.output)


if __name__ == '__main__':
    main()
