from datetime import date

import pandas as pd
import pytest


def _metadata():
    from market_research.contracts import PanelMetadata

    return PanelMetadata(
        source="fixture",
        as_of="2026-09-07",
        currency="CNY",
        universe_filter="all",
        fx_method="none",
        feature_lag=1,
        coverage_start="2026-01-01",
        coverage_end="2026-01-02",
        calendar_mode="explicit",
        quality_status="verified",
    )


def test_normalize_panel_orders_columns_and_dates():
    from market_research.contracts import CANONICAL_COLUMNS, normalize_panel

    frame = pd.DataFrame(
        {
            "symbol": ["000001.SZ"],
            "market": ["a_share"],
            "date": ["2026-01-01T00:00:00"],
            "close": [10.0],
            "volume": [100.0],
            "turnover": [1000.0],
            "market_cap": [1_000_000.0],
            "currency": ["CNY"],
            "is_tradable": [True],
            "is_suspended": [False],
            "source": ["fixture"],
        }
    )

    result, metadata = normalize_panel(frame, _metadata())

    assert list(result.columns) == list(CANONICAL_COLUMNS)
    assert result.loc[0, "date"] == date(2026, 1, 1)
    assert pd.isna(result.loc[0, "adj_close"])
    assert metadata.currency == "CNY"


def test_validate_panel_rejects_duplicate_keys():
    from market_research.contracts import validate_panel

    frame = pd.DataFrame(
        {
            "market": ["us", "us"],
            "symbol": ["ABC", "ABC"],
            "date": [date(2026, 1, 1), date(2026, 1, 1)],
            "close": [1.0, 1.0],
            "volume": [1.0, 1.0],
            "turnover": [1.0, 1.0],
            "market_cap": [2.0, 2.0],
            "currency": ["USD", "USD"],
            "is_tradable": [True, True],
            "is_suspended": [False, False],
            "source": ["fixture", "fixture"],
        }
    )

    assert "duplicate_key" in validate_panel(frame)


def test_normalize_panel_rejects_invalid_currency():
    from market_research.contracts import normalize_panel

    frame = pd.DataFrame(
        {
            "market": ["us"],
            "symbol": ["ABC"],
            "date": ["2026-01-01"],
            "close": [1.0],
            "volume": [1.0],
            "turnover": [1.0],
            "market_cap": [2.0],
            "currency": ["EUR"],
            "is_tradable": [True],
            "is_suspended": [False],
            "source": ["fixture"],
        }
    )

    with pytest.raises(ValueError, match="currency"):
        normalize_panel(frame, _metadata())


def _numeric_panel(value, column):
    frame = pd.DataFrame({
        "market": ["us"], "symbol": ["ABC"], "date": ["2026-01-01"],
        "close": [1.0], "volume": [1.0], "turnover": [1.0], "market_cap": [2.0],
        "currency": ["USD"], "is_tradable": [True], "is_suspended": [False],
        "source": ["fixture"],
    })
    frame[column] = [value]
    return frame


@pytest.mark.parametrize("column", ["close", "volume", "turnover", "market_cap"])
def test_validate_panel_reports_non_numeric_values(column):
    from market_research.contracts import validate_panel

    assert f"invalid_numeric:{column}" in validate_panel(_numeric_panel("broken", column))


@pytest.mark.parametrize("column", ["close", "volume", "turnover", "market_cap"])
def test_normalize_panel_rejects_non_numeric_values_before_coercion(column):
    from market_research.contracts import normalize_panel

    with pytest.raises(ValueError, match=f"invalid_numeric:{column}"):
        normalize_panel(_numeric_panel("broken", column), _metadata())


@pytest.mark.parametrize("value", [None, float("nan"), pd.NA, "12.5", 0.0])
def test_numeric_panel_preserves_supported_missing_values_and_numeric_strings(value):
    from market_research.contracts import normalize_panel, validate_panel

    frame = _numeric_panel(value, "close")
    assert validate_panel(frame) == []
    result, _ = normalize_panel(frame, _metadata())
    if pd.isna(value):
        assert pd.isna(result.loc[0, "close"])
    else:
        assert result.loc[0, "close"] == float(value)
