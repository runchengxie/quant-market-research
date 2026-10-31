"""Same-date ETF index/NAV/market-price reconciliation; no fee double counting."""

from __future__ import annotations

import numpy as np
import pandas as pd
from .analysis import validate_levels


def etf_gap(frame: pd.DataFrame) -> dict:
    cols = ["index_total", "unit_nav", "adj_nav", "close", "adj_factor"]
    data = validate_levels(frame, cols)
    n = len(data) - 1
    growth = {c: float(data[c].iloc[-1] / data[c].iloc[0]) for c in cols}
    index_growth = growth["index_total"]
    nav_growth = growth["adj_nav"]
    market_growth = growth["close"] * growth["adj_factor"]
    nav_relative = nav_growth / index_growth
    premium_growth = growth["close"] / growth["unit_nav"]
    basis_growth = growth["adj_factor"] / (growth["adj_nav"] / growth["unit_nav"])
    premium = data.close / data.unit_nav - 1
    monthly_tracking = (
        data.adj_nav.pct_change(fill_method=None) - data.index_total.pct_change(fill_method=None)
    ).iloc[1:]

    def cagr(g):
        return float(g ** (12 / n) - 1)

    return {
        "start": data.date.iloc[0].date().isoformat(),
        "end": data.date.iloc[-1].date().isoformat(),
        "months": n,
        "index_total_cagr": cagr(index_growth),
        "nav_cagr": cagr(nav_growth),
        "market_total_proxy_cagr": cagr(market_growth),
        "nav_minus_index_cagr_pp": cagr(nav_growth) - cagr(index_growth),
        "market_minus_index_cagr_pp": cagr(market_growth) - cagr(index_growth),
        "nav_relative_wealth_ratio": nav_relative,
        "premium_wealth_ratio": premium_growth,
        "distribution_basis_wealth_ratio": basis_growth,
        "market_relative_wealth_ratio": market_growth / index_growth,
        "geometric_reconciliation_error": market_growth / index_growth
        - nav_relative * premium_growth * basis_growth,
        "monthly_tracking_error_annualized": float(monthly_tracking.std(ddof=1) * np.sqrt(12))
        if n > 1
        else None,
        "premium_at_start": float(premium.iloc[0]),
        "premium_at_end": float(premium.iloc[-1]),
        "premium_minimum": float(premium.min()),
        "premium_maximum": float(premium.max()),
        "manager_fees_subtracted_again": False,
        "interpretation": "Adjusted NAV and market factors are provider return proxies. Closing NAV is a retrospective valuation, not an executable quote. Costs/taxes/slippage excluded.",
    }
