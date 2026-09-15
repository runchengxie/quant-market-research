import duckdb
import pandas as pd
import pytest


def test_size_portfolio_returns_keep_stale_suspensions_and_bound_unknown_marks():
    from market_research.microcap_history import build_daily_portfolio_returns

    panel = pd.DataFrame(
        [
            ("2020-01-02", "A", 1.0, 100.0, 10.0, True, False),
            ("2020-01-02", "B", 2.0, 100.0, 20.0, True, False),
            ("2020-01-02", "C", 3.0, 100.0, 30.0, True, False),
            ("2020-01-02", "D", 4.0, 100.0, 40.0, True, False),
            ("2020-01-03", "A", 1.0, 100.0, 10.0, True, False),
            ("2020-01-03", "B", 2.0, 100.0, 20.0, True, False),
            ("2020-01-03", "C", 3.0, 100.0, 30.0, True, False),
            ("2020-01-03", "D", 4.0, 100.0, 40.0, True, False),
            ("2020-01-06", "B", 2.0, 100.0, 18.0, True, False),
            ("2020-01-06", "C", 3.0, 100.0, 36.0, True, False),
        ],
        columns=[
            "date",
            "symbol",
            "market_cap",
            "amount",
            "adj_close",
            "is_eligible",
            "is_suspended",
        ],
    )
    panel["date"] = pd.to_datetime(panel["date"])
    events = pd.DataFrame(
        {
            "symbol": ["A", "D"],
            "date": pd.to_datetime(["2020-01-06", "2020-01-06"]),
            "suspend_type": ["S", "U"],
        }
    )
    with duckdb.connect() as connection:
        connection.register("market_panel", panel)
        connection.register("suspension_events", events)
        returns = build_daily_portfolio_returns(connection, constituent_counts=(2, 4))

    first = returns.loc[returns.formation_date.eq(pd.Timestamp("2020-01-02"))].set_index(
        "constituent_count"
    )
    assert first.loc[2, "return_date"] == pd.Timestamp("2020-01-06")
    assert first.loc[2, "return_unknown_flat"] == pytest.approx(-0.05)
    assert first.loc[2, "return_unknown_total_loss"] == pytest.approx(-0.05)
    assert first.loc[2, "confirmed_suspension_stale_marks"] == 1
    assert first.loc[2, "unresolved_missing_marks"] == 0
    assert first.loc[2, "mark_status"] == "price_complete_with_suspension_mark"
    assert first.loc[4, "return_unknown_flat"] == pytest.approx(0.025)
    assert first.loc[4, "return_unknown_total_loss"] == pytest.approx(-0.225)
    assert first.loc[4, "unresolved_missing_marks"] == 1
    assert first.loc[4, "mark_status"] == "unresolved_price_sensitivity"


def test_size_portfolio_returns_reject_duplicate_security_dates():
    from market_research.microcap_history import build_daily_portfolio_returns

    duplicate = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-02", "2020-01-02"]),
            "symbol": ["A", "A"],
            "market_cap": [1.0, 1.0],
            "amount": [100.0, 100.0],
            "adj_close": [10.0, 10.0],
            "is_eligible": [True, True],
            "is_suspended": [False, False],
        }
    )
    with duckdb.connect() as connection:
        connection.register("market_panel", duplicate)
        connection.register(
            "suspension_events",
            pd.DataFrame(columns=["symbol", "date", "suspend_type"]),
        )
        with pytest.raises(ValueError, match="unique symbol/date"):
            build_daily_portfolio_returns(connection, constituent_counts=(1,))
