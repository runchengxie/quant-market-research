from datetime import date

import pandas as pd


def test_classify_missing_holdings_uses_windowed_evidence():
    from market_research.microcap_repair import classify_missing_holdings

    missing = pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000002.SZ", "000003.SZ", "000004.SZ"],
            "date": [date(2026, 1, 5)] * 4,
            "next_market_date": [date(2026, 1, 6)] * 4,
            "next_stock_date": [date(2026, 1, 8), date(2026, 1, 8), date(2026, 1, 8), date(2026, 1, 8)],
        }
    )
    instruments = pd.DataFrame({"ts_code": ["000003.SZ"], "delist_date": [date(2026, 1, 7)]})
    st_events = pd.DataFrame({"ts_code": ["000002.SZ"], "imp_date": [date(2026, 1, 7)]})
    suspend_events = pd.DataFrame({"ts_code": ["000001.SZ"], "trade_date": [date(2026, 1, 7)]})

    result = classify_missing_holdings(missing, instruments, st_events, suspend_events)

    assert list(result["classification"]) == [
        "suspension_evidence",
        "st_event_evidence",
        "delist_evidence",
        "unclassified_gap",
    ]


def test_terminal_missing_is_not_treated_as_suspension():
    from market_research.microcap_repair import classify_missing_holdings

    missing = pd.DataFrame(
        {"ts_code": ["000001.SZ"], "date": [date(2026, 1, 5)], "next_market_date": [pd.NaT], "next_stock_date": [pd.NaT]}
    )
    result = classify_missing_holdings(missing)
    assert result.loc[0, "classification"] == "terminal_or_source_gap"
