"""Reproducible synthetic DATA → public research → runtime → report smoke check.

All prices, liquidity, eligibility and limits are invented. This checks adapters
and integrity, never vendor correctness or investable strategy performance.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any

import pandas as pd

from market_research.microcap_execution import build_replay_inputs
from market_research.runtime_jobs import publish_verified_frames, run_sequenced_job

PINS = {
    "quant-market-data-platform": "71e40a0da03530fe88d70d4b212701d3af6a8cfa",
    "quant-backtest-runtime": "4fbfe973540e15fb6552068be037229d2f53d540",
    "quant-platform": "15ec62b66e894395d694049eaaace931de4a1265",
    "research-contracts": "15ec62b66e894395d694049eaaace931de4a1265",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _environment() -> dict[str, Any]:
    distributions = {}
    names = [
        *PINS,
        "market-research",
        "research-code-quality",
        "pandas",
        "pyarrow",
        "numpy",
        "pyyaml",
        "scipy",
    ]
    for name in names:
        expected = PINS.get(name)
        distribution = metadata.distribution(name)
        direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
        commit = direct_url.get("vcs_info", {}).get("commit_id")
        if expected is not None and commit != expected:
            raise ValueError(f"{name} must be installed at {expected}; found {commit!r}")
        distributions[name] = {
            "version": distribution.version,
            "commit": commit,
            "direct_url": direct_url,
        }
    repository = Path(__file__).resolve().parents[2]
    revision = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "market_research_source_revision": revision.stdout.strip()
        if revision.returncode == 0
        else None,
        "distributions": distributions,
        "source_files": {
            path.name: _sha256(path)
            for path in (
                Path(__file__),
                Path(__file__).with_name("runtime_jobs.py"),
                Path(__file__).with_name("microcap_execution.py"),
            )
        },
    }


def _fixture(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from quant_market_data_platform.research_views.a_share_research_data import (
        AShareResearchAssets,
        load_a_share_research_daily,
        load_a_share_research_instruments,
    )

    daily = root / "daily_clean"
    (daily / "data").mkdir(parents=True)
    (daily / "manifest.yml").write_text(
        "schema_version: tushare.a_share.daily_clean.v2\nstatus: completed\n"
        "contracts:\n  st_availability: daily_clean.st_available_from.v1\n"
        "source: synthetic_no_vendor_data\n",
        encoding="utf-8",
    )
    pd.DataFrame(
        {
            "trade_date": ["2026-01-02", "2026-01-05", "2026-01-06"],
            "symbol": ["000001.SZ"] * 3,
            "close": [100.0, 100.0, 105.0],
            "turnover_rate": [10.0] * 3,
            "total_mv": [1000.0] * 3,
            "is_st": [False] * 3,
            "st_available_from": [None] * 3,
            "is_suspended": [False] * 3,
            "list_date": ["2010-01-01"] * 3,
        }
    ).to_parquet(daily / "data" / "part.parquet", index=False)
    instruments = root / "instruments.parquet"
    pd.DataFrame(
        {"symbol": ["000001.SZ"], "industry": ["synthetic"], "delist_date": [None]}
    ).to_parquet(instruments, index=False)
    assets = AShareResearchAssets(
        data_root=root,
        current_contract=root / "unused-current.json",
        daily_clean=daily,
        instruments=instruments,
        daily_as_of="20260106",
    )
    panel = load_a_share_research_daily(assets, end_date="20260106")
    basic = load_a_share_research_instruments(assets)
    panel = panel.merge(basic[["symbol", "delist_date"]], on="symbol", validate="many_to_one")
    panel = panel.rename(columns={"symbol": "ts_code"})
    panel["trade_date"] = panel.trade_date.dt.strftime("%Y%m%d")
    panel["list_date"] = pd.to_datetime(panel.list_date).dt.strftime("%Y%m%d")
    # The DATA research API does not provide adjusted prices or liquidity.
    # These are explicitly synthetic fixture assumptions, not inferred real data.
    panel["adj_close"] = panel.close  # No corporate actions in this fixture.
    panel["amount"] = 10_000_000.0
    limits = panel[["trade_date", "ts_code"]].assign(up_limit=200.0, down_limit=50.0)
    events = pd.DataFrame(columns=["ts_code", "trade_date", "suspend_type"])
    return panel, limits, events


def publish_report(result: Path, receipt: dict[str, Any], destination: Path) -> dict[str, Any]:
    """Reverify the worker result before any report directory or files are created."""
    from backtest_runtime.results import read_job_result

    if result.name != receipt["job_id"]:
        raise ValueError("runtime result directory identity mismatch")
    read_job_result(
        result.parent,
        job_id=receipt["job_id"],
        manifest_sha256=receipt["result_sha256"],
        request_sha256=receipt["request_sha256"],
    )
    if destination.exists():
        raise FileExistsError(f"report destination already exists: {destination}")
    daily = pd.read_parquet(result / "daily_ledger.parquet")
    terminal = float(daily.nav.iloc[-1])
    if abs(terminal - 105_000.0) > 1e-7:
        raise ValueError(f"synthetic ledger differs from hand calculation: {terminal}")
    publish_verified_frames(result, destination)
    summary = {
        "evidence_tier": "diagnostic",
        "source": "synthetic_no_vendor_data",
        "initial_capital": 100_000.0,
        "terminal_nav": terminal,
        "expected_terminal_nav": 105_000.0,
        "transaction_cost_bps": 0.0,
        "runtime_receipt": receipt,
        "limitations": "synthetic public adapters only; no private strategy or Intel publication",
    }
    _write_json(destination / "summary.json", summary)
    return summary


def run_smoke(output: Path) -> dict[str, Any]:
    """Run the pinned integration without optional skips; retain auditable outputs."""
    from portfolio_backtester.execution_sim import ExecutionSimConfig

    output = output.resolve()
    repository = Path(__file__).resolve().parents[2]
    if output == repository or output.is_relative_to(repository):
        raise ValueError("synthetic outputs must be outside the source repository")
    if output.exists():
        raise FileExistsError(f"output must be a new directory: {output}")
    environment = _environment()  # Fail before creating outputs on absent/wrong dependencies.
    output.mkdir(parents=True)
    panel, limits, events = _fixture(output / "inputs")
    positions, pricing, clocks, audit = build_replay_inputs(
        panel,
        limits,
        events,
        constituent_count=1,
    )
    normalized = output / "normalized"
    normalized.mkdir()
    positions.to_parquet(normalized / "positions.parquet", index=False)
    pricing.to_parquet(normalized / "pricing.parquet", index=False)
    _write_json(normalized / "decision_clocks.json", clocks)
    config = ExecutionSimConfig(
        enabled=True,
        portfolio_value=100_000.0,
        participation_rate=1.0,
        liquidity_cols=("amount",),
    )
    result, receipt = run_sequenced_job(
        output / "runtime",
        "synthetic-chain",
        positions,
        pricing,
        clocks,
        asdict(config),
        transaction_cost_bps=0.0,
    )
    summary = publish_report(result, receipt, output / "report")
    tampered = output / "tampered" / receipt["job_id"]
    shutil.copytree(result, tampered)
    with (tampered / "daily_ledger.parquet").open("ab") as stream:
        stream.write(b"synthetic-tamper")
    try:
        publish_report(tampered, receipt, output / "rejected-report")
    except ValueError as error:
        if "checksum" not in str(error):
            raise
        tamper_error = str(error)
    else:
        raise AssertionError("tampered frame was accepted")
    files = {
        str(path.relative_to(output)): _sha256(path)
        for directory in (output / "inputs", normalized, output / "report", result)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }
    request = output / "runtime" / "synthetic-chain-request.json"
    files[str(request.relative_to(output))] = _sha256(request)
    evidence = {
        "schema_version": "market-research.synthetic-chain.v1",
        "scope": "synthetic_public_market_research_only",
        "environment": environment,
        "runtime_receipt": receipt,
        "files": files,
        "input_audit": audit,
        "checks": {
            "terminal_nav": summary["terminal_nav"],
            "position_count": len(positions),
            "tamper_rejected": True,
            "tamper_error": tamper_error,
        },
        "assumptions": {
            "corporate_actions": "none",
            "liquidity": "synthetic_constant",
            "limits": "synthetic_50_to_200",
            "transaction_cost_bps": 0.0,
        },
    }
    _write_json(output / "evidence.json", evidence)
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", required=True, type=Path, help="new directory outside the source repository"
    )
    args = parser.parse_args(argv)
    run_smoke(args.output)
    print(f"Synthetic public chain verified: {args.output / 'evidence.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
