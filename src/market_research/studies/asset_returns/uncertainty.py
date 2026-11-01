"""Paired circular-block sensitivity, conditional on the observed monthly sample."""

from __future__ import annotations

import numpy as np


def block_indices(months: int, block: int, draws: int, seed: int) -> np.ndarray:
    if any(type(v) is not int or v < 1 for v in (months, block, draws)) or block > months:
        raise ValueError("positive integer sample, block and draws required; block <= sample")
    rng = np.random.default_rng(seed)
    starts = rng.integers(months, size=(draws, (months + block - 1) // block))
    return ((starts[:, :, None] + np.arange(block)) % months).reshape(draws, -1)[:, :months]


def policy_wealth(returns: np.ndarray, weights, policy: str) -> np.ndarray:
    r = np.asarray(returns, dtype=float)
    w = np.asarray(weights, dtype=float)
    if (
        r.ndim != 3
        or r.shape[1] < 1
        or len(w) != r.shape[2]
        or not np.isfinite(r).all()
        or (r <= -1).any()
        or not np.isfinite(w).all()
        or (w < 0).any()
        or abs(w.sum() - 1) > 1e-10
        or policy not in {"annual", "buy_hold"}
    ):
        raise ValueError("invalid monthly returns, target weights or policy")
    holdings = np.tile(w, (len(r), 1))
    wealth = np.ones((len(r), r.shape[1] + 1))
    for i in range(r.shape[1]):
        holdings *= 1 + r[:, i, :]
        wealth[:, i + 1] = holdings.sum(axis=1)
        if policy == "annual" and (i + 1) % 12 == 0 and i + 1 < r.shape[1]:
            holdings = wealth[:, i + 1, None] * w
    return wealth


def _range(values):
    values = np.asarray(values)
    values = values[np.isfinite(values)]
    if not len(values):
        return None
    return {
        "lower": float(np.quantile(values, 0.025)),
        "median": float(np.median(values)),
        "upper": float(np.quantile(values, 0.975)),
        "positive_fraction": float(np.mean(values > 0)),
        "valid_draws": len(values),
    }


def _correlations(r):
    out = {}
    for key, a, b in [("equity_bond", 0, 1), ("equity_gold", 0, 2), ("bond_gold", 1, 2)]:
        x, y = r[:, :, a], r[:, :, b]
        x, y = x - x.mean(axis=1, keepdims=True), y - y.mean(axis=1, keepdims=True)
        denom = np.sqrt((x * x).sum(axis=1) * (y * y).sum(axis=1))
        values = np.full(len(r), np.nan)
        np.divide((x * y).sum(axis=1), denom, out=values, where=denom > 1e-20)
        out[key] = _range(values)
    return out


def paired_uncertainty(
    multi_returns, small_returns, large_returns, *, draws=1000, seed=20261101, blocks=(6, 12, 24)
) -> list[dict]:
    multi = np.asarray(multi_returns, dtype=float)
    pair = np.column_stack([small_returns, large_returns]).astype(float)
    if (
        multi.ndim != 2
        or multi.shape[1] != 3
        or min(len(pair), len(multi)) < max(blocks)
        or not np.isfinite(multi).all()
        or not np.isfinite(pair).all()
        or (multi <= -1).any()
        or (pair <= -1).any()
    ):
        raise ValueError("finite paired monthly returns above -100% and sufficient sample required")
    results = []
    for block in blocks:
        pair_draws = pair[block_indices(len(pair), block, draws, seed)]
        relative = np.expm1(
            (np.log1p(pair_draws[:, :, 0]) - np.log1p(pair_draws[:, :, 1])).mean(axis=1) * 12
        )
        r = multi[block_indices(len(multi), block, draws, seed + 1)]
        hold = policy_wealth(r[:, :, :2], [0.6, 0.4], "buy_hold")
        annual = policy_wealth(r[:, :, :2], [0.6, 0.4], "annual")
        cagr_difference = annual[:, -1] ** (12 / len(multi)) - hold[:, -1] ** (12 / len(multi))
        hold_dd = (hold / np.maximum.accumulate(hold, axis=1) - 1).min(axis=1)
        annual_dd = (annual / np.maximum.accumulate(annual, axis=1) - 1).min(axis=1)
        results.append(
            {
                "block_months": block,
                "draws": draws,
                "small_large_relative_cagr": _range(relative),
                "annual_minus_hold_cagr": _range(cagr_difference),
                "annual_minus_hold_drawdown": _range(annual_dd - hold_dd),
                "correlations": _correlations(r),
            }
        )
    return results
