from pathlib import Path

import pandas as pd


def test_load_historical_turnover_panel_joins_daily_and_daily_basic(tmp_path: Path):
    from market_research.smallcap_turnover_history import load_historical_turnover_panel

    daily = tmp_path / "daily"
    basic = tmp_path / "daily_basic"
    daily.mkdir()
    basic.mkdir()
    pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000001.SZ", "000002.SZ"],
            "trade_date": [20080102, 20080103, 20080102],
            "amount": [10.0, 20.0, 30.0],
        }
    ).to_parquet(daily / "part.parquet", index=False)
    pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000001.SZ", "000002.SZ"],
            "trade_date": [20080102, 20080103, 20080102],
            "total_mv": [100.0, 110.0, 300.0],
        }
    ).to_parquet(basic / "part.parquet", index=False)

    panel, metadata = load_historical_turnover_panel(
        daily, basic, start_date="20080102", end_date="20080102"
    )

    assert panel[["symbol", "date", "turnover", "market_cap"]].to_dict("records") == [
        {"symbol": "000001.SZ", "date": "2008-01-02", "turnover": 10_000.0, "market_cap": 1_000_000.0},
        {"symbol": "000002.SZ", "date": "2008-01-02", "turnover": 30_000.0, "market_cap": 3_000_000.0},
    ]
    assert metadata["quality_status"] == "incomplete"
    assert "ST" in metadata["universe_filter"]


def test_loader_reads_platform_asset_data_subdirectory(tmp_path: Path):
    import duckdb

    from market_research.smallcap_turnover_history import load_historical_turnover_panel

    daily = tmp_path / "daily" / "data"
    basic = tmp_path / "daily_basic" / "data"
    daily.mkdir(parents=True)
    basic.mkdir(parents=True)
    con = duckdb.connect()
    try:
        con.execute("COPY (SELECT '000001.SZ' ts_code, 20080102 trade_date, 10.0 amount) TO ? (FORMAT PARQUET)", [str(daily / "part.parquet")])
        con.execute("COPY (SELECT '000001.SZ' ts_code, 20080102 trade_date, 100.0 total_mv) TO ? (FORMAT PARQUET)", [str(basic / "part.parquet")])
    finally:
        con.close()
    frame, _ = load_historical_turnover_panel(tmp_path / "daily", tmp_path / "daily_basic", "20080102", "20080102")
    assert len(frame) == 1
    assert frame.iloc[0]["symbol"] == "000001.SZ"
