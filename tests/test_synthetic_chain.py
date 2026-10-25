"""An actual DATA reader → public replay builder → durable worker → report chain."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

from market_research.locked_providers import read_locked_pins

import pandas as pd
import pytest


SOURCE = Path(__file__).resolve().parents[1]


def _run_smoke(output):
    from market_research.synthetic_chain import run_smoke
    return run_smoke(output, expected_pins=read_locked_pins(SOURCE))


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
    assert {name: commits[name] for name in read_locked_pins(SOURCE)} == read_locked_pins(SOURCE)
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
    from market_research.synthetic_chain import publish_report

    evidence = _run_smoke(tmp_path / "chain")
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
    from market_research.synthetic_chain import publish_report

    evidence = _run_smoke(tmp_path / "chain")
    receipt = evidence["runtime_receipt"]
    results = tmp_path / "chain" / "runtime" / "results"
    wrong_job = results / "wrong-job"
    shutil.copytree(results / receipt["job_id"], wrong_job)
    destination = tmp_path / "unpublished"
    with pytest.raises(ValueError, match="identity"):
        publish_report(wrong_job, receipt, destination)
    assert not destination.exists()


def test_distribution_metadata_does_not_authorize_shadow_provider_source(tmp_path):
    _require_integration()
    import subprocess
    import sys

    shadow = tmp_path / "shadow"
    package = shadow / "quant_market_data_platform"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("# synthetic unpinned source shadow\n")
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            "import json, sys; from market_research.synthetic_chain import _environment; "
            "_environment(json.loads(sys.argv[1]))",
            json.dumps(read_locked_pins(SOURCE)),
        ],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(shadow)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "origin" in completed.stderr.lower()


def test_runtime_ignores_caller_pythonpath_and_current_directory(tmp_path, monkeypatch):
    _require_integration()

    shadow = tmp_path / "shadow"
    package = shadow / "backtest_runtime"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "cli.py").write_text("raise RuntimeError('UNPINNED_SHADOW_CLI')\n")
    monkeypatch.setenv("PYTHONPATH", str(shadow))
    monkeypatch.chdir(shadow)
    evidence = _run_smoke(tmp_path / "chain")
    assert evidence["checks"]["terminal_nav"] == pytest.approx(105_000.0)
    assert evidence["environment"]["module_origins"]


def test_wheel_layout_rejects_output_inside_callers_real_git_repository(tmp_path, monkeypatch):
    _require_integration()
    import subprocess
    from market_research import synthetic_chain

    repository = tmp_path / "caller"
    repository.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repository)], check=True)
    nested = repository / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)
    wheel_file = tmp_path / "wheel" / "site-packages" / "market_research" / "synthetic_chain.py"
    monkeypatch.setattr(synthetic_chain, "__file__", str(wheel_file))

    def unexpected_environment():
        raise AssertionError("repository output must be refused before environment validation")

    monkeypatch.setattr(synthetic_chain, "_environment", unexpected_environment)
    output = repository / "generated"
    with pytest.raises(ValueError, match="outside.*repository"):
        synthetic_chain.run_smoke(output)
    assert not output.exists()


@pytest.mark.parametrize("marker_kind", ["directory", "file"])
def test_empty_git_markers_do_not_define_source_repositories(tmp_path, marker_kind):
    from market_research.synthetic_chain import _git_root

    marker = tmp_path / ".git"
    if marker_kind == "directory":
        marker.mkdir()
    else:
        marker.touch()
    assert _git_root(tmp_path) is None


def test_nonfinite_but_hash_valid_ledger_cannot_be_published(tmp_path):
    _require_integration()
    from market_research.synthetic_chain import publish_report

    evidence = _run_smoke(tmp_path / "chain")
    receipt = dict(evidence["runtime_receipt"])
    result = tmp_path / "chain" / "runtime" / "results" / receipt["job_id"]
    path = result / "daily_ledger.parquet"
    daily = pd.read_parquet(path)
    daily["nav"] = float("nan")
    daily.to_parquet(path, index=False)
    manifest_path = result / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for item in manifest["inventory"]:
        if item["path"] == "daily_ledger.parquet":
            item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            item["size_bytes"] = path.stat().st_size
    manifest_path.write_text(json.dumps(manifest))
    receipt["result_sha256"] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    destination = tmp_path / "unpublished"
    with pytest.raises(ValueError, match="finite"):
        publish_report(result, receipt, destination)
    assert not destination.exists()


def test_default_cli_accepts_the_formal_locked_provider_combination(tmp_path):
    _require_integration()
    import subprocess
    import sys

    output = tmp_path / 'default-cli'
    completed = subprocess.run([
        sys.executable, '-I', '-m', 'market_research.synthetic_chain', '--output', str(output),
    ], cwd=tmp_path, capture_output=True, text=True, check=False, timeout=120)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    evidence = json.loads((output / 'evidence.json').read_text())
    commits = {name: item['commit'] for name, item in evidence['environment']['distributions'].items()}
    assert {name: commits[name] for name in read_locked_pins(SOURCE)} == read_locked_pins(SOURCE)
    assert evidence['checks']['terminal_nav'] == pytest.approx(105_000.0)
    assert evidence['checks']['tamper_rejected'] is True
