"""Compact helpers for robust, month-weighted liquidity stability summaries."""

from __future__ import annotations

import numpy as np
import pandas as pd


def summarize_monthly_stability(frame: pd.DataFrame) -> list[dict[str, object]]:
    """Summarize monthly cross-sectional medians without pooling all security-days.

    Expected columns: market, year, bucket, month, monthly_adv_median,
    monthly_turnover_rate_median, security_days. Each input row is one market,
    calendar month and cap bucket.
    """
    keys = ["market", "year", "bucket"]
    result = []
    for key, group in frame.groupby(keys, sort=True, dropna=False):
        adv = group["monthly_adv_median"].dropna().to_numpy(dtype=float)
        rate = group["monthly_turnover_rate_median"].dropna().to_numpy(dtype=float)
        result.append(
            {
                "market": key[0],
                "year": int(key[1]),
                "bucket": key[2],
                "months": int(group["month"].nunique()),
                "security_days": int(group["security_days"].sum()),
                "adv20_median_of_months_usd": float(np.median(adv)) if len(adv) else None,
                "adv20_monthly_p25_usd": float(np.quantile(adv, 0.25)) if len(adv) else None,
                "adv20_monthly_p75_usd": float(np.quantile(adv, 0.75)) if len(adv) else None,
                "turnover_rate_median_of_months": float(np.median(rate)) if len(rate) else None,
                "turnover_rate_monthly_p25": float(np.quantile(rate, 0.25)) if len(rate) else None,
                "turnover_rate_monthly_p75": float(np.quantile(rate, 0.75)) if len(rate) else None,
            }
        )
    return result
