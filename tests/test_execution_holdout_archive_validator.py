from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts/validate_execution_holdout_archive.py"
SPEC = importlib.util.spec_from_file_location("validate_execution_holdout_archive", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


PRE_ARTIFACTS = [
    "candidate_universe",
    "targets",
    "input_manifest",
    "announcement_st_evidence",
    "minute_data_manifest",
    "engine_config_fingerprint",
]
POST_ARTIFACTS = ["cash_holdings_orders_fills_valuation_ledgers"]


def _iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _expected_sessions(count: int = 252) -> list[dict[str, str]]:
    result = []
    day = date(2026, 1, 1)
    while len(result) < count:
        if day.weekday() < 5:
            decision_at = datetime.combine(
                day - timedelta(days=1), time(20, 2), timezone(timedelta(hours=8))
            )
            open_at = datetime.combine(day, time(9), timezone(timedelta(hours=8)))
            result.append(
                {
                    "session_date": day.isoformat(),
                    "decision_at_utc": _iso_utc(decision_at),
                    "session_open_utc": _iso_utc(open_at),
                    "entry_cutoff_utc": _iso_utc(open_at + timedelta(minutes=32)),
                    "closeout_not_before_utc": _iso_utc(
                        datetime.combine(day, time(15, 1), timezone(timedelta(hours=8)))
                    ),
                }
            )
        day += timedelta(days=1)
    return result


def _write_json(path: Path, value: object) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.write_bytes(data)
    return data


def _write_artifacts(session_dir: Path, phase: str) -> dict[str, dict[str, object]]:
    names = PRE_ARTIFACTS if phase == "pre_session" else POST_ARTIFACTS
    result = {}
    for name in names:
        relative = f"artifacts/{name}.bin"
        path = session_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        # The validator may hash this ledger-shaped payload but must never parse or print it.
        payload = b'{"nav":123.4,"return":0.56}' if name in POST_ARTIFACTS else name.encode()
        path.write_bytes(payload)
        result[name] = {
            "path": relative,
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    return result


def _write_receipt(
    root: Path,
    registration_sha256: str,
    session: dict[str, str],
    phase: str,
    *,
    captured_at_utc: str | None = None,
    artifact_changes: dict[str, dict[str, object]] | None = None,
    extra: dict[str, object] | None = None,
) -> Path:
    session_dir = root / "sessions" / session["session_date"]
    artifacts = _write_artifacts(session_dir, phase)
    if artifact_changes:
        artifacts.update(artifact_changes)
    if phase == "pre_session":
        decision = datetime.fromisoformat(session["decision_at_utc"].replace("Z", "+00:00"))
        captured_at_utc = captured_at_utc or _iso_utc(decision + timedelta(minutes=3))
    else:
        captured_at_utc = captured_at_utc or session["closeout_not_before_utc"]
    receipt = {
        "schema_version": "execution-validation-holdout-session-receipt.v1",
        "cohort_id": "execution-validation-20260101-v2",
        "session_date": session["session_date"],
        "capture_phase": phase,
        "captured_at_utc": captured_at_utc,
        "registration_sha256": registration_sha256,
        "status": "complete",
        "missing_artifacts": [],
        "artifacts": artifacts,
    }
    if extra:
        receipt.update(extra)
    path = session_dir / f"{phase}.json"
    _write_json(path, receipt)
    return path


def _build_cohort(tmp_path: Path, sessions_to_capture: int = 1) -> tuple[Path, list[dict[str, str]]]:
    root = tmp_path / "synthetic-cohort"
    schedule = _expected_sessions()
    protocol = b'{"schema":"synthetic-holdout.v2","do_not_evaluate":true}\n'
    (root / "protocol.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "protocol.json").write_bytes(protocol)
    calendar_bytes = _write_json(
        root / "session-calendar.json",
        {
            "schema_version": "execution-validation-session-calendar.v1",
            "source": "synthetic-test-calendar",
            "session_dates": [item["session_date"] for item in schedule],
        },
    )
    registration = {
        "schema_version": "execution-validation-holdout-registration.v1",
        "cohort_id": "execution-validation-20260101-v2",
        "registered_at_utc": "2025-12-31T12:00:00Z",
        "first_session_date": schedule[0]["session_date"],
        "duration_trade_sessions": 252,
        "session_calendar_source": "synthetic-test-calendar",
        "session_calendar_sha256": hashlib.sha256(calendar_bytes).hexdigest(),
        "code_commit": "b" * 40,
        "code_fingerprints": {"execution_engine": "c" * 64},
        "source_fingerprints": {"daily_panel_manifest": "d" * 64},
        "expected_sessions": schedule,
        "required_artifacts": {
            "pre_session": PRE_ARTIFACTS,
            "post_session": POST_ARTIFACTS,
        },
        "protocol_sha256": hashlib.sha256(protocol).hexdigest(),
    }
    registration_bytes = _write_json(root / "registration.json", registration)
    registration_sha256 = hashlib.sha256(registration_bytes).hexdigest()
    for session in schedule[:sessions_to_capture]:
        _write_receipt(root, registration_sha256, session, "pre_session")
        _write_receipt(root, registration_sha256, session, "post_session")
    return root, schedule


def test_valid_synthetic_receipts_validate_without_exposing_ledger_values(tmp_path, capsys):
    root, schedule = _build_cohort(tmp_path)

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert report.ok
    assert report.sessions_checked == 1
    assert report.errors == ()
    assert "123.4" not in capsys.readouterr().out


def test_cli_synthetic_rehearsal_reports_only_completeness(tmp_path, capsys):
    root, schedule = _build_cohort(tmp_path)

    exit_code = validator.main(
        ["--root", str(root), "--through-session-date", schedule[0]["session_date"]]
    )
    output = capsys.readouterr()
    assert exit_code == 0
    assert "Archive complete" in output.out
    assert "123.4" not in output.out + output.err
    assert "return" not in output.out.lower() + output.err.lower()


def test_pre_session_receipt_after_entry_cutoff_is_rejected(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    receipt = root / "sessions" / schedule[0]["session_date"] / "pre_session.json"
    data = json.loads(receipt.read_text())
    data["captured_at_utc"] = schedule[0]["entry_cutoff_utc"]
    receipt.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("pre-session" in message.lower() and "time" in message.lower() for message in report.errors)


def test_pre_session_receipt_before_registered_decision_is_rejected(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    receipt = root / "sessions" / schedule[0]["session_date"] / "pre_session.json"
    data = json.loads(receipt.read_text())
    decision = datetime.fromisoformat(schedule[0]["decision_at_utc"].replace("Z", "+00:00"))
    data["captured_at_utc"] = _iso_utc(decision - timedelta(seconds=1))
    receipt.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("decision" in message.lower() for message in report.errors)


def test_missing_required_artifact_is_rejected(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    receipt = root / "sessions" / schedule[0]["session_date"] / "pre_session.json"
    data = json.loads(receipt.read_text())
    del data["artifacts"]["targets"]
    receipt.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("targets" in message for message in report.errors)


def test_artifact_hash_mismatch_is_rejected(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    artifact = root / "sessions" / schedule[0]["session_date"] / "artifacts/targets.bin"
    artifact.write_bytes(b"different bytes")

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("hash" in message.lower() for message in report.errors)


def test_path_escape_is_rejected_before_artifact_read(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    receipt = root / "sessions" / schedule[0]["session_date"] / "pre_session.json"
    data = json.loads(receipt.read_text())
    data["artifacts"]["targets"]["path"] = "../../outside.bin"
    receipt.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("path" in message.lower() for message in report.errors)


def test_symlink_escape_is_rejected(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    session_dir = root / "sessions" / schedule[0]["session_date"]
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside the session archive")
    link = session_dir / "artifacts/linked-targets.bin"
    link.symlink_to(outside)
    receipt = session_dir / "pre_session.json"
    data = json.loads(receipt.read_text())
    data["artifacts"]["targets"] = {
        "path": "artifacts/linked-targets.bin",
        "size_bytes": outside.stat().st_size,
        "sha256": hashlib.sha256(outside.read_bytes()).hexdigest(),
    }
    receipt.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("path" in message.lower() for message in report.errors)


def test_performance_fields_are_rejected_by_receipt_schema(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    receipt = root / "sessions" / schedule[0]["session_date"] / "post_session.json"
    data = json.loads(receipt.read_text())
    data["nav"] = 1.25
    receipt.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("schema" in message.lower() for message in report.errors)
    assert "nav" not in " ".join(report.errors).lower()


def test_registration_protocol_fingerprint_mismatch_is_rejected(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    (root / "protocol.json").write_text('{"schema":"changed"}\n')

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("protocol" in message.lower() and "hash" in message.lower() for message in report.errors)


def test_session_calendar_fingerprint_must_match_registered_dates(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    calendar = root / "session-calendar.json"
    data = json.loads(calendar.read_text())
    data["session_dates"][1], data["session_dates"][2] = (
        data["session_dates"][2],
        data["session_dates"][1],
    )
    calendar.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("calendar" in message.lower() for message in report.errors)


def test_performance_metric_cannot_be_registered_as_a_completeness_artifact(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    registration_path = root / "registration.json"
    registration = json.loads(registration_path.read_text())
    registration["required_artifacts"]["pre_session"][0] = "nav"
    registration_path.write_text(json.dumps(registration))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("required artifact names" in message for message in report.errors)


def test_registration_change_after_receipts_is_rejected_by_bound_fingerprint(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    registration_path = root / "registration.json"
    registration = json.loads(registration_path.read_text())
    registration["registered_at_utc"] = "2025-12-31T11:59:00Z"
    registration_path.write_text(json.dumps(registration))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("registration fingerprint" in message.lower() for message in report.errors)


def test_blocked_receipt_is_not_reported_as_complete(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    receipt = root / "sessions" / schedule[0]["session_date"] / "pre_session.json"
    data = json.loads(receipt.read_text())
    del data["artifacts"]["targets"]
    data["status"] = "blocked"
    data["missing_artifacts"] = ["targets"]
    receipt.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("explicitly blocked" in message for message in report.errors)


def test_incomplete_date_sequence_through_requested_session_is_rejected(tmp_path):
    root, schedule = _build_cohort(tmp_path, sessions_to_capture=2)
    missing = root / "sessions" / schedule[1]["session_date"] / "pre_session.json"
    missing.unlink()

    report = validator.validate_archive(root, schedule[1]["session_date"])
    assert not report.ok
    assert any(schedule[1]["session_date"] in message for message in report.errors)


def test_receipt_timeline_cannot_overlap_the_next_session_decision(tmp_path):
    root, schedule = _build_cohort(tmp_path, sessions_to_capture=2)
    first_post = root / "sessions" / schedule[0]["session_date"] / "post_session.json"
    data = json.loads(first_post.read_text())
    next_decision = datetime.fromisoformat(schedule[1]["decision_at_utc"].replace("Z", "+00:00"))
    data["captured_at_utc"] = _iso_utc(next_decision + timedelta(minutes=4))
    first_post.write_text(json.dumps(data))

    report = validator.validate_archive(root, schedule[1]["session_date"])
    assert not report.ok
    assert any("sequence" in message.lower() for message in report.errors)


def test_registration_schedule_must_be_strictly_increasing(tmp_path):
    root, schedule = _build_cohort(tmp_path)
    registration_path = root / "registration.json"
    registration = json.loads(registration_path.read_text())
    registration["expected_sessions"][1], registration["expected_sessions"][2] = (
        registration["expected_sessions"][2],
        registration["expected_sessions"][1],
    )
    registration_path.write_text(json.dumps(registration))

    report = validator.validate_archive(root, schedule[0]["session_date"])
    assert not report.ok
    assert any("schedule" in message.lower() for message in report.errors)


def test_schemas_are_strict_and_reject_unregistered_performance_properties():
    registration_schema = json.loads(validator.REGISTRATION_SCHEMA.read_text())
    receipt_schema = json.loads(validator.RECEIPT_SCHEMA.read_text())
    calendar_schema = json.loads(validator.CALENDAR_SCHEMA.read_text())

    assert registration_schema["additionalProperties"] is False
    assert receipt_schema["additionalProperties"] is False
    assert calendar_schema["additionalProperties"] is False
    assert set(registration_schema["properties"]) == validator.REGISTRATION_FIELDS
    assert set(receipt_schema["properties"]) == validator.RECEIPT_FIELDS
    assert registration_schema["properties"]["expected_sessions"]["minItems"] == 252
    assert registration_schema["properties"]["expected_sessions"]["maxItems"] == 252
    assert calendar_schema["properties"]["session_dates"]["minItems"] == 252
    assert calendar_schema["properties"]["session_dates"]["maxItems"] == 252
    registered_artifact_names = registration_schema["properties"]["required_artifacts"]
    assert "nav" not in registered_artifact_names["properties"]["pre_session"]["items"]["enum"]
    assert "nav" not in receipt_schema["properties"]["artifacts"]["propertyNames"]["enum"]
    assert {"code_commit", "code_fingerprints", "source_fingerprints"} <= set(
        registration_schema["properties"]
    )
    assert "nav" not in receipt_schema["properties"]
    assert "return" not in receipt_schema["properties"]
