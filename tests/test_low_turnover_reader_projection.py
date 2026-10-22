"""Exercise unit conversion and full-stage selection on synthetic aggregate inputs."""
import csv
import hashlib
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("reader_projection", Path(__file__).parents[1] / "scripts/project_low_turnover_reader.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_unreviewed_input_is_rejected(tmp_path):
    (tmp_path / "manifest.json").write_text("{}")
    with pytest.raises(ValueError, match="unreviewed source hash"):
        module.project(tmp_path)


def test_projection_preserves_stage_and_converts_returns_to_percentage_points(tmp_path, monkeypatch):
    (tmp_path / "manifest.json").write_text("{}")
    with (tmp_path / "effect_summary.csv").open("w") as handle:
        writer = csv.writer(handle)
        writer.writerow(["signal", "count", "mean", "bootstrap_ci_low", "bootstrap_ci_high"])
        writer.writerows([
            ["plus_beta", 86, 0.0118, 0.008, 0.015],
            ["plus_beta_value", 86, 0.012, 0.009, 0.016],
            ["raw", 86, 0.0138, 0.0094, 0.0192],
            ["size", 86, 0.0163, 0.0123, 0.0206],
            ["size_lowvol", 86, 0.0086, 0.0057, 0.0118],
        ])
    with (tmp_path / "monthly_effects.csv").open("w") as handle:
        writer = csv.writer(handle)
        writer.writerow(["signal", "low_turnover_leg_return", "high_turnover_leg_return"])
        for stage in ["plus_beta_value", "raw", "size_lowvol", "size"]:
            writer.writerows([[stage, 0.01, -0.002]] * 86)
    # Replace only the reviewed input boundary with hashes for this synthetic fixture.
    hashes = {name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() for name in module.SOURCE_HASHES}
    monkeypatch.setattr(module, "SOURCE_HASHES", hashes)
    result = module.project(tmp_path)
    raw, _, _, full = result["controls"]
    assert raw["id"] == "raw"
    assert raw["spread"] == pytest.approx(1.38)
    assert full["id"] == "plus_beta_value"
    assert full["spread"] == pytest.approx(1.20)
    assert full["ciLow"] == pytest.approx(0.9)
    assert full["ciHigh"] == pytest.approx(1.6)
    assert full["low"] == pytest.approx(1.0)
    assert full["high"] == pytest.approx(-0.2)
    assert str(tmp_path) not in str(result)
