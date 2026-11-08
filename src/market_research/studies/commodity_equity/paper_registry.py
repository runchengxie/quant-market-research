"""Immutable protocol registration before future paper observations exist."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


def register_paper(
    protocol: dict, calendar: pd.DatetimeIndex, registered_at: pd.Timestamp, output: Path
) -> dict:
    if registered_at.tzinfo is None or calendar.has_duplicates or calendar.hasnans:
        raise ValueError("explicit registration timezone and unique calendar required")
    first = pd.Timestamp(protocol["first_eligible_session"])
    today = registered_at.tz_convert("Asia/Shanghai").normalize().tz_localize(None)
    if first <= today or first not in calendar or not calendar.is_monotonic_increasing:
        raise ValueError("paper observation must begin on a verified future session")
    if protocol["real_orders"] is not False or protocol["initial_capital_CNY"] <= 0:
        raise ValueError("positive paper capital and no real orders required")
    raw = (json.dumps(protocol, sort_keys=True, separators=(",", ":")) + "\n").encode()
    receipt = {
        "schema_version": 1,
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": hashlib.sha256(raw).hexdigest(),
        "registered_at": registered_at.isoformat(),
        "first_eligible_session": str(first.date()),
        "completed_forward_windows": 0,
        "observed_trades": 0,
        "real_orders": False,
        "status": "registered_before_first_session",
    }
    # Refuse overwrite before doing any writes.
    output.mkdir(parents=True, exist_ok=False)
    (output / "protocol.json").write_bytes(raw)
    (output / "registration.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt
