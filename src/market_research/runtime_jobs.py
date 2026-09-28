"""Submit sequenced diagnostics to the durable backtest runtime CLI."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd


def _store_artifact(root: Path, payload: bytes) -> str:
    digest = hashlib.sha256(payload).hexdigest()
    destination = root / "sha256" / digest
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.read_bytes() != payload:
            raise ValueError("content-addressed artifact collision")
    else:
        destination.write_bytes(payload)
    return f"artifact://sha256/{digest}"


def _store_frame(root: Path, frame: pd.DataFrame, staging: Path) -> str:
    frame.to_parquet(staging, index=False)
    try:
        return _store_artifact(root, staging.read_bytes())
    finally:
        staging.unlink()


def _runtime_command(root: Path, command: str, argument: str) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest_runtime.cli",
            "--database",
            str(root / "jobs.sqlite"),
            "--artifact-root",
            str(root / "artifacts"),
            "--result-root",
            str(root / "results"),
            command,
            argument,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return json.loads(completed.stdout)


def run_sequenced_job(
    root: Path,
    variant: str,
    positions: pd.DataFrame,
    pricing: pd.DataFrame,
    clocks: dict[str, dict[str, str]],
    ledger_config: dict[str, Any],
    *,
    transaction_cost_bps: float,
) -> tuple[Path, dict[str, Any]]:
    """Return a verified runtime result directory and its receipt."""
    root.mkdir(parents=True, exist_ok=True)
    artifacts = root / "artifacts"
    inputs = {
        "positions_ref": _store_frame(artifacts, positions, root / f"{variant}-positions.parquet"),
        "pricing_ref": _store_frame(artifacts, pricing, root / f"{variant}-pricing.parquet"),
        "decision_clocks_ref": _store_artifact(
            artifacts, (json.dumps(clocks, ensure_ascii=False, sort_keys=True) + "\n").encode()
        ),
    }
    request = {
        "schema_version": 3,
        "idempotency_key": "",
        "backend": "native.sequenced_execution",
        "evidence_tier": "diagnostic",
        "inputs": inputs,
        "config": {
            "price_col": "adj_close",
            "tradable_col": "tradable",
            "buy_tradable_col": None,
            "sell_tradable_col": None,
            "limit_up_col": "limit_up",
            "limit_down_col": "limit_down",
            "listing_status_col": None,
            "transaction_cost_bps": transaction_cost_bps,
            "price_basis": "daily_clean.adjusted_close_proxy",
        },
        "execution": {"ledger_config": ledger_config},
        "budgets": {"wall_seconds": 1800, "memory_mb": 8192},
    }
    fingerprint = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:24]
    request["idempotency_key"] = f"market-research-{variant}-{fingerprint}"
    manifest = root / f"{variant}-request.json"
    manifest.write_text(json.dumps(request, ensure_ascii=False, sort_keys=True) + "\n")
    receipt = _runtime_command(root, "submit", str(manifest))
    job_id = str(receipt["job_id"])
    deadline = time.monotonic() + 1810
    while time.monotonic() < deadline:
        status = _runtime_command(root, "status", job_id)
        if status["status"] == "SUCCEEDED":
            verified = _runtime_command(root, "result", job_id)
            if verified.get("backend") != "native.sequenced_execution":
                raise ValueError("unexpected runtime backend in verified result")
            return root / "results" / job_id, {
                "job_id": job_id,
                "request_sha256": verified["request_sha256"],
                "result_sha256": status["result_sha256"],
            }
        if status["status"] in {"FAILED", "CANCELLED"}:
            raise RuntimeError(f"backtest job {job_id} {status['status']}: {status['error_code']}")
        time.sleep(0.1)
    raise TimeoutError(f"backtest job {job_id} did not finish within its budget")


def publish_verified_frames(result_dir: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("performance", "positions", "orders", "fills", "daily_ledger"):
        shutil.copy2(result_dir / f"{name}.parquet", destination / f"{name}.parquet")
