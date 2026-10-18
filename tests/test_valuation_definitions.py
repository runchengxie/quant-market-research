"""Regression checks required for the new denominator calculations."""

import runpy
from pathlib import Path

import pytest

FUNCTIONS = runpy.run_path(str(Path(__file__).parents[1] / "scripts/analyze_valuation_definitions.py"))


def test_trailing_uses_matching_prior_year_ytd():
    assert FUNCTIONS["trailing"](60, 100, 40) == 120
    assert FUNCTIONS["positive_multiple"](1200, 120) == 10


@pytest.mark.parametrize("denominator", [0, -1, float("nan"), float("inf")])
def test_invalid_denominator_is_unavailable_not_cheap(denominator):
    assert FUNCTIONS["positive_multiple"](100, denominator) is None


@pytest.mark.parametrize("market_value", [0, -1, float("nan"), float("inf")])
def test_invalid_market_value_fails(market_value):
    with pytest.raises(ValueError, match="market value"):
        FUNCTIONS["positive_multiple"](market_value, 10)
