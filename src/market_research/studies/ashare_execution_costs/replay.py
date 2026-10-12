"""Study-specific snapshot counterfactual; no event semantics or impact inferred."""
from __future__ import annotations

import importlib.metadata
import importlib.util
import sys
import types
from pathlib import Path
import math


def provider_book():
    """Load the installed provider without ticknet's unrelated torch training imports."""
    name = '_execution_audit_provider'
    if name not in sys.modules:
        root = Path(importlib.metadata.distribution('quant-platform').locate_file(
            'ticknet/simulator'))
        package = types.ModuleType(name)
        package.__path__ = [str(root)]
        sys.modules[name] = package
    module_name = name + '.matching'
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            module_name, Path(sys.modules[name].__path__[0]) / 'matching.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return sys.modules[module_name].LimitOrderBook()


def replay_gate(*, semantics_verified, exchange_order_verified):
    reasons = []
    if not semantics_verified:
        reasons.append('vendor order-type, side and cancellation meanings unverified')
    if not exchange_order_verified:
        reasons.append('cross-stream exchange order unverified')
    return {'full_book_replay': 'blocked' if reasons else 'eligible',
            'snapshot_reconciliation': 'not_run', 'reasons': reasons,
            'causal_impact': 'not_identified', 'actual_slippage': 'not_measured'}


def snapshot_path(frame, *, quantity, budget_cny, mode, side, horizon_ms=300000, interval_ms=60000):
    """Refresh displayed depth once per clock, independent of our counterfactual fills.

    Fixed quantity, schedule and limit use no future features. Future quotes become
    execution outcomes only at their own clock. No passive fill is established.
    """
    if mode not in ('market', 'twap', 'limit_wait') or side not in ('buy', 'sell'):
        raise ValueError('unsupported execution mode or side')
    if quantity <= 0 or int(quantity) != quantity or budget_cny < 0:
        raise ValueError('positive integer quantity and nonnegative cash required')
    path = frame.sort_values('time_ms', kind='stable').drop_duplicates('time_ms', keep='first')
    if path.empty:
        raise ValueError('empty quote path')
    if horizon_ms <= 0 or interval_ms <= 0:
        raise ValueError('positive schedule durations required')
    start_ms = int(path.iloc[0].time_ms)
    path = path[path.time_ms <= start_ms + horizon_ms]
    slices = math.ceil(horizon_ms / interval_ms)
    first = path.iloc[0]
    limit = int(first['BidPrice1'] if side == 'buy' else first['AskPrice1'])
    if mode == 'market':
        path = path.iloc[:1]
    remaining, cash = int(quantity), 0.0
    fills = []
    prefix, sign = ('Ask', 1) if side == 'buy' else ('Bid', -1)
    cumulative_target = 0
    for _, row in path.iterrows():
        released = min(slices, 1 + (int(row.time_ms) - start_ms) // interval_ms)
        cumulative_target = (math.ceil(quantity * released / slices)
                             if mode == 'twap' else quantity)
        child = min(remaining, cumulative_target - (quantity - remaining))
        for level in range(1, 11):
            p = row.get(f'{prefix}Price{level}', 0)
            q = row.get(f'{prefix}Volume{level}', 0)
            if not math.isfinite(p) or not math.isfinite(q) or p <= 0 or q <= 0:
                continue
            if int(p) != p or int(q) != q:
                raise ValueError('integer cents and shares required')
            if mode == 'limit_wait' and (p > limit if side == 'buy' else p < limit):
                continue
            take = min(child, int(q))
            if side == 'buy':
                take = min(take, max(0, math.floor((budget_cny - cash + 1e-9) * 100 / p)))
            if not take:
                continue
            # One level per provider call: provider aggregates multi-level fills
            # at final price; splitting preserves exact money accounting.
            book = provider_book()
            book.seed_level(-sign, int(p), int(q), 'DISPLAY')
            trade = book.apply_order('CHILD', sign, int(p), take)
            if trade is None or trade.volume != take:
                raise RuntimeError('provider matching failed conservation')
            amount = trade.price * trade.volume / 100
            cash += amount
            remaining -= take
            child -= take
            fills.append({'time_ms': int(row.time_ms), 'price_cent': trade.price,
                          'quantity': take, 'cash_cny': amount})
    return {'mode': mode, 'side': side, 'requested_quantity': quantity,
            'filled_quantity': quantity - remaining, 'remaining_quantity': remaining,
            'cash_cny': cash, 'instants': len(path), 'fills': fills,
            'optimistic_passive_quantity_upper_bound': quantity if mode == 'limit_wait' else None,
            'passive_bound_cash': 'not_identified' if mode == 'limit_wait' else None,
            'limit_cent': limit if mode == 'limit_wait' else None}
