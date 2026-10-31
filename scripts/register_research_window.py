"""Create a non-overwriting local research receipt; never certify independent time."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def timestamp(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamps require an explicit timezone")
    return result.astimezone(timezone.utc)


def register(study: str, protocol: Path, inputs: Path, calendar: Path,
             formation_at: str, entry_at: str, now: datetime) -> dict:
    if study not in {"low-turnover", "valuation", "asset-allocation"}:
        raise ValueError("unknown research study")
    if now.tzinfo is None:
        raise ValueError("recording time requires a timezone")
    formation, entry = timestamp(formation_at), timestamp(entry_at)
    now = now.astimezone(timezone.utc)
    if formation >= entry or now >= entry:
        raise ValueError("registration must be before entry")
    if now < formation:
        raise ValueError("registration must be after formation inputs are available")
    minimum = (datetime(2026, 11, 30, 7, tzinfo=timezone.utc) if study == "asset-allocation"
               else datetime(2026, 11 if study == "valuation" else 10, 1, tzinfo=timezone.utc))
    if formation < minimum:
        raise ValueError("formation predates the new cohort")
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "schema_version": 1, "study": study,
        "recorded_at_utc": now.isoformat(), "clock_evidence": "local_clock_only",
        "formation_at_utc": formation.isoformat(), "entry_at_utc": entry.isoformat(),
        "protocol_sha256": digest(protocol), "inputs_sha256": digest(inputs),
        "calendar_sha256": digest(calendar), "status": "pending_external_time_proof",
        "admitted": False, "completed_windows": 0,
    }


def write_receipt(output: Path, receipt: dict) -> None:
    # Exclusive creation preserves previous registrations even if called twice.
    with output.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True, choices=["low-turnover", "valuation", "asset-allocation"])
    for name in ("protocol", "inputs", "calendar", "output"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    parser.add_argument("--formation-at", required=True)
    parser.add_argument("--entry-at", required=True)
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[1]
    if args.output.resolve().is_relative_to(repository):
        parser.error("receipts belong in the external research data directory")
    receipt = register(args.study, args.protocol, args.inputs, args.calendar,
                       args.formation_at, args.entry_at, datetime.now(timezone.utc))
    write_receipt(args.output, receipt)
    print("Local receipt written. External time proof and admission review remain pending.")


if __name__ == "__main__":
    main()
