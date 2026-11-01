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
