import duckdb
import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.fitness import (
    reconcile_selection,
    reference_timing,
    prepare_paths,
)


def test_selection_audit_keeps_missing_extra_and_wrong_first_rows_separate():
    expected = pd.DataFrame(
        {
            "SecuCode": [1, 2, 3],
            "minute": [570] * 3,
            "absolute_ms": [34200000] * 3,
            "source_row": [1, 2, 3],
        }
    )
    saved = pd.DataFrame(
        {
            "SecuCode": [1, 2, 4],
            "minute": [570] * 3,
            "absolute_ms": [34200000] * 3,
            "source_row": [1, 9, 4],
        }
    )
    out = reconcile_selection(expected, saved)
    assert out == {
        "expected_bins": 3,
        "saved_bins": 3,
        "missing_saved_bins": 1,
        "extra_saved_bins": 1,
        "wrong_earliest_bins": 1,
        "matched_bins": 1,
    }


def test_selection_audit_rejects_duplicate_minute_keys():
    rows = pd.DataFrame(
        {
            "SecuCode": [1, 1],
            "minute": [570, 570],
            "absolute_ms": [34200000] * 2,
            "source_row": [1, 2],
        }
    )
    with pytest.raises(ValueError, match="duplicate"):
        reconcile_selection(rows, rows)


def test_reference_audit_does_not_turn_future_or_ambiguous_keys_into_verified_orders():
    con = duckdb.connect()
    orders = pd.DataFrame(
        {
            "SecuCode": [1, 1, 1, 1],
            "OrderID": [10, 20, 20, 30],
            "time_ms_absolute": [100, 100, 200, 300],
        }
    )
    trades = pd.DataFrame(
        {
            "SecuCode": [1] * 5,
            "BuyID": [10, 20, 30, 0, 40],
            "SellID": [10] * 5,
            "time_ms_absolute": [150] * 5,
            "Price": [100] * 5,
            "Volume": [10] * 5,
        }
    )
    con.register("orders", orders)
    con.register("trades", trades)
    out = reference_timing(con, "orders", "trades", "OrderID")["buy"]
    assert out["eligible_trades"] == 5
    assert out["unique_key_available_by_trade"] == 1
    assert out["ambiguous_key_available_by_trade"] == 1
    assert out["key_only_after_trade"] == 1
    assert out["missing_key"] == 2
    assert out["nonpositive_reference"] == 1


def test_reference_keys_include_channel_when_both_sources_have_it():
    con = duckdb.connect()
    con.register(
        "orders",
        pd.DataFrame({"SecuCode": [1], "Channel": [1], "OrderID": [10], "time_ms_absolute": [100]}),
    )
    con.register(
        "trades",
        pd.DataFrame(
            {
                "SecuCode": [1],
                "Channel": [2],
                "BuyID": [10],
                "SellID": [10],
                "time_ms_absolute": [150],
                "Price": [100],
                "Volume": [10],
            }
        ),
    )
    assert reference_timing(con, "orders", "trades", "OrderID")["buy"]["missing_key"] == 1


def test_paths_filter_declared_day_before_duplicate_times_and_reject_late_arrival():
    frame = pd.DataFrame(
        {
            "SecuCode": [1, 1, 1, 2],
            "TradingDay": [20210104, 20210115, 20210104, 20210104],
            "time_ms": [0, 60000, 60000, 70000],
            "source_row": [0, 1, 2, 3],
        }
    )
    paths, counts = prepare_paths(frame, 20210104, [1, 2], max_arrival_delay_ms=60000)
    assert paths[1].source_row.tolist() == [0, 2]
    assert 2 not in paths
    assert counts["late_arrival_securities"] == 1


def test_invalid_displayed_book_blocks_whole_execution_path_without_silent_filtering():
    frame = pd.DataFrame(
        {
            "SecuCode": [1, 1],
            "TradingDay": [20210104] * 2,
            "time_ms": [0, 60000],
            "source_row": [1, 2],
            "book_valid": [True, False],
        }
    )
    paths, counts = prepare_paths(frame, 20210104, [1])
    assert not paths
    assert counts["invalid_book_securities"] == 1


def test_equal_timestamps_remain_ambiguous_exchange_order():
    con = duckdb.connect()
    con.register(
        "orders", pd.DataFrame({"SecuCode": [1], "OrderID": [10], "time_ms_absolute": [100]})
    )
    con.register(
        "trades",
        pd.DataFrame(
            {
                "SecuCode": [1],
                "BuyID": [10],
                "SellID": [10],
                "time_ms_absolute": [100],
                "Price": [100],
                "Volume": [10],
            }
        ),
    )
    result = reference_timing(con, "orders", "trades", "OrderID")["buy"]
    assert result["first_timestamp_equal_trade"] == 1
