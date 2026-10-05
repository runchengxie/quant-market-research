import math

import pandas as pd
import pytest

from market_research.dividend_screen import (
    annual_volatility,
    dividend_totals,
    head_flags,
    payout_ratios,
    screen,
)


def events():
    return pd.DataFrame(
        [
            ["A", "20221231", "20230601", "实施", 0.6],
            ["A", "20221231", "20230601", "实施", 0.6],
            ["A", "20231231", "20240601", "预案", 0.8],
            ["B", "20221231", "20230601", "实施", 0.5],
        ],
        columns=["ts_code", "end_date", "ex_date", "div_proc", "cash_div_tax"],
    )


def test_implemented_calendar_year_deduplicates_and_fiscal_is_separate():
    totals = dividend_totals(events())
    assert totals.loc[0, "year"] == 2023
    assert totals.loc[0, "cash_div_tax"] == 0.6
    fiscal = dividend_totals(events(), basis="fiscal")
    assert fiscal.loc[0, "year"] == 2022


def test_conflicting_duplicate_rejected():
    df = events()
    df.loc[1, "cash_div_tax"] = 0.7
    with pytest.raises(ValueError, match="conflict"):
        dividend_totals(df)


def test_missing_dividend_not_zero_and_threshold_strict():
    totals = dividend_totals(events())
    quotes = pd.DataFrame(
        {"ts_code": ["A", "B", "C"], "year": [2023] * 3, "close": [10.0, 10.0, 10.0]}
    )
    result = screen(totals, quotes)
    assert result.loc[result.ts_code == "A", "selected"].item()
    assert not result.loc[result.ts_code == "B", "selected"].item()
    assert pd.isna(result.loc[result.ts_code == "C", "yield_pct"].item())


def test_volatility_includes_prior_year_close_and_missing_no_forward_fill():
    prices = pd.DataFrame(
        {
            "ts_code": ["A"] * 4,
            "trade_date": ["20221230", "20230103", "20230104", "20230105"],
            "adj_close": [100.0, 110.0, 99.0, 108.9],
        }
    )
    row = annual_volatility(prices, [2023]).iloc[0]
    assert row.return_count == 3
    assert row.volatility_pct == pytest.approx(
        pd.Series([0.1, -0.1, 0.1]).std() * math.sqrt(252) * 100
    )
    assert row.sample_status == "insufficient_sample"
    prices.loc[2, "adj_close"] = float("nan")
    assert annual_volatility(prices, [2023]).iloc[0].return_count == 1


def test_head_proxy_top_three_ties_deterministic_and_broker_independent():
    df = pd.DataFrame(
        {
            "ts_code": ["D", "C", "B", "A"],
            "year": [2023] * 4,
            "sw_l1": ["非银金融"] * 4,
            "is_broker": [True] * 4,
            "total_mv": [1, 2, 3, 4],
        }
    )
    result = head_flags(df)
    assert set(result.loc[result.broker_head, "ts_code"]) == {"A", "B", "C"}
    assert not result.loc[result.ts_code == "D", "industry_head"].item()


def test_payout_prefers_cash_amount_and_marks_eps_proxy():
    df = pd.DataFrame(
        {
            "ts_code": ["A", "B"],
            "year": [2023] * 2,
            "cash_div_tax": [0.5, 0.5],
            "cash_amount": [50.0, None],
            "net_profit_parent": [100.0, 100.0],
            "eps": [0.8, 1.0],
        }
    )
    result = payout_ratios(df)
    assert result.payout_pct.tolist() == [50.0, 50.0]
    assert result.payout_method.tolist() == ["cash_amount/net_profit_parent", "dps/eps_proxy"]


def test_tushare_base_share_ten_thousand_shares_to_cash_amount():
    from market_research.dividend_screen import normalize_tushare_cash

    df = events()
    df["base_share"] = [100.0, None, 100.0, 50.0]
    result = normalize_tushare_cash(df)
    assert result.cash_amount.iloc[0] == 600000.0
    assert pd.isna(result.cash_amount.iloc[1])


def test_cash_restated_to_year_end_shares_including_same_day_stock_distribution():
    from market_research.dividend_screen import restated_dividend_events

    df = pd.DataFrame(
        {
            "ts_code": ["A", "A"],
            "ex_date": ["20230601", "20231201"],
            "cash_div_tax": [0.6, 0.2],
            "stk_div": [0.5, 0.0],
            "cash_amount": [600.0, 300.0],
        }
    )
    result = restated_dividend_events(df)
    assert result.cash_div_tax.tolist() == pytest.approx([0.4, 0.2])
    assert result.cash_div_tax_raw.sum() == pytest.approx(0.8)
    assert result.cash_amount.tolist() == [600.0, 300.0]


def test_pure_stock_after_cash_and_different_year_is_not_applied():
    from market_research.dividend_screen import restated_dividend_events

    df = pd.DataFrame(
        {
            "ts_code": ["A"] * 3,
            "ex_date": ["20230301", "20230501", "20240101"],
            "cash_div_tax": [0.6, 0.0, 0.0],
            "stk_div": [0.0, 0.5, 1.0],
        }
    )
    result = restated_dividend_events(df)
    assert result.cash_div_tax.iloc[0] == pytest.approx(0.4)


def test_same_date_stock_factor_once_conflicts_rejected_missing_flagged():
    from market_research.dividend_screen import restated_dividend_events

    df = pd.DataFrame(
        {
            "ts_code": ["A"] * 3,
            "ex_date": ["20230601"] * 2 + ["20231201"],
            "cash_div_tax": [0.6, 0.6, 0.2],
            "stk_div": [0.5, 0.5, None],
        }
    )
    result = restated_dividend_events(df)
    assert result.cash_div_tax.iloc[0] == pytest.approx(0.4)
    assert result.stk_div_assumed_zero.iloc[2]
    df.loc[1, "stk_div"] = 0.6
    with pytest.raises(ValueError, match="conflict"):
        restated_dividend_events(df)
    df.loc[1, "stk_div"] = -0.1
    with pytest.raises(ValueError, match="negative"):
        restated_dividend_events(df)
