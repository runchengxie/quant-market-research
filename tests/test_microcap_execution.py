from __future__ import annotations

import json

import pandas as pd
import pytest

from market_research.microcap_execution import (
    build_replay_inputs, decision_clock, historical_name_mask, run_diagnostic,
)


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    for day, symbols in (
        ("20250102", ("A.SZ", "B.SZ")),
        ("20250103", ("A.SZ",)),
        ("20250106", ("A.SZ", "B.SZ")),
    ):
        for symbol in symbols:
            rows.append({
                "ts_code": symbol, "trade_date": day,
                "close": 10.0, "adj_close": 20.0, "total_mv": 1.0 if symbol == "B.SZ" else 2.0,
                "amount": 1000.0, "is_st": False, "is_suspended": False,
                "list_date": "20200101", "delist_date": None,
            })
    panel = pd.DataFrame(rows)
    limits = panel[["trade_date", "ts_code"]].assign(up_limit=11.0, down_limit=9.0)
    suspensions = pd.DataFrame({
        "ts_code": ["B.SZ"], "trade_date": ["20250103"], "suspend_type": ["S"]
    })
    return panel, limits, suspensions


def test_microcap_targets_have_independent_next_session_clocks() -> None:
    panel, limits, events = _inputs()
    positions, pricing, clocks, audit = build_replay_inputs(
        panel, limits, events, constituent_count=1
    )
    assert positions[["rebalance_date", "entry_date", "symbol"]].values.tolist() == [
        ["20250102", "20250103", "B.SZ"], ["20250103", "20250106", "A.SZ"]
    ]
    assert clocks["20250102"]["earliest_order_at"] == "2025-01-03T09:30:00+08:00"
    assert audit["confirmed_suspension_carry_rows"] == 1
    suspended = pricing.loc[pricing.symbol.eq("B.SZ") & pricing.trade_date.eq("20250103")]
    assert len(suspended) == 1
    assert not bool(suspended.iloc[0].tradable)
    assert suspended.iloc[0].adj_close == 20.0
    assert decision_clock("20250103", "20250106", "20250106")["decision_at"] < clocks[
        "20250103"
    ]["earliest_order_at"]


def test_unexplained_missing_quote_refuses_replay() -> None:
    panel, limits, _ = _inputs()
    with pytest.raises(ValueError, match="unexplained daily price gap"):
        build_replay_inputs(panel, limits, pd.DataFrame(), constituent_count=1)


def test_unknown_limit_refuses_replay() -> None:
    panel, limits, events = _inputs()
    limits.loc[limits.ts_code.eq("A.SZ") & limits.trade_date.eq("20250103"), "up_limit"] = None
    with pytest.raises(ValueError, match="unknown prices, liquidity or price limits"):
        build_replay_inputs(panel, limits, events, constituent_count=1)


def test_ineligible_and_duplicate_input_refuses_replay() -> None:
    panel, limits, events = _inputs()
    with pytest.raises(ValueError, match="duplicate"):
        build_replay_inputs(pd.concat([panel, panel.iloc[[0]]]), limits, events,
                            constituent_count=1)
    panel.loc[panel.ts_code.eq("B.SZ") & panel.trade_date.eq("20250102"), "is_st"] = True
    positions, _, _, _ = build_replay_inputs(panel, limits, events, constituent_count=1)
    assert positions.iloc[0].symbol == "A.SZ"


def test_historical_name_excludes_st_and_known_delisting_period() -> None:
    panel, limits, events = _inputs()
    namechange = pd.DataFrame([
        {"ts_code": "A.SZ", "name": "样例A", "change_reason": "其他",
         "start_date": "20200101", "end_date": None, "ann_date": "20191231"},
        {"ts_code": "B.SZ", "name": "*ST样例B", "change_reason": "*ST",
         "start_date": "20200101", "end_date": "20250101", "ann_date": "20191231"},
        {"ts_code": "B.SZ", "change_reason": "退市整理期", "start_date": "20250102",
         "name": "退市样例B", "end_date": "20250106", "ann_date": "20250101"},
        {"ts_code": "A.SZ", "name": "退市样例A", "change_reason": "退市整理期",
         "start_date": "20250103", "end_date": "20250106", "ann_date": "20250103"},
    ])
    mask = historical_name_mask(namechange, panel)
    assert not bool(mask.loc[panel.ts_code.eq("B.SZ")].any())
    assert bool(mask.loc[panel.ts_code.eq("A.SZ") & panel.trade_date.lt("20250106")].all())
    assert not bool(mask.loc[panel.ts_code.eq("A.SZ") & panel.trade_date.eq("20250106")].any())
    positions, _, _, audit = build_replay_inputs(
        panel, limits, events, constituent_count=1, namechange=namechange,
    )
    assert positions.iloc[0].symbol == "A.SZ"
    assert audit["historical_name_excluded_rows"] == 3
    with pytest.raises(ValueError, match="only 0 eligible"):
        build_replay_inputs(panel, limits, events, constituent_count=1,
                            namechange=namechange.assign(ann_date="20250101"))


def test_missing_source_writes_blocked_receipt(tmp_path) -> None:
    output = tmp_path / "diagnostic"
    with pytest.raises(FileNotFoundError, match="no manifest"):
        run_diagnostic(
            daily_asset=tmp_path / "missing", limit_asset=tmp_path / "limits",
            instruments=tmp_path / "instruments.parquet", suspensions=tmp_path / "s.parquet",
            namechange_asset=tmp_path / "namechange.parquet",
            output_dir=output, start="20250102", end="20250106", constituent_count=1,
        )
    receipt = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert receipt["evidence_tier"] == "blocked"
    assert "no manifest" in receipt["reason"]
