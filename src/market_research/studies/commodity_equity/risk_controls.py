"""Cash controls with monthly decisions based solely on completed daily history."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .analysis import _valid


def lagged_risk_control(
    levels: pd.DataFrame, endpoints: pd.DatetimeIndex, lookback: int = 756
) -> dict:
    """Match trailing daily-rebalanced 80/20 model volatility with stock/cash.

    Zero cash yield for every comparison. Estimate at a completed month-end;
    trade at that closing mark (idealized) and hold for subsequent returns.
    No leverage and no claim that realized future risk is exactly matched.
    """
    for col in ["equity", "commodity"]:
        _valid(levels[col])
    if lookback < 2:
        raise ValueError("at least two past returns required")
    returns = levels[["equity", "commodity"]].pct_change()
    model = 0.8 * returns.equity + 0.2 * returns.commodity
    ratios = (model.rolling(lookback).std() / returns.equity.rolling(lookback).std()).clip(0, 1)
    decisions = ratios.reindex(endpoints.intersection(levels.index)).dropna()
    if decisions.empty or not np.isfinite(decisions).all():
        raise ValueError("insufficient finite risk-estimation history")
    dates = levels.loc[decisions.index[0] :].index
    # Each decision affects only subsequent returns; today's return used yesterday's holding.
    weights = decisions.reindex(dates).ffill()
    nav = pd.Series(1.0, index=dates)
    holdings = np.array([weights.iloc[0], 1 - weights.iloc[0]])
    for i in range(1, len(dates)):
        holdings[0] *= levels.equity.loc[dates[i]] / levels.equity.loc[dates[i - 1]]
        nav.iloc[i] = holdings.sum()
        if dates[i] in decisions.index:
            holdings = nav.iloc[i] * np.array([weights.iloc[i], 1 - weights.iloc[i]])
    return {
        "nav": nav,
        "weights": weights,
        "decision_weights": decisions,
        "lookback_sessions": lookback,
    }
