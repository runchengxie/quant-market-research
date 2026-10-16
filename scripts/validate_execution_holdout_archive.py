"""Validate prospective holdout archive completeness without reading ledger contents."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION_SCHEMA = (
    ROOT / "docs/schemas/execution-validation-holdout-registration.v1.schema.json"
)
RECEIPT_SCHEMA = ROOT / "docs/schemas/execution-validation-holdout-session-receipt.v1.schema.json"
CALENDAR_SCHEMA = ROOT / "docs/schemas/execution-validation-session-calendar.v1.schema.json"
REGISTRATION_VERSION = "execution-validation-holdout-registration.v1"
RECEIPT_VERSION = "execution-validation-holdout-session-receipt.v1"
CALENDAR_VERSION = "execution-validation-session-calendar.v1"
REGISTRATION_FIELDS = {
    "schema_version",
    "cohort_id",
    "registered_at_utc",
    "first_session_date",
    "duration_trade_sessions",
    "session_calendar_source",
    "session_calendar_sha256",
    "code_commit",
    "code_fingerprints",
    "source_fingerprints",
    "expected_sessions",
    "required_artifacts",
    "protocol_sha256",
}
SCHEDULE_FIELDS = {
    "session_date",
    "decision_at_utc",
    "session_open_utc",
    "entry_cutoff_utc",
    "closeout_not_before_utc",
}
RECEIPT_FIELDS = {
    "schema_version",
    "cohort_id",
    "session_date",
    "capture_phase",
    "captured_at_utc",
    "registration_sha256",
    "status",
    "missing_artifacts",
    "artifacts",
}
ARTIFACT_FIELDS = {"path", "size_bytes", "sha256"}
CALENDAR_FIELDS = {"schema_version", "source", "session_dates"}
PRE_SESSION_ARTIFACTS = {
    "candidate_universe",
    "targets",
    "input_manifest",
    "announcement_st_evidence",
    "minute_data_manifest",
    "engine_config_fingerprint",
}
POST_SESSION_ARTIFACTS = {"cash_holdings_orders_fills_valuation_ledgers"}
NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
COHORT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,79}$")


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    sessions_checked: int
    errors: tuple[str, ...]


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(HASH_RE.fullmatch(value))


def _is_fingerprint_map(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and bool(value)
        and all(
            isinstance(name, str) and NAME_RE.fullmatch(name) and _is_sha256(digest)
            for name, digest in value.items()
        )
    )


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        return None
    return parsed.astimezone(timezone.utc)


def _read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        raw = path.read_bytes()
    except OSError:
        return None, "file is missing or unreadable"
    try:
        return json.loads(raw), None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "file is not valid JSON"


def _hash_file(path: Path) -> tuple[str | None, int | None]:
    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
    except OSError:
        return None, None
    return digest.hexdigest(), size


def _validate_registration(data: Any) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    if not isinstance(data, dict) or set(data) != REGISTRATION_FIELDS:
        return ["registration does not match the registered schema"], []
    if data["schema_version"] != REGISTRATION_VERSION:
        errors.append("registration schema version is unsupported")
    if not isinstance(data["cohort_id"], str) or not COHORT_RE.fullmatch(data["cohort_id"]):
        errors.append("registration cohort ID is invalid")
    registered_at = _parse_utc(data["registered_at_utc"])
    if registered_at is None:
        errors.append("registration timestamp must be an ISO-8601 UTC timestamp")
    if data["duration_trade_sessions"] != 252 or isinstance(data["duration_trade_sessions"], bool):
        errors.append("registration duration must be exactly 252 sessions")
    if not isinstance(data["session_calendar_source"], str) or not data["session_calendar_source"].strip():
        errors.append("registration calendar source is missing")
    if not _is_sha256(data["session_calendar_sha256"]):
        errors.append("registration calendar fingerprint is invalid")
    if not _is_sha256(data["protocol_sha256"]):
        errors.append("registration protocol fingerprint is invalid")
    if not isinstance(data["code_commit"], str) or not re.fullmatch(r"[0-9a-f]{40,64}", data["code_commit"]):
        errors.append("registration code commit is invalid")
    if not _is_fingerprint_map(data["code_fingerprints"]):
        errors.append("registration code fingerprints are invalid")
    if not _is_fingerprint_map(data["source_fingerprints"]):
        errors.append("registration source fingerprints are invalid")
    schedule = data["expected_sessions"]
    if not isinstance(schedule, list) or len(schedule) != 252:
        errors.append("registration must contain exactly 252 expected sessions")
        schedule = []
    parsed_dates: list[date] = []
    parsed_times: list[tuple[datetime, datetime, datetime, datetime]] = []
    for item in schedule:
        if not isinstance(item, dict) or set(item) != SCHEDULE_FIELDS:
            errors.append("registration session schedule does not match the schema")
            continue
        session_day = _parse_date(item["session_date"])
        decision_at = _parse_utc(item["decision_at_utc"])
        opened = _parse_utc(item["session_open_utc"])
        entry_cutoff = _parse_utc(item["entry_cutoff_utc"])
        closeout = _parse_utc(item["closeout_not_before_utc"])
        if (
            session_day is None
            or decision_at is None
            or opened is None
            or entry_cutoff is None
            or closeout is None
        ):
            errors.append("registration session date or UTC time is invalid")
            continue
        if opened.date() != session_day:
            errors.append("registered session open does not fall on its session date in UTC")
        if not decision_at < opened < entry_cutoff < closeout or closeout.date() != session_day:
            errors.append("registered session times are not strictly ordered")
        parsed_dates.append(session_day)
        parsed_times.append((decision_at, opened, entry_cutoff, closeout))
    if len(parsed_times) == 252 and any(
        previous[3] >= current[0] for previous, current in zip(parsed_times, parsed_times[1:])
    ):
        errors.append("registered session decision times do not follow prior closeout")
    if len(parsed_dates) == 252 and any(a >= b for a, b in zip(parsed_dates, parsed_dates[1:])):
        errors.append("registered session schedule is not strictly increasing")
    first_date = _parse_date(data["first_session_date"])
    if not parsed_dates or first_date is None or first_date != parsed_dates[0]:
        errors.append("registration first session does not match its schedule")
    if registered_at is not None and parsed_times and registered_at >= parsed_times[0][0]:
        errors.append("registration was not recorded before the first decision time")
    requirements = data["required_artifacts"]
    if not isinstance(requirements, dict) or set(requirements) != {"pre_session", "post_session"}:
        errors.append("required artifact groups do not match the schema")
    else:
        expected_by_phase = {
            "pre_session": PRE_SESSION_ARTIFACTS,
            "post_session": POST_SESSION_ARTIFACTS,
        }
        for phase, names in requirements.items():
            valid_names = isinstance(names, list) and all(isinstance(name, str) for name in names)
            if (
                not valid_names
                or len(set(names)) != len(names)
                or set(names) != expected_by_phase[phase]
            ):
                errors.append(f"required artifact names are invalid for {phase}")
    return errors, schedule


def _safe_artifact_path(session_dir: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        return None
    posix = PurePosixPath(relative)
    if posix.is_absolute() or any(part in {"", ".", ".."} for part in posix.parts):
        return None
    candidate = session_dir.joinpath(*posix.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(session_dir.resolve(strict=True))
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def _safe_archive_file(root: Path, relative: str) -> Path | None:
    candidate = root / relative
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def _validate_receipt(
    receipt_path: Path,
    *,
    root: Path,
    schedule_item: dict[str, Any],
    phase: str,
    cohort_id: str,
    registration_sha256: str,
    registered_at: datetime,
    required_artifacts: list[str],
) -> tuple[list[str], datetime | None]:
    errors: list[str] = []
    data, read_error = _read_json(receipt_path)
    session_date = schedule_item["session_date"]
    if read_error:
        return [f"{session_date}: {phase} receipt {read_error}"], None
    if not isinstance(data, dict) or set(data) != RECEIPT_FIELDS:
        return [f"{session_date}: {phase} receipt does not match the strict schema"], None
    if data["schema_version"] != RECEIPT_VERSION:
        errors.append(f"{session_date}: {phase} receipt schema version is unsupported")
    if data["cohort_id"] != cohort_id or data["session_date"] != session_date:
        errors.append(f"{session_date}: {phase} receipt is bound to a different cohort or date")
    if data["capture_phase"] != phase:
        errors.append(f"{session_date}: receipt phase does not match its file")
    if data["registration_sha256"] != registration_sha256:
        errors.append(f"{session_date}: {phase} receipt registration fingerprint does not match")
    captured_at = _parse_utc(data["captured_at_utc"])
    if captured_at is None:
        errors.append(f"{session_date}: {phase} receipt timestamp must be UTC")
    elif phase == "pre_session":
        decision_at = _parse_utc(schedule_item["decision_at_utc"])
        if captured_at < decision_at or captured_at >= _parse_utc(schedule_item["entry_cutoff_utc"]):
            errors.append(
                f"{session_date}: pre-session receipt time is before decision or after entry cutoff"
            )
    elif captured_at < _parse_utc(schedule_item["closeout_not_before_utc"]):
        errors.append(f"{session_date}: post-session receipt time is before closeout")

    status = data["status"]
    missing = data["missing_artifacts"]
    artifacts = data["artifacts"]
    if not isinstance(status, str) or status not in {"complete", "blocked"}:
        errors.append(f"{session_date}: {phase} receipt status is invalid")
    if not isinstance(missing, list) or any(
        not isinstance(name, str) or name not in required_artifacts for name in missing
    ) or len(set(missing)) != len(missing):
        errors.append(f"{session_date}: {phase} receipt missing-artifact list is invalid")
        missing = []
    if not isinstance(artifacts, dict) or any(name not in required_artifacts for name in artifacts):
        errors.append(f"{session_date}: {phase} receipt artifact map is invalid")
        artifacts = {}
    absent = set(required_artifacts) - set(artifacts)
    if status == "complete" and (missing or absent):
        absent_names = ", ".join(sorted(set(missing) | absent))
        errors.append(f"{session_date}: {phase} receipt claims complete with missing artifacts: {absent_names}")
    if status == "blocked":
        if not missing and not absent:
            errors.append(f"{session_date}: {phase} receipt is blocked without a missing artifact")
        else:
            errors.append(f"{session_date}: {phase} receipt is explicitly blocked")
    if not absent.issubset(set(missing)):
        errors.append(f"{session_date}: {phase} receipt omits required missing-artifact names")

    session_dir = root / "sessions" / session_date
    for name, artifact in artifacts.items():
        if not isinstance(artifact, dict) or set(artifact) != ARTIFACT_FIELDS:
            errors.append(f"{session_date}: {phase} artifact metadata does not match the schema")
            continue
        relative_path = artifact["path"]
        if not isinstance(artifact["size_bytes"], int) or isinstance(artifact["size_bytes"], bool) or artifact["size_bytes"] < 0:
            errors.append(f"{session_date}: {phase} artifact size is invalid")
            continue
        if not _is_sha256(artifact["sha256"]):
            errors.append(f"{session_date}: {phase} artifact fingerprint is invalid")
            continue
        path = _safe_artifact_path(session_dir, relative_path)
        if path is None:
            errors.append(f"{session_date}: {phase} artifact path is unsafe or unavailable")
            continue
        actual_sha256, actual_size = _hash_file(path)
        if actual_sha256 is None:
            errors.append(f"{session_date}: {phase} artifact could not be read for hashing")
        else:
            if actual_size != artifact["size_bytes"]:
                errors.append(f"{session_date}: {phase} artifact size does not match")
            if actual_sha256 != artifact["sha256"]:
                errors.append(f"{session_date}: {phase} artifact hash does not match")
    return errors, captured_at


def validate_archive(root: Path, through_session_date: str) -> ValidationReport:
    """Check registered archive metadata and file digests only; never parse artifact contents."""
    errors: list[str] = []
    try:
        archive_root = Path(root).resolve(strict=True)
    except OSError:
        return ValidationReport(False, 0, ("archive root is missing or unreadable",))
    registration_path = _safe_archive_file(archive_root, "registration.json")
    if registration_path is None:
        return ValidationReport(False, 0, ("registration is missing, unreadable or outside archive root",))
    registration_bytes, read_error = _read_json(registration_path)
    if read_error:
        return ValidationReport(False, 0, (f"registration {read_error}",))
    registration_hash, _ = _hash_file(registration_path)
    protocol_path = _safe_archive_file(archive_root, "protocol.json")
    calendar_path = _safe_archive_file(archive_root, "session-calendar.json")
    protocol_hash, _ = _hash_file(protocol_path) if protocol_path else (None, None)
    calendar_data, calendar_read_error = (
        _read_json(calendar_path) if calendar_path else (None, "file is missing or outside archive root")
    )
    calendar_hash_actual, _ = _hash_file(calendar_path) if calendar_path else (None, None)
    schema_errors, schedule = _validate_registration(registration_bytes)
    errors.extend(schema_errors)
    if errors:
        return ValidationReport(False, 0, tuple(errors))
    if protocol_hash != registration_bytes["protocol_sha256"]:
        return ValidationReport(False, 0, ("registered protocol hash does not match protocol.json",))
    if registration_hash is None:
        return ValidationReport(False, 0, ("registration cannot be fingerprinted",))
    calendar_hash = registration_bytes["session_calendar_sha256"]
    if not _is_sha256(calendar_hash):
        return ValidationReport(False, 0, ("registered session calendar hash is invalid",))
    if calendar_read_error or calendar_hash_actual != calendar_hash:
        return ValidationReport(False, 0, ("registered session calendar fingerprint does not match",))
    if (
        not isinstance(calendar_data, dict)
        or set(calendar_data) != CALENDAR_FIELDS
        or calendar_data["schema_version"] != CALENDAR_VERSION
        or calendar_data["source"] != registration_bytes["session_calendar_source"]
        or calendar_data["session_dates"] != [item["session_date"] for item in schedule]
    ):
        return ValidationReport(False, 0, ("session calendar does not match the registered schedule",))
    through = _parse_date(through_session_date)
    dates = [_parse_date(item["session_date"]) for item in schedule]
    if through is None or through not in dates:
        return ValidationReport(False, 0, ("requested through-date is not a registered session",))
    registered_at = _parse_utc(registration_bytes["registered_at_utc"])
    required = registration_bytes["required_artifacts"]
    cohort_id = registration_bytes["cohort_id"]
    checked = 0
    previous_post_session_at: datetime | None = None
    for item in schedule:
        if item["session_date"] > through.isoformat():
            break
        phase_times: dict[str, datetime | None] = {}
        for phase in ("pre_session", "post_session"):
            receipt_path = _safe_archive_file(
                archive_root, f"sessions/{item['session_date']}/{phase}.json"
            )
            if receipt_path is None:
                errors.append(f"{item['session_date']}: {phase} receipt is missing or outside archive root")
                phase_times[phase] = None
                continue
            receipt_errors, captured_at = _validate_receipt(
                receipt_path,
                root=archive_root,
                schedule_item=item,
                phase=phase,
                cohort_id=cohort_id,
                registration_sha256=registration_hash,
                registered_at=registered_at,
                required_artifacts=required[phase],
            )
            errors.extend(receipt_errors)
            phase_times[phase] = captured_at
        pre_time, post_time = phase_times["pre_session"], phase_times["post_session"]
        if pre_time is not None and post_time is not None and post_time <= pre_time:
            errors.append(f"{item['session_date']}: post-session receipt does not follow pre-session receipt")
        if (
            pre_time is not None
            and previous_post_session_at is not None
            and pre_time <= previous_post_session_at
        ):
            errors.append(f"{item['session_date']}: receipt sequence overlaps the prior session closeout")
        if post_time is not None:
            previous_post_session_at = post_time
        checked += 1
    return ValidationReport(not errors, checked, tuple(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check holdout registration, receipt completeness, timestamps, paths and SHA-256 only."
    )
    parser.add_argument("--root", required=True, type=Path, help="external cohort archive root")
    parser.add_argument("--through-session-date", required=True, help="registered session date (YYYY-MM-DD)")
    args = parser.parse_args(argv)
    report = validate_archive(args.root, args.through_session_date)
    if report.ok:
        print(f"Archive complete through requested session ({report.sessions_checked} sessions checked).")
        return 0
    for error in report.errors:
        print(f"INCOMPLETE: {error}", file=sys.stderr)
    print(f"Archive incomplete ({report.sessions_checked} sessions checked).", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
