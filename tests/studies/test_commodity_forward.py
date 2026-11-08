import numpy as np
import pandas as pd
import pytest

from market_research.studies.commodity_equity.funded_products import funded_products


def test_initial_final_and_rebalance_costs_are_funded():
    dates = pd.bdate_range("2020-01-01", periods=3)
    levels = pd.DataFrame(
        {"stock": [1, 2, 2], "product": [1, 1, 1], "cash": [1, 1, 1]}, index=dates
    )
    result = funded_products(levels, [0.8, 0.2, 0], {dates[1]}, fee_bps=100)
    assert result["initial_fee"] == pytest.approx(1 - 1 / 1.01)
    assert result["terminal_wealth"] == pytest.approx(
        1 + result["gross_pnl"] - result["total_fees"]
    )
    assert result["trade_events"] == 3
    assert result["final_fee"] > 0
    assert result["ledger"][1]["two_sided_turnover"] > 0


def test_cash_is_not_charged_as_a_second_trade_leg():
    d = pd.bdate_range("2020-01-01", periods=2)
    frame = pd.DataFrame({"stock": [1, 1], "cash": [1, 1]}, index=d)
    r = funded_products(frame, [0.8, 0.2], set(), fee_bps=100)
    expected_open_wealth = 1 / 1.008
    assert r["terminal_wealth"] == pytest.approx(expected_open_wealth * 0.992)


def test_no_fill_or_invalid_weight_admission():
    d = pd.bdate_range("2020-01-01", periods=2)
    with pytest.raises(ValueError):
        funded_products(
            pd.DataFrame({"stock": [1, np.nan], "cash": [1, 1]}, index=d), [0.8, 0.2], set()
        )


def test_registration_cannot_retroactively_start_or_overwrite(tmp_path):
    from market_research.studies.commodity_equity.paper_registry import register_paper

    protocol = {
        "protocol_id": "test",
        "first_eligible_session": "2026-11-09",
        "real_orders": False,
        "initial_capital_CNY": 1000000,
    }
    calendar = pd.DatetimeIndex(["2026-11-06", "2026-11-09"])
    now = pd.Timestamp("2026-11-08T01:00:00Z")
    receipt = register_paper(protocol, calendar, now, tmp_path / "new")
    assert receipt["observed_trades"] == 0
    with pytest.raises(FileExistsError):
        register_paper(protocol, calendar, now, tmp_path / "new")
    with pytest.raises(ValueError, match="future"):
        register_paper(protocol, calendar, pd.Timestamp("2026-11-09T01:00:00Z"), tmp_path / "bad")
