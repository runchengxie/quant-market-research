"""Fractional total-return product proxies with fully funded transaction costs."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .analysis import _valid


def funded_products(
    levels: pd.DataFrame, weights: list[float], month_ends: set[pd.Timestamp], fee_bps: float = 0
) -> dict:
    """Cash is a reserve asset, not a charged trading leg.

    The first displayed NAV is pre-entry capital. Initial entry, scheduled
    close rebalances and terminal liquidation all pay per-side traded-notional
    fees. Adjusted-price units are fractional proxies, not exchange share lots.
    """
    if "cash" not in levels or len(weights) != len(levels.columns) or len(levels) < 2:
        raise ValueError("cash asset, valid dimensions and two dates required")
    for col in levels:
        _valid(levels[col])
    target = np.asarray(weights, dtype=float)
    if (
        not np.isfinite(target).all()
        or (target < 0).any()
        or not np.isclose(target.sum(), 1)
        or not np.isfinite(fee_bps)
        or not 0 <= fee_bps < 10000
    ):
        raise ValueError("invalid target weights or fee")
    traded_assets = np.array([c != "cash" for c in levels])
    rate = fee_bps / 10000

    def rebalance(holdings):
        wealth = holdings.sum()
        low, high = 0.0, wealth
        for _ in range(60):
            fee = (low + high) / 2
            required = rate * np.abs(target * (wealth - fee) - holdings)[traded_assets].sum()
            if fee > required:
                high = fee
            else:
                low = fee
        fee = (low + high) / 2 if rate else 0.0
        new = target * (wealth - fee)
        turnover = np.abs(new - holdings)[traded_assets].sum()
        return new, float(fee), float(turnover)

    holdings = np.zeros(len(target))
    holdings[levels.columns.get_loc("cash")] = 1
    holdings, opening_fee, turn = rebalance(holdings)
    ledger = [
        {
            "date": str(levels.index[0].date()),
            "fee": opening_fee,
            "two_sided_turnover": turn,
            "wealth": float(holdings.sum()),
            "event": "entry",
        }
    ]
    fees, gross, events = opening_fee, 0.0, 1
    nav = pd.Series(1.0, index=levels.index)
    # Retain post-entry value separately while day-zero NAV remains the initial capital.
    for i in range(1, len(levels)):
        before = holdings.sum()
        holdings *= levels.iloc[i].to_numpy() / levels.iloc[i - 1].to_numpy()
        gross += holdings.sum() - before
        fee, turnover, event = 0.0, 0.0, "mark"
        if i == len(levels) - 1:
            turnover = float(holdings[traded_assets].sum())
            fee = rate * turnover
            marked_wealth = float(holdings.sum())
            holdings[:] = 0
            holdings[levels.columns.get_loc("cash")] = marked_wealth - fee
            event = "exit"
            events += 1
        elif levels.index[i] in month_ends:
            holdings, fee, turnover = rebalance(holdings)
            event = "rebalance"
            events += 1
        fees += fee
        nav.iloc[i] = holdings.sum()
        ledger.append(
            {
                "date": str(levels.index[i].date()),
                "fee": float(fee),
                "two_sided_turnover": turnover,
                "wealth": float(holdings.sum()),
                "event": event,
            }
        )
    return {
        "nav": nav,
        "terminal_wealth": float(nav.iloc[-1]),
        "gross_pnl": float(gross),
        "initial_fee": opening_fee,
        "final_fee": float(ledger[-1]["fee"]),
        "total_fees": float(fees),
        "trade_events": events,
        "ledger": ledger,
    }
