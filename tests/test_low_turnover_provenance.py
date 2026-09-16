import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from audit_low_turnover_provenance import audit_outputs


def test_audit_requires_manifest_and_effect_periods_to_match(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    effects = tmp_path / "effect.csv"
    manifest.write_text(json.dumps({"source_experiment": "demo", "completed_formation_periods_by_signal": {"raw": 2}}), encoding="utf-8")
    pd.DataFrame({"signal": ["raw"], "count": [2], "mean": [0.01], "bootstrap_ci_low": [0.0], "bootstrap_ci_high": [0.02]}).to_csv(effects, index=False)
    result = audit_outputs(manifest, effects)
    assert result["completed_periods"] == 2
    assert result["checks"]["positive_pe_sample_disclosed"] is True


def test_audit_rejects_duplicate_signal_rows(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    effects = tmp_path / "effect.csv"
    manifest.write_text(json.dumps({"completed_formation_periods_by_signal": {"raw": 2}}), encoding="utf-8")
    pd.DataFrame({"signal": ["raw", "raw"], "count": [2, 2], "mean": [0.01, 0.02], "bootstrap_ci_low": [0.0, 0.0], "bootstrap_ci_high": [0.02, 0.03]}).to_csv(effects, index=False)
    with pytest.raises(ValueError, match="duplicate"):
        audit_outputs(manifest, effects)
