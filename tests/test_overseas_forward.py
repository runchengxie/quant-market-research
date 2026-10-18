import hashlib
import json
from datetime import datetime, timedelta, timezone

import pytest

from market_research.studies.overseas_leadlag.forward import seal_forecast


def test_probe_is_sealed_but_never_eligible_and_cannot_overwrite(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    receipt = {
        "protocol": "overseas-receipt-v1", "mode": "capture_probe",
        "timely_capture": False, "target_date": "20261019", "sources": {},
        "cutoff_utc": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    }
    (run / "receipt.json").write_text(json.dumps(receipt))
    path = seal_forecast(run, tmp_path / "output")
    result = json.loads(path.read_text())
    assert not result["eligible"]
    assert "prediction_sealed_after_cutoff" in result["exclusion_reasons"]
    assert result["receipt_sha256"] == hashlib.sha256((run / "receipt.json").read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        seal_forecast(run, tmp_path / "output")


def test_valid_timely_signal_and_corrupt_input(tmp_path, monkeypatch):
    from market_research.studies.overseas_leadlag import forward

    class Frozen(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 10, 19, 0, 44, 30, tzinfo=timezone.utc)

    monkeypatch.setattr(forward, "datetime", Frozen)
    run = tmp_path / "fresh"
    run.mkdir()
    contents = {
        "calendar": "cal_date,is_open\n20261019,1\n",
        "spx": "trade_date,close\n20261015,100\n20261016,101\n",
    }
    sources = {}
    for name, content in contents.items():
        (run / (name + ".csv")).write_text(content)
        sources[name] = {"status": "ok", "file": name + ".csv",
                         "sha256": hashlib.sha256(content.encode()).hexdigest()}
    sources["spx"]["assumed_regular_close_utc"] = {
        "20261015": "2026-10-15T20:00:00+00:00",
        "20261016": "2026-10-16T20:00:00+00:00",
    }
    (run / "receipt.json").write_text(json.dumps({
        "protocol": "overseas-receipt-v1", "mode": "scheduled",
        "timely_capture": True, "target_date": "20261019", "sources": sources,
        "cutoff_utc": "2026-10-19T00:45:00+00:00",
    }))
    result = json.loads(seal_forecast(run, tmp_path / "out").read_text())
    assert result["eligible"] and result["prediction"]["direction"] == 1
    (run / "spx.csv").write_text("corrupt")
    invalid = json.loads(seal_forecast(run, tmp_path / "other").read_text())
    assert not invalid["eligible"] and "missing_or_invalid_input" in invalid["exclusion_reasons"]
