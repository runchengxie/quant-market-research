"""Reproducible synthetic DATA → public research → runtime → report smoke check.

All prices, liquidity, eligibility and limits are invented. This checks adapters
and integrity, never vendor correctness or investable strategy performance.
"""

from __future__ import annotations

import argparse
import base64
from dataclasses import asdict
import hashlib
from importlib import import_module, metadata
import json
import math
import os
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
    "quant-platform": "3ac555bbfc8dba69d1a910320d5eefe947122df3",
    "research-contracts": "3ac555bbfc8dba69d1a910320d5eefe947122df3",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_root(start: Path) -> Path | None:
    """Recognize real checkouts/worktrees, ignoring empty .git placeholders."""
    start = start.resolve()
    for candidate in (start, *start.parents):
        marker = candidate / ".git"
        if marker.is_dir():
            valid = (marker / "HEAD").is_file() and (marker / "objects").is_dir()
        elif marker.is_file():
            text = marker.read_text(encoding="utf-8").strip()
            directory = (candidate / text[8:]).resolve() if text.startswith("gitdir: ") else None
            valid = directory is not None and (directory / "HEAD").is_file()
        else:
            valid = False
        if not valid:
            continue
        result = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )
        if result.returncode == 0 and Path(result.stdout.strip()).resolve() == candidate:
            return candidate
    return None


def _module_origins() -> dict[str, Any]:
    """Match imported owner files to their actual installed distribution RECORD."""
    modules = {
        "quant-market-data-platform": (
            "quant_market_data_platform",
            "quant_market_data_platform.research_views.a_share_research_data",
        ),
        "quant-backtest-runtime": (
            "backtest_runtime",
            "backtest_runtime.cli",
            "backtest_runtime.worker",
            "backtest_runtime.results",
        ),
        "quant-platform": ("portfolio_backtester", "portfolio_backtester.execution_sim"),
        "research-contracts": ("research_contracts",),
    }
    for owner, names in modules.items():
        top = import_module(names[0])
        expected = Path(
            metadata.distribution(owner).locate_file(names[0].replace(".", "/") + "/__init__.py")
        ).resolve()
        if top.__file__ is None or Path(top.__file__).resolve() != expected:
            raise ValueError(f"{names[0]} origin does not match installed {owner}")
        for name in names[1:]:
            import_module(name)
    prefixes = {
        "quant-market-data-platform": ("quant_market_data_platform",),
        "quant-backtest-runtime": ("backtest_runtime",),
        "quant-platform": (
            "portfolio_backtester",
            "quant_platform",
            "quant_execution_engine",
            "alpha_research",
            "strategy_pipeline",
            "ticknet",
        ),
        "research-contracts": ("research_contracts",),
    }
    origins = {}
    for owner, roots in prefixes.items():
        distribution = metadata.distribution(owner)
        records = {
            Path(distribution.locate_file(item)).resolve(): item
            for item in distribution.files or ()
        }
        loaded = [
            (name, module)
            for name, module in list(sys.modules.items())
            if any(name == root or name.startswith(root + ".") for root in roots)
        ]
        for name, module in loaded:
            origin = Path(module.__file__).resolve() if module.__file__ else None
            if origin not in records:
                raise ValueError(f"{name} origin does not match installed {owner}")
            record = records[origin]
            digest = _sha256(origin)
            encoded = base64.urlsafe_b64encode(bytes.fromhex(digest)).decode().rstrip("=")
            if record.hash is None or record.hash.mode != "sha256" or record.hash.value != encoded:
                raise ValueError(f"{name} origin differs from installed distribution RECORD")
            origins[name] = {"distribution": owner, "path": str(origin), "sha256": digest}
    return origins


def _environment(expected_pins: dict[str, str] | None = None) -> dict[str, Any]:
    from market_research.crossrepo_acceptance import (
        QUALITY_PIN, REPOSITORIES, validate_expected_pins,
    )

    expected_pins = (
        {**PINS, "research-code-quality": QUALITY_PIN}
        if expected_pins is None else validate_expected_pins(expected_pins)
    )
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
        expected = expected_pins.get(name)
        distribution = metadata.distribution(name)
        direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
        commit = direct_url.get("vcs_info", {}).get("commit_id")
        if expected is not None:
            official = f"https://github.com/runchengxie/{REPOSITORIES[name]}.git"
            if direct_url.get("url") != official:
                raise ValueError(f"{name} must come from official source {official}")
        if expected is not None and commit != expected:
            raise ValueError(f"{name} must be installed at {expected}; found {commit!r}")
        distributions[name] = {
            "version": distribution.version,
            "commit": commit,
            "direct_url": direct_url,
        }
    repository = _git_root(Path(__file__).resolve().parent)
    revision = (
        subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            text=True,
            capture_output=True,
            check=False,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        )
        if repository is not None
        else None
    )
    return {
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "market_research_source_revision": revision.stdout.strip()
        if revision is not None and revision.returncode == 0
        else None,
        "distributions": distributions,
        "module_origins": _module_origins(),
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
    if not math.isfinite(terminal):
        raise ValueError("synthetic terminal NAV must be finite")
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


def run_smoke(output: Path, expected_pins: dict[str, str] | None = None) -> dict[str, Any]:
    """Run the pinned integration without optional skips; retain auditable outputs."""
    if expected_pins is not None:
        from market_research.crossrepo_acceptance import validate_expected_pins

        expected_pins = validate_expected_pins(expected_pins)
    from quant_platform.backtest.legacy.execution_sim import ExecutionSimConfig

    output = output.resolve()
    repositories = {_git_root(Path.cwd()), _git_root(Path(__file__).resolve().parent)}
    if any(
        root is not None and (output == root or output.is_relative_to(root))
        for root in repositories
    ):
        raise ValueError("synthetic outputs must be outside the source repository")
    if output.exists():
        raise FileExistsError(f"output must be a new directory: {output}")
    environment = _environment(expected_pins) if expected_pins is not None else _environment()
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
        isolated=True,
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
        "runtime_launch": {
            "isolated": True,
            "python_flags": ["-I"],
            "cwd": str(output / "runtime"),
            "environment": {"PATH": os.defpath, "LANG": "C.UTF-8", "PYTHONNOUSERSITE": "1"},
        },
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
    parser.add_argument("--expected-providers", type=Path, help="explicit isolated acceptance commits")
    args = parser.parse_args(argv)
    expected = None
    if args.expected_providers:
        from market_research.crossrepo_acceptance import validate_expected_pins

        expected = validate_expected_pins(json.loads(args.expected_providers.read_text()))
    run_smoke(args.output, expected)
    print(f"Synthetic public chain verified: {args.output / 'evidence.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
