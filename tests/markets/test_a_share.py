from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def dated_st_manifest(tmp_path: Path):
    (tmp_path / "manifest.yml").write_text(
        "schema_version: tushare.a_share.daily_clean.v2\n"
        "inputs:\n  st_history_file: /fixture/validated-st-history.parquet\n"
        "  st_history_receipt_schema: market-data-platform.reconstructed-st-history.v2\n"
        "contracts:\n  st_availability: daily_clean.st_available_from.v1\n",
        encoding="utf-8",
    )


def test_a_share_adapter_converts_units_and_filters(tmp_path: Path):
    from market_research.markets.a_share import build_a_share_panel

    source = tmp_path / "000001.SZ.parquet"
    pd.DataFrame(
        {
            "trade_date": ["2026-01-01", "2026-01-02"],
            "close": [10.0, 11.0],
            "adj_close": [10.0, 11.0],
            "amount": [1000.0, 2000.0],
            "total_mv": [5000.0, 6000.0],
            "is_st": [False, True],
            "st_available_from": [None, "20260102"],
            "is_suspended": [False, False],
        }
    ).to_parquet(source)

    panel, metadata = build_a_share_panel(tmp_path)

    assert len(panel) == 1
    assert panel.loc[0, "turnover"] == 1_000_000
    assert panel.loc[0, "market_cap"] == 50_000_000
    assert panel.loc[0, "close"] == 10.0
    assert panel.loc[0, "adj_close"] == 10.0
    assert metadata.currency == "CNY"


def test_a_share_adapter_accepts_one_parquet_file(tmp_path: Path):
    from market_research.markets.a_share import build_a_share_panel

    source = tmp_path / "000001.SZ.parquet"
    pd.DataFrame(
        {
            "trade_date": ["2026-01-01"], "close": [10.0], "adj_close": [10.0],
            "amount": [1000.0], "total_mv": [5000.0], "is_st": [False],
            "st_available_from": [None], "is_suspended": [False],
        }
    ).to_parquet(source)

    panel, _ = build_a_share_panel(source)

    assert len(panel) == 1


def test_a_share_adapter_can_scan_directory_with_duckdb(tmp_path: Path):
    pytest.importorskip("duckdb")
    from market_research.markets.a_share import build_a_share_panel

    for symbol, close in [("000001.SZ", 10.0), ("000002.SZ", 20.0)]:
        pd.DataFrame(
            {
                "ts_code": [symbol], "trade_date": ["2026-01-01"], "close": [close],
                "adj_close": [close], "vol": [100.0], "amount": [1000.0],
                "total_mv": [5000.0], "is_st": [False],
                "st_available_from": [None], "is_suspended": [False],
            }
        ).to_parquet(tmp_path / f"{symbol}.parquet")

    panel, _ = build_a_share_panel(tmp_path, use_duckdb=True)

    assert set(panel["symbol"]) == {"000001.SZ", "000002.SZ"}


@pytest.mark.parametrize("engine", [False, True], ids=["pandas", "duckdb"])
def test_st_is_unknown_until_its_availability_date(tmp_path: Path, engine: bool):
    from market_research.markets.a_share import build_a_share_panel

    source = tmp_path / "000001.SZ.parquet"
    pd.DataFrame(
        {
            "trade_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "close": [10.0, 11.0, 12.0],
            "adj_close": [10.0, 11.0, 12.0],
            "amount": [1000.0] * 3,
            "total_mv": [5000.0] * 3,
            "is_st": [True] * 3,
            "st_available_from": ["20260102"] * 3,
            "is_suspended": [False] * 3,
        }
    ).to_parquet(source)

    panel, _ = build_a_share_panel(
        tmp_path, use_duckdb=engine, retain_ineligible_quotes=True
    )

    assert pd.isna(panel.loc[0, "is_st"])
    assert panel.loc[1:, "is_st"].tolist() == [True, True]
    assert panel["is_tradable"].tolist() == [False, False, False]


@pytest.mark.parametrize("engine", [False, True], ids=["pandas", "duckdb"])
def test_st_with_missing_availability_remains_unknown(tmp_path: Path, engine: bool):
    from market_research.markets.a_share import build_a_share_panel

    source = tmp_path / "000001.SZ.parquet"
    pd.DataFrame(
        {
            "trade_date": ["2026-01-01"], "close": [10.0], "adj_close": [10.0],
            "amount": [1000.0], "total_mv": [5000.0], "is_st": [True],
            "st_available_from": [None], "is_suspended": [False],
        }
    ).to_parquet(source)

    panel, metadata = build_a_share_panel(
        tmp_path, use_duckdb=engine, retain_ineligible_quotes=True
    )

    assert pd.isna(panel.loc[0, "is_st"])
    assert not panel.loc[0, "is_tradable"]
    assert metadata.quality_status == "incomplete"


@pytest.mark.parametrize("engine", [False, True], ids=["pandas", "duckdb"])
def test_v2_manifest_cannot_hide_missing_availability_column(tmp_path: Path, engine: bool):
    from market_research.markets.a_share import build_a_share_panel

    pd.DataFrame(
        {
            "trade_date": ["2026-01-01"], "close": [10.0], "adj_close": [10.0],
            "amount": [1000.0], "total_mv": [5000.0], "is_st": [False],
            "is_suspended": [False],
        }
    ).to_parquet(tmp_path / "000001.SZ.parquet")
    with pytest.raises(ValueError, match="missing st_available_from"):
        build_a_share_panel(tmp_path, use_duckdb=engine)
