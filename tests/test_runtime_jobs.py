"""The public market diagnostic runs through the durable runtime worker."""

from __future__ import annotations

from dataclasses import asdict
from importlib import import_module

import pandas as pd
import pytest

from market_research.runtime_jobs import publish_verified_frames, run_sequenced_job


def test_sequenced_job_publishes_verified_daily_ledger(tmp_path) -> None:
    pytest.importorskip("backtest_runtime")
    execution_sim = import_module("portfolio_backtester.execution_sim")

    positions = pd.DataFrame(
        {
            "rebalance_date": ["20260102"],
            "entry_date": ["20260105"],
            "symbol": ["AAA"],
            "weight": [1.0],
        }
    )
    pricing = pd.DataFrame(
        {
            "trade_date": ["20260105", "20260106"],
            "symbol": ["AAA", "AAA"],
            "adj_close": [100.0, 105.0],
            "amount": [10_000_000.0] * 2,
            "tradable": [True, True],
            "limit_up": [False, False],
            "limit_down": [False, False],
        }
    )
    clocks = {
        "20260102": {
            "schema_version": "research.clock.v1",
            "timezone": "Asia/Shanghai",
            "information_cutoff_at": "2026-01-02T20:00:00+08:00",
            "signal_at": "2026-01-02T20:01:00+08:00",
            "decision_at": "2026-01-02T20:02:00+08:00",
            "earliest_order_at": "2026-01-05T09:30:00+08:00",
            "execution_window_start_at": "2026-01-05T09:30:00+08:00",
            "execution_window_end_at": "2026-01-05T15:00:00+08:00",
            "valuation_at": "2026-01-06T16:00:00+08:00",
            "timing_policy_id": "synthetic.next-session.v1",
            "trading_calendar_ref": "synthetic-calendar",
        }
    }
    config = execution_sim.ExecutionSimConfig(
        enabled=True,
        portfolio_value=100_000.0,
        participation_rate=1.0,
        liquidity_cols=("amount",),
    )
    result_dir, receipt = run_sequenced_job(
        tmp_path / "runtime",
        "microcap",
        positions,
        pricing,
        clocks,
        asdict(config),
        transaction_cost_bps=5.0,
    )
    destination = tmp_path / "published"
    publish_verified_frames(result_dir, destination)
    daily = pd.read_parquet(destination / "daily_ledger.parquet")
    assert not daily.empty
    assert daily.nav.iloc[-1] > 0
    assert len(receipt["request_sha256"]) == 64
    assert len(receipt["result_sha256"]) == 64
