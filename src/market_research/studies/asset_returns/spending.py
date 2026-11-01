"""Finite real-spending scenarios, with explicitly funded zero-interest cash."""

from __future__ import annotations

import numpy as np


def spending_path(
    returns, cpi, *, annual_real=4.0, buffer_months=0, shock_month=None, shock_real=0.0
) -> dict:
    r, inflation = np.asarray(returns, dtype=float), np.asarray(cpi, dtype=float)
    if (
        r.ndim != 1
        or len(r) < 1
        or inflation.shape != (len(r) + 1,)
        or not np.isfinite(r).all()
        or (r < -1).any()
        or not np.isfinite(inflation).all()
        or (inflation <= 0).any()
        or not np.isfinite([annual_real, shock_real]).all()
        or min(annual_real, shock_real) < 0
        or type(buffer_months) is not int
        or buffer_months < 0
        or (
            shock_month is not None
            and (type(shock_month) is not int or not 1 <= shock_month <= len(r))
        )
    ):
        raise ValueError("invalid spending inputs")
    initial_cash = annual_real / 12 * buffer_months
    if initial_cash > 100:
        raise ValueError("cash buffer must be funded by initial capital")
    cash, risky = initial_cash, 100 - initial_cash
    first_shortfall = None
    real_paid = real_unmet = sales = drawdown_sales = 0.0
    risky_index = peak = 1.0
    for i, ret in enumerate(r, start=1):
        risky *= 1 + ret
        risky_index *= 1 + ret
        peak = max(peak, risky_index)
        scale = inflation[i] / inflation[0]
        demand = (annual_real / 12 + (shock_real if i == shock_month else 0)) * scale
        from_cash = min(cash, demand)
        cash -= from_cash
        from_risky = min(risky, max(0.0, demand - from_cash))
        risky -= from_risky
        paid = from_cash + from_risky
        unmet = max(0.0, demand - paid)
        sales += from_risky
        if risky_index < peak - 1e-12:
            drawdown_sales += from_risky / scale
        if unmet > 1e-10 and first_shortfall is None:
            first_shortfall = i
        real_paid += paid / scale
        real_unmet += unmet / scale
    return {
        "initial_cash": initial_cash,
        "initial_risky": 100 - initial_cash,
        "terminal_real_capital": (cash + risky) / (inflation[-1] / inflation[0]),
        "first_shortfall_month": first_shortfall,
        "real_paid": real_paid,
        "real_unmet": real_unmet,
        "risky_sales_nominal": sales,
        "drawdown_real_sales": drawdown_sales,
    }


def summarize_spending(paths: list[dict]) -> dict:
    if not paths:
        return {"completed_windows": 0, "shortfall_fraction": None}
    capital = [p["terminal_real_capital"] for p in paths]
    shortfalls = [
        p["first_shortfall_month"] for p in paths if p["first_shortfall_month"] is not None
    ]
    return {
        "completed_windows": len(paths),
        "shortfall_fraction": len(shortfalls) / len(paths),
        "earliest_shortfall_month": min(shortfalls) if shortfalls else None,
        "median_terminal_real_capital": float(np.median(capital)),
        "minimum_terminal_real_capital": float(min(capital)),
        "drawdown_sale_window_fraction": sum(p["drawdown_real_sales"] > 1e-10 for p in paths)
        / len(paths),
        "median_drawdown_real_sales": float(np.median([p["drawdown_real_sales"] for p in paths])),
        "maximum_real_unmet": float(max(p["real_unmet"] for p in paths)),
    }
