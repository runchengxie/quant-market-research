"""Cash and fund diagnostics with explicit proxy/benchmark boundaries."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .analysis import _valid


def collateral_levels(
    commodity: pd.Series, rates: pd.Series, fraction: float, already_includes_cash: bool = False
) -> pd.Series:
    if already_includes_cash:
        raise ValueError("cash is already included in these levels")
    _valid(commodity)
    if not np.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError("cash-rate fraction must be between zero and one")
    if (
        rates.index.has_duplicates
        or not rates.index.is_monotonic_increasing
        or not np.isfinite(rates).all()
    ):
        raise ValueError("ordered unique finite cash rates required")
    starts = commodity.index[:-1]
    selected = rates.reindex(starts, method="ffill")
    if selected.isna().any():
        raise ValueError("no prior available cash rate")
    rate_dates = pd.Series(rates.index, index=rates.index).reindex(starts, method="ffill")
    if ((starts - pd.DatetimeIndex(rate_dates)).days > 14).any():
        raise ValueError("stale cash rate")
    days = np.diff(commodity.index.values).astype("timedelta64[D]").astype(int)
    price_returns = commodity.to_numpy()[1:] / commodity.to_numpy()[:-1] - 1
    cash_returns = selected.to_numpy() / 100 * days / 365 * fraction
    growth = 1 + price_returns + cash_returns
    if (growth <= 0).any():
        raise ValueError("nonpositive sleeve wealth")
    return pd.Series(np.r_[1.0, np.cumprod(growth)] * commodity.iloc[0], index=commodity.index)


def fund_comparison(
    levels: pd.DataFrame, name: str, issuer_benchmark: str, reference_benchmark: str
) -> dict:
    for col in ["close", "adj_factor", "unit_nav", "adj_nav"]:
        _valid(levels[col])
    growth = {c: float(levels[c].iloc[-1] / levels[c].iloc[0]) for c in levels}
    years = (levels.index[-1] - levels.index[0]).days / 365.25
    market = growth["close"] * growth["adj_factor"]
    nav = growth["adj_nav"]
    same = issuer_benchmark == reference_benchmark
    tracking = None
    if same and "benchmark" in levels:
        difference = levels.adj_nav.pct_change(fill_method=None) - levels.benchmark.pct_change(
            fill_method=None
        )
        tracking = float(difference.iloc[1:].std(ddof=1) * np.sqrt(252))
    premium = levels.close / levels.unit_nav - 1
    return {
        "name": name,
        "issuer_benchmark": issuer_benchmark,
        "reference_benchmark": reference_benchmark,
        "same_benchmark": same,
        "tracking_error": tracking,
        "manager_fees_subtracted_again": False,
        "start": str(levels.index[0].date()),
        "end": str(levels.index[-1].date()),
        "observations": len(levels),
        "market_total_return_proxy": market - 1,
        "adjusted_nav_return_proxy": nav - 1,
        "market_cagr_proxy": market ** (1 / years) - 1,
        "adjusted_nav_cagr_proxy": nav ** (1 / years) - 1,
        "premium_start": float(premium.iloc[0]),
        "premium_end": float(premium.iloc[-1]),
        "premium_min": float(premium.min()),
        "premium_max": float(premium.max()),
        "market_nav_relative_wealth": market / nav,
        "fees_taxes_slippage_in_market_proxy": False,
        "nav_is_retrospective_valuation_not_executable_price": True,
    }
