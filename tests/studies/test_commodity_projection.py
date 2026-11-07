"""Public evidence must contain derived aggregates, never private run metadata."""

from scripts.project_commodity_equity import project


def test_projection_drops_private_receipts_levels_and_nonprimary_return_bases():
    stats = {
        "start": "2006-12-29",
        "end": "2025-12-31",
        "observations": 4619,
        "cagr": 0.04,
        "total_return": 1.1,
        "max_drawdown": -0.5,
        "daily_volatility_252": 0.15,
        "drawdown_episodes": [{"private": "LOCAL_SECRET"}],
    }
    analysis = {
        "daily": {"equity": stats, "commodity": stats},
        "holding_periods": {},
        "monthly_max_drawdown": {},
        "diversification": {"correlation": {}, "down_market": {}},
        "allocation": [],
        "calendar_year_returns": [],
        "recent_periods": {},
    }
    pair = {
        "equity": "H00300.CSI",
        "commodity": "NHCI.NH",
        "audit": {"eligible": True},
        "equity_return_basis": "total_return",
        "commodity_return_basis": "commodity_futures_return_index",
        "analysis": analysis,
    }
    source = {
        "source_revision": "a" * 40,
        "manifest_sha256": "b" * 64,
        "input_receipts": [{"token": "LOCAL_SECRET"}],
        "coverage": {},
        "comparisons": {"H00300.CSI__NHCI.NH": pair},
        "missing_series": [],
        "series_metadata": {"H00300.CSI": {"currency": "CNY"}, "NHCI.NH": {"currency": "CNY"}},
    }
    result = project(source, source, source)
    import json

    assert "LOCAL_SECRET" not in json.dumps(result)
    assert "input_receipts" not in result
    assert result["primary"]["daily"]["commodity"]["cagr"] == 0.04
    assert result["primary"]["series"]["equity"]["id"] == "H00300.CSI"
    assert result["primary"]["series"]["equity"]["return_basis"] == "total_return"
    assert (
        result["primary"]["series"]["commodity"]["return_basis"] == "commodity_futures_return_index"
    )
    assert result["primary"]["series"]["equity"]["currency"] == "CNY"
    source["comparisons"]["H00300.CSI__NHCI.NH"]["audit"]["eligible"] = False
    blocked = project(source, source, source)
    assert blocked["primary"] is None
    assert blocked["allocations"] == []
