"""An actual DATA reader → public replay builder → durable worker → report chain."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os

import pandas as pd
import pytest


def _require_integration():
    missing = [
        name
        for name in ("quant_market_data_platform", "backtest_runtime")
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        reason = f"integration extra required; missing {', '.join(missing)}"
        if os.environ.get("REQUIRE_CROSSREPO_SMOKE") == "1":
            pytest.fail(reason)
        pytest.skip(reason)


def test_data_runtime_report_chain_has_exact_ledger_and_pinned_evidence(tmp_path):
    _require_integration()
    from market_research.synthetic_chain import run_smoke

    evidence = run_smoke(tmp_path / "chain")
    assert evidence["scope"] == "synthetic_public_market_research_only"
    assert evidence["checks"]["terminal_nav"] == pytest.approx(105_000.0)
    assert evidence["checks"]["tamper_rejected"] is True
    assert evidence["checks"]["position_count"] == 2
    assert evidence["environment"]["python"]["version"]
    commits = {
        name: item["commit"] for name, item in evidence["environment"]["distributions"].items()
    }
    assert commits["quant-market-data-platform"] == "71e40a0da03530fe88d70d4b212701d3af6a8cfa"
    assert commits["quant-backtest-runtime"] == "4fbfe973540e15fb6552068be037229d2f53d540"
    assert commits["quant-platform"] == "15ec62b66e894395d694049eaaace931de4a1265"
    report = tmp_path / "chain" / "report"
    daily = pd.read_parquet(report / "daily_ledger.parquet")
    assert daily.trade_date.astype(str).tolist() == ["20260105", "20260106"]
    assert daily.nav.tolist() == pytest.approx([100_000.0, 105_000.0])
    assert daily.cash.tolist() == pytest.approx([0.0, 0.0])
    fills = pd.read_parquet(report / "fills.parquet")
    assert fills.filled_notional.tolist() == pytest.approx([100_000.0])
    assert fills.transaction_cost.tolist() == pytest.approx([0.0])
    targets = pd.read_parquet(tmp_path / "chain" / "normalized" / "positions.parquet")
    assert targets.rebalance_date.tolist() == ["20260102", "20260105"]
    assert targets.entry_date.tolist() == ["20260105", "20260106"]
    assert json.loads((report / "summary.json").read_text())["evidence_tier"] == "diagnostic"
    for relative, digest in evidence["files"].items():
        assert hashlib.sha256((tmp_path / "chain" / relative).read_bytes()).hexdigest() == digest
    assert "report/daily_ledger.parquet" in evidence["files"]
    assert any(name.startswith("inputs/") for name in evidence["files"])


def test_tampered_runtime_frame_cannot_be_published(tmp_path):
    _require_integration()
    from market_research.synthetic_chain import publish_report, run_smoke

    evidence = run_smoke(tmp_path / "chain")
    receipt = evidence["runtime_receipt"]
    result = tmp_path / "chain" / "runtime" / "results" / receipt["job_id"]
    with (result / "daily_ledger.parquet").open("ab") as stream:
        stream.write(b"tampered")
    destination = tmp_path / "unpublished"
    with pytest.raises(ValueError, match="checksum"):
        publish_report(result, receipt, destination)
    assert not destination.exists()


def test_report_rejects_a_directory_other_than_the_verified_job(tmp_path):
    _require_integration()
    import shutil
    from market_research.synthetic_chain import publish_report, run_smoke

    evidence = run_smoke(tmp_path / "chain")
    receipt = evidence["runtime_receipt"]
    results = tmp_path / "chain" / "runtime" / "results"
    wrong_job = results / "wrong-job"
    shutil.copytree(results / receipt["job_id"], wrong_job)
    destination = tmp_path / "unpublished"
    with pytest.raises(ValueError, match="identity"):
        publish_report(wrong_job, receipt, destination)
    assert not destination.exists()
