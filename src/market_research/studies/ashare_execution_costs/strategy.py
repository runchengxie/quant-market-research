"""Frozen execution-path accounting sensitivity; never an execution simulator.

Cost replacement changes cash debits only. Holdings, missed fills and their market
P&L stay fixed. Negative counterfactual cash exposes infeasible funding rather
than implicitly borrowing or reoptimizing orders. Capital mapping is proportional
accounting, not a liquidity/capacity estimate. Static book assumptions are borrowed
from another sample and cannot establish net alpha.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _positive(value: float, name: str, *, zero: bool = False) -> None:
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(f"{name} must be finite and {'nonnegative' if zero else 'positive'}")


def _numbers(frame: pd.DataFrame, columns: list[str], *, signed: bool = False) -> None:
    if not set(columns).issubset(frame.columns):
        raise ValueError("missing accounting columns")
    values = frame[columns].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (not signed and (values < 0).any()):
        raise ValueError("invalid accounting values")


def _equal(left, right, message: str) -> None:
    if not np.allclose(left, right, atol=1e-6, rtol=1e-9):
        raise ValueError(message)


def accounting_overlay(
    ledger: pd.DataFrame,
    fills: pd.DataFrame,
    orders: pd.DataFrame,
    performance: pd.DataFrame,
    *,
    initial_capital: float,
    capital: float,
    buy_fee_bp: float = 0.0,
    sell_fee_bp: float = 0.0,
    buy_static_bp: float = 0.0,
    sell_static_bp: float = 0.0,
    original_cost_bp: float = 5.0,
) -> tuple[pd.DataFrame, dict]:
    """Replace reconciled original debits on executed notional, in CNY and bp.

    Fee rates are explicit sensitivity inputs. Flat rates do not model minimum
    commissions, venue-specific rates or fee-order grouping. No cost is charged
    on unfilled notional. Orders provide only unfilled amounts, not reason codes.
    """
    for name, value in [("initial_capital", initial_capital), ("capital", capital)]:
        _positive(value, name)
    for name, value in [
        ("buy_fee_bp", buy_fee_bp),
        ("sell_fee_bp", sell_fee_bp),
        ("buy_static_bp", buy_static_bp),
        ("sell_static_bp", sell_static_bp),
        ("original_cost_bp", original_cost_bp),
    ]:
        _positive(value, name, zero=True)
    _numbers(ledger, ["cash", "positions_value", "nav"], signed=True)
    _numbers(fills, ["filled_notional", "transaction_cost"])
    _numbers(orders, ["requested_notional", "filled_notional", "unfilled_notional"])
    _numbers(performance, ["transaction_cost", "traded_notional"])
    for frame in (fills, orders):
        if not frame.side.isin(["buy", "sell"]).all():
            raise ValueError("invalid side")
    days = ledger.trade_date.astype(str)
    if ledger.empty or days.duplicated().any() or not days.is_monotonic_increasing:
        raise ValueError("daily ledger must have unique ordered sessions")
    if (ledger.nav <= 0).any() or (ledger.positions_value < 0).any():
        raise ValueError("nonpositive NAV or negative positions")
    _equal(ledger.nav, ledger.cash + ledger.positions_value, "NAV does not reconcile")
    _equal(
        orders.requested_notional,
        orders.filled_notional + orders.unfilled_notional,
        "orders do not reconcile",
    )
    _equal(
        fills.transaction_cost,
        fills.filled_notional * original_cost_bp / 10000,
        "original flat simulator cost does not reconcile",
    )
    if not fills.trade_date.astype(str).isin(days).all():
        raise ValueError("fill outside ledger sessions")
    if performance.period_end.astype(str).duplicated().any():
        raise ValueError("duplicate performance sessions")
    perf = performance.assign(period_end=performance.period_end.astype(str)).set_index("period_end")
    if set(perf.index) != set(days):
        raise ValueError("performance sessions do not match")
    flow = fills.assign(trade_date=fills.trade_date.astype(str))
    cost = flow.groupby("trade_date").transaction_cost.sum().reindex(days, fill_value=0.0)
    traded = flow.groupby("trade_date").filled_notional.sum().reindex(days, fill_value=0.0)
    _equal(cost, perf.loc[days].transaction_cost, "daily original cost does not reconcile")
    _equal(traded, perf.loc[days].traded_notional, "daily traded notional does not reconcile")
    for side in ("buy", "sell"):
        _equal(
            flow.loc[flow.side.eq(side)].filled_notional.sum(),
            orders.loc[orders.side.eq(side)].filled_notional.sum(),
            "order/fill totals do not reconcile",
        )
    scale = capital / initial_capital
    daily = pd.DataFrame({"trade_date": days.to_numpy()})
    for side in ("buy", "sell"):
        daily[f"{side}_cny"] = (
            flow.loc[flow.side.eq(side)]
            .groupby("trade_date")
            .filled_notional.sum()
            .reindex(days, fill_value=0.0)
            .to_numpy()
            * scale
        )
    daily["original_cost_cny"] = cost.to_numpy() * scale
    daily["fee_cny"] = (daily.buy_cny * buy_fee_bp + daily.sell_cny * sell_fee_bp) / 10000
    daily["static_cost_cny"] = (
        daily.buy_cny * buy_static_bp + daily.sell_cny * sell_static_bp
    ) / 10000
    gross_value = ledger.nav.to_numpy() * scale + daily.original_cost_cny.cumsum()
    gross_cash = ledger.cash.to_numpy() * scale + daily.original_cost_cny.cumsum()
    daily["source_nav"] = ledger.nav.to_numpy() / initial_capital
    daily["positions_cny"] = ledger.positions_value.to_numpy() * scale
    for scenario, debit in [
        ("gross", 0 * daily.fee_cny),
        ("fee_only", daily.fee_cny),
        ("fee_static", daily.fee_cny + daily.static_cost_cny),
    ]:
        daily[f"{scenario}_nav"] = (gross_value - debit.cumsum()) / capital
        daily[f"{scenario}_cash_cny"] = gross_cash - debit.cumsum()
        if (daily[f"{scenario}_nav"] <= 0).any():
            raise ValueError("cost overlay exhausts NAV")
        nav = daily[f"{scenario}_nav"]
        daily[f"{scenario}_return"] = nav / nav.shift(1, fill_value=1.0) - 1
    previous_nav = ledger.nav.shift(1, fill_value=initial_capital).to_numpy() * scale
    daily["buy_turnover"] = daily.buy_cny / previous_nav
    daily["sell_turnover"] = daily.sell_cny / previous_nav
    daily["one_way_turnover"] = (daily.buy_turnover + daily.sell_turnover) / 2
    summary = {
        "evidence": "diagnostic_frozen_path_accounting_sensitivity",
        "capital_cny": capital,
        "source_initial_capital_cny": initial_capital,
        "sessions": len(daily),
        "capital_mapping": "proportional_frozen_path_not_capacity",
        "original_cost_cny": float(daily.original_cost_cny.sum()),
        "fee_cny": float(daily.fee_cny.sum()),
        "static_cost_cny": float(daily.static_cost_cny.sum()),
        "mean_one_way_turnover": float(daily.one_way_turnover.mean()),
        "max_one_way_turnover": float(daily.one_way_turnover.max()),
    }
    for scenario in ("gross", "fee_only", "fee_static"):
        summary[f"{scenario}_terminal_nav"] = float(daily[f"{scenario}_nav"].iloc[-1])
        summary[f"{scenario}_negative_cash_sessions"] = int(
            (daily[f"{scenario}_cash_cny"] < -1e-6).sum()
        )
        summary[f"{scenario}_max_funding_shortfall_cny"] = float(
            max(0.0, -daily[f"{scenario}_cash_cny"].min())
        )
    for side in ("buy", "sell"):
        summary[f"executed_{side}_cny"] = float(daily[f"{side}_cny"].sum())
        summary[f"unfilled_{side}_cny"] = float(
            orders.loc[orders.side.eq(side)].unfilled_notional.sum() * scale
        )
    return daily, summary


def turnover_stress(
    capital: float, *, sessions: int, one_way_turnover: float, buy_bp: float, sell_bp: float
) -> dict:
    """Cost-only stress: each side trades one_way_turnover of current NAV daily."""
    _positive(capital, "capital")
    for name, value in [
        ("one_way_turnover", one_way_turnover),
        ("buy_bp", buy_bp),
        ("sell_bp", sell_bp),
    ]:
        _positive(value, name, zero=True)
    if not isinstance(sessions, int) or sessions < 1:
        raise ValueError("sessions must be a positive integer")
    fraction = one_way_turnover * (buy_bp + sell_bp) / 10000
    if fraction >= 1:
        raise ValueError("daily stress exhausts NAV")
    return {
        "capital_cny": capital,
        "sessions": sessions,
        "one_way_turnover": one_way_turnover,
        "daily_cost_fraction": fraction,
        "daily_initial_capital_cost_cny": capital * fraction,
        "terminal_cost_only_nav": (1 - fraction) ** sessions,
        "linear_cost_fraction": sessions * fraction,
        "compounded_cost_fraction": 1 - (1 - fraction) ** sessions,
    }


def anchor_exceedance(orders: pd.DataFrame, *, scale: float, reference_notional: float) -> dict:
    """Notional-weighted size mismatch; never an inferred depth-fill probability."""
    _positive(scale, "scale")
    _positive(reference_notional, "reference_notional")
    _numbers(orders, ["requested_notional"])
    result = {"interpretation": "size_comparison_only_not_matched_book_coverage"}
    for side in ("buy", "sell"):
        notionals = orders.loc[orders.side.eq(side)].requested_notional * scale
        total = notionals.sum()
        result[f"{side}_requested_notional_above_anchor_fraction"] = (
            float(notionals.loc[notionals > reference_notional].sum() / total) if total else 0.0
        )
    return result
