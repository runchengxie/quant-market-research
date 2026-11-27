import pytest
from market_research.bmll_pilot import (
    decode_statement,
    annual_cost_hurdle,
    cap_bucket,
    paired_summary,
)


def test_rejects_truncated_or_unfinished_sql_results():
    with pytest.raises(ValueError):
        decode_statement({"status": {"state": "RUNNING"}})
    with pytest.raises(ValueError):
        decode_statement({"status": {"state": "SUCCEEDED"}, "manifest": {"truncated": True}})


def test_manifest_types_preserve_null_and_check_row_count():
    raw = {
        "status": {"state": "SUCCEEDED"},
        "manifest": {
            "total_row_count": 2,
            "schema": {"columns": [{"name": "x", "type_name": "DOUBLE"}]},
        },
        "result": {"data_array": [["1.25"], [None]]},
    }
    assert decode_statement(raw) == [{"x": 1.25}, {"x": None}]
    raw["manifest"]["total_row_count"] = 3
    with pytest.raises(ValueError):
        decode_statement(raw)


def test_cost_is_full_round_trip_not_twice_full_spread():
    assert annual_cost_hurdle(100, 21, 0.5) == pytest.approx(0.06)
    with pytest.raises(ValueError):
        annual_cost_hurdle(100, 0)
    assert cap_bucket(1e8) == "100m_1bn"
    assert cap_bucket(None) == "unclassified"
    assert cap_bucket(float("nan")) == "unclassified"


def test_paired_comparison_does_not_pool_unequal_date_counts():
    rows = [
        {"ticker": "A", "trade_date": d, "x": x}
        for d, x in [("a", 10), ("b", 30), ("c", 40), ("d", 60), ("e", 80)]
    ]
    rows += [{"ticker": "B", "trade_date": "a", "x": 9}]
    assert paired_summary(rows, "x", {"a", "b"}, {"c", "d", "e"}) == [
        {"ticker": "A", "baseline": 20, "comparison": 60, "ratio": 3, "difference": 40}
    ]
