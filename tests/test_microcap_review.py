import pytest

from market_research.microcap_review import _grid, compound_periods


def test_compounds_percentage_periods_and_uses_observed_sessions():
    result = compound_periods([{"year": 2025, "observations": 252, "period_return": 10}, {"year": 2026, "observations": 126, "period_return": -10}])
    assert result["observations"] == 378
    assert result["cumulative_return"] == pytest.approx(-1)
    assert result["net_annual_return"] == pytest.approx((0.99 ** (252 / 378) - 1) * 100)


@pytest.mark.parametrize("rows", [[], [{"year": 2025, "observations": 252, "period_return": -100}], [{"year": 2025, "observations": 0, "period_return": 10}], [{"year": 2025, "observations": 252, "period_return": 10}] * 2])
def test_rejects_undefined_or_duplicate_periods(rows):
    with pytest.raises(ValueError):
        compound_periods(rows)


def test_requires_exact_grid_not_just_row_count():
    with pytest.raises(ValueError):
        _grid([{"a": 0, "b": 1}, {"a": 0, "b": 1}], ("a", "b"), ((0,), (1, 2)))
    _grid([{"a": 0, "b": 1}, {"a": 0, "b": 2}], ("a", "b"), ((0,), (1, 2)))
