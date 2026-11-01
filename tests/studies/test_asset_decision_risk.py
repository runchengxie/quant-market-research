import numpy as np
import pandas as pd
import pytest

from market_research.studies.asset_returns.uncertainty import (
    block_indices,
    paired_uncertainty,
    policy_wealth,
)


def test_circular_blocks_keep_cross_asset_pairing_and_reproducibility():
    indices = block_indices(24, 6, 50, 17)
    assert indices.shape == (50, 24)
    assert np.array_equal(indices, block_indices(24, 6, 50, 17))
    assert np.all(np.diff(indices.reshape(50, 4, 6), axis=2) % 24 == 1)
    r = np.tile(np.array([0.03, -0.02, 0.01]), 8)
    result = paired_uncertainty(np.column_stack([r, r, np.zeros(24)]), r, r, draws=50)
    assert all(row["small_large_relative_cagr"]["lower"] == pytest.approx(0) for row in result)
    assert all(row["correlations"]["equity_gold"] is None for row in result)


def test_vectorized_policy_matches_existing_allocation():
    from market_research.studies.asset_returns.allocation import compare_allocation

    r = np.column_stack([np.tile([0.1, -0.05], 12), np.repeat(0.002, 24)])
    dates = pd.date_range("2020-01-31", periods=25, freq="ME")
    levels = np.vstack([np.ones(2), np.cumprod(1 + r, axis=0)])
    frame = pd.DataFrame({"date": dates, "total": levels[:, 0], "bond": levels[:, 1]})
    for policy in ["annual", "buy_hold"]:
        expected = compare_allocation(frame, {"total": 0.6, "bond": 0.4}, policy)
        wealth = policy_wealth(r[None, :, :], [0.6, 0.4], policy)[0]
        assert wealth[-1] == pytest.approx(expected["path"][-1]["wealth"])


def test_spending_cash_is_funded_and_exact_exhaustion_is_not_shortfall():
    from market_research.studies.asset_returns.spending import spending_path

    result = spending_path(
        np.zeros(12), np.ones(13), annual_real=0, buffer_months=0, shock_month=12, shock_real=100
    )
    assert result["terminal_real_capital"] == pytest.approx(0)
    assert result["first_shortfall_month"] is None
    assert result["real_paid"] == pytest.approx(100)
    result = spending_path(np.zeros(12), np.ones(13), annual_real=12, buffer_months=12)
    assert result["initial_cash"] == 12
    assert result["initial_risky"] == 88
    assert result["risky_sales_nominal"] == pytest.approx(0)
    assert result["terminal_real_capital"] == pytest.approx(88)


def test_spending_cpi_shortfalls_and_sequence_are_explicit():
    from market_research.studies.asset_returns.spending import spending_path

    result = spending_path([0, 0], [1, 2, 2], annual_real=12, shock_month=2, shock_real=100)
    assert result["first_shortfall_month"] == 2
    assert result["real_paid"] == pytest.approx(50)
    assert result["real_unmet"] == pytest.approx(52)
    bad_first = spending_path([-0.5, 1], [1, 1, 1], annual_real=12)
    good_first = spending_path([1, -0.5], [1, 1, 1], annual_real=12)
    assert bad_first["terminal_real_capital"] < good_first["terminal_real_capital"]
    assert np.prod(1 + np.array([-0.5, 1])) == np.prod(1 + np.array([1, -0.5]))


def test_stress_small_samples_and_recovery_censoring():
    from market_research.studies.asset_returns.stress import conditional_stress, event_recovery

    dates = pd.date_range("2019-12-31", periods=14, freq="ME")
    equity = np.array([1.0, 0.8, 0.7, *([0.75] * 11)])
    frame = pd.DataFrame(
        {
            "date": dates,
            "total": equity,
            "bond": np.ones(14),
            "gold": np.linspace(1, 1.1, 14),
            "cpi": np.ones(14),
        }
    )
    result = conditional_stress(frame)
    bad = next(r for r in result if r["id"] == "equity_down_5pct")
    assert bad["months"] == 2
    assert bad["correlations"]["equity_bond"] is None
    recovery = event_recovery(frame, [("test", "2019-12-31", "2020-12-31")])
    assert recovery[0]["equity"]["censored"] is True
    assert recovery[0]["equity"]["recovered_at"] is None
    assert recovery[0]["equity"]["underwater_observed_months"] == 13
