"""Reject diagnostic corruption and unauthenticated observation clocks."""

import importlib
import json
from argparse import Namespace
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def script(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("analyze_financial_template_coverage")


@pytest.fixture
def diagnostic(tmp_path, script):
    vintage, output = tmp_path / "vintage", tmp_path / "diagnostic"
    output.mkdir()
    receipt = {"published_asset": False, "historical_pit_certified": False, "datasets": {}}
    for name in ["income", "balancesheet"]:
        for level in ["raw", "normalized"]:
            path = vintage / level / name / "manifest.yml"
            path.parent.mkdir(parents=True)
            path.write_text(f"{level}/{name}")
        table = output / f"{name}_diagnostic.parquet"
        pd.DataFrame({"_source_retrieved_at": ["2026-01-01T00:00:00Z"]}).to_parquet(table)
        receipt["datasets"][name] = {
            "diagnostic_sha256": script.digest(table),
            "old_normalized_manifest_sha256": script.digest(vintage / "normalized" / name / "manifest.yml"),
            "raw_manifest_sha256": script.digest(vintage / "raw" / name / "manifest.yml"),
        }
    (output / "diagnostic_receipt.json").write_text(json.dumps(receipt))
    return vintage, output


def test_valid_diagnostic_retains_actual_observation_time(script, diagnostic):
    hashes = {}
    data, _ = script.load_diagnostics(*diagnostic, hashes)
    assert set(data) == {"income", "balancesheet"}
    assert data["income"]._source_retrieved_at.tolist() == ["2026-01-01T00:00:00Z"]
    assert "diagnostic_receipt" in hashes


@pytest.mark.parametrize("target, message", [
    ("diagnostic", "diagnostic data hash differs"),
    ("normalized", "diagnostic baseline differs"),
    ("raw", "diagnostic raw vintage differs"),
])
def test_rejects_changed_diagnostic_or_baseline(script, diagnostic, target, message):
    vintage, output = diagnostic
    path = (output / "income_diagnostic.parquet" if target == "diagnostic"
            else vintage / target / "income" / "manifest.yml")
    path.write_bytes(path.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match=message):
        script.load_diagnostics(vintage, output, {})


@pytest.mark.parametrize("observation", [None, "invalid", (pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=1)).isoformat(), "missing_column"])
def test_rejects_missing_invalid_or_future_actual_observation(script, diagnostic, observation):
    vintage, output = diagnostic
    path = output / "income_diagnostic.parquet"
    frame = (pd.DataFrame({"other": [1]}) if observation == "missing_column"
             else pd.DataFrame({"_source_retrieved_at": [observation]}))
    frame.to_parquet(path)
    receipt_path = output / "diagnostic_receipt.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["datasets"]["income"]["diagnostic_sha256"] = script.digest(path)
    receipt_path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="observation timestamp"):
        script.load_diagnostics(vintage, output, {})


def test_rejects_repository_output_before_reading_sources(script):
    repo = Path(script.__file__).resolve().parents[1]
    with pytest.raises(ValueError, match="outside the repository"):
        script.run(Namespace(output=repo / "forbidden-diagnostic-output"))
