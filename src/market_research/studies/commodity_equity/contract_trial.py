"""Bounded individual-contract accounting experiment, not an execution engine."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def settlement_trial(
    frame: pd.DataFrame,
    schedule: list[tuple[pd.Timestamp, str]],
    end: pd.Timestamp,
    *,
    capital: float = 1_000_000,
    per_unit: float = 10,
    slippage_ticks: float = 1,
    tick_size: float = 1,
    margin_buffer: float = 0.05,
) -> dict:
    """Predeclared dated rolls; size using prior-session settlement and equity.

    Mark existing contracts settlement-to-settlement. Entries, rolls and final
    exit use current settlement as a hypothetical fill, plus explicit adverse
    slippage and the recorded per-lot fee. Cash earns zero. Margin is reserved,
    not subtracted a second time from equity. Missing inputs fail closed.
    """
    if (
        not schedule
        or schedule != sorted(schedule)
        or len({d for d, _ in schedule}) != len(schedule)
    ):
        raise ValueError("unique ordered schedule required")
    if (
        not np.isfinite([capital, per_unit, slippage_ticks, tick_size, margin_buffer]).all()
        or min(capital, per_unit, tick_size) <= 0
        or min(slippage_ticks, margin_buffer) < 0
    ):
        raise ValueError("invalid account settings")
    data = frame.copy()
    data["trade_date"] = pd.to_datetime(data.trade_date)
    if data.duplicated(["trade_date", "ts_code"]).any():
        raise ValueError("duplicate contract marks")
    data = data.set_index(["trade_date", "ts_code"]).sort_index()
    dates = data.index.get_level_values(0).unique().sort_values()
    if any(day not in dates for day, _ in schedule) or end not in dates or end <= schedule[-1][0]:
        raise ValueError("invalid trial endpoints")
    changes = dict(schedule)
    equity, lots, held = float(capital), 0, None
    ledger = []

    def row(day, code):
        if (day, code) not in data.index:
            raise ValueError("missing contract mark")
        r = data.loc[(day, code)]
        if (
            not np.isfinite([r.settle, r.trading_fee, r.long_margin_rate, r.vol]).all()
            or r.settle <= 0
            or r.trading_fee < 0
            or r.vol < 0
            or not 0 < r.long_margin_rate <= 1
        ):
            raise ValueError("invalid price, fee or margin")
        return r

    total_pnl = total_fee = total_slip = 0.0
    for i, day in enumerate(dates):
        if day < schedule[0][0] or day > end:
            continue
        if i == 0:
            raise ValueError("prior-session marks required for sizing")
        previous = dates[i - 1]
        before = equity
        pnl = (
            0.0
            if held is None
            else lots * per_unit * (row(day, held).settle - row(previous, held).settle)
        )
        equity += pnl
        target = changes.get(day, held)
        new_lots = lots
        if day in changes:
            prior = row(previous, target)
            new_lots = math.floor(before / (per_unit * prior.settle))
        if day == end:
            target, new_lots = None, 0
        traded = 0
        fee = 0.0
        if target != held:
            for code, count in [(held, lots), (target, new_lots)]:
                if code is not None and count:
                    r = row(day, code)
                    if r.vol <= 0:
                        raise ValueError("no traded volume on hypothetical execution day")
                    fee += count * r.trading_fee
                    traded += count
        else:
            traded = abs(new_lots - lots)
            if traded:
                fee = traded * row(day, held).trading_fee
        slip = traded * per_unit * tick_size * slippage_ticks
        equity -= fee + slip
        held, lots = target, new_lots
        margin = (
            0.0
            if held is None
            else lots
            * per_unit
            * row(day, held).settle
            * (row(day, held).long_margin_rate + margin_buffer)
        )
        if equity <= 0 or margin > equity:
            raise ValueError("insufficient equity for required margin")
        total_pnl += pnl
        total_fee += fee
        total_slip += slip
        ledger.append(
            {
                "date": str(day.date()),
                "contract": held,
                "lots": lots,
                "pnl": float(pnl),
                "fee": float(fee),
                "slippage": float(slip),
                "traded_lots": traded,
                "equity": float(equity),
                "margin": float(margin),
                "free_cash": float(equity - margin),
            }
        )
    return {
        "initial_capital": capital,
        "terminal_equity": equity,
        "total_pnl": float(total_pnl),
        "total_fee": float(total_fee),
        "total_slippage": float(total_slip),
        "max_margin_fraction": max(r["margin"] / r["equity"] for r in ledger),
        "ledger": ledger,
    }
