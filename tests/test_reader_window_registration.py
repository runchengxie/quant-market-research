from datetime import datetime, timezone
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("reader_register", Path(__file__).parents[1] / "scripts/register_research_window.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_late_registration_is_rejected(tmp_path):
    source = tmp_path / "input.json"
    source.write_text("{}")
    with pytest.raises(ValueError, match="before entry"):
        module.register("low-turnover", source, source, source, "2026-10-30T07:00:00+00:00", "2026-11-02T01:30:00+00:00", datetime(2026, 11, 2, 2, tzinfo=timezone.utc))


def test_local_receipt_does_not_certify_external_time(tmp_path):
    source = tmp_path / "input.json"
    source.write_text("{}")
    receipt = module.register("low-turnover", source, source, source, "2026-10-30T07:00:00+00:00", "2026-11-02T01:30:00+00:00", datetime(2026, 10, 30, 10, tzinfo=timezone.utc))
    assert receipt["status"] == "pending_external_time_proof"
    assert receipt["admitted"] is False
    assert receipt["completed_windows"] == 0
    assert receipt["inputs_sha256"] == "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
    assert str(tmp_path) not in str(receipt)


def test_formation_in_future_cannot_be_registered_as_ready(tmp_path):
    source = tmp_path / "input.json"
    source.write_text("{}")
    with pytest.raises(ValueError, match="after formation"):
        module.register("valuation", source, source, source, "2026-11-30T07:00:00+00:00", "2026-12-01T01:30:00+00:00", datetime(2026, 10, 22, tzinfo=timezone.utc))


def test_existing_receipt_is_never_overwritten(tmp_path):
    output = tmp_path / "receipt.json"
    output.write_text("original")
    with pytest.raises(FileExistsError):
        module.write_receipt(output, {"status": "pending"})
    assert output.read_text() == "original"
