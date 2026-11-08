"""Immutable protocol registration before future paper observations exist."""

from __future__ import annotations

import hashlib
import json
import math
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
    if (
        protocol["real_orders"] is not False
        or not math.isfinite(protocol["initial_capital_CNY"])
        or protocol["initial_capital_CNY"] <= 0
    ):
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


def append_observation(
    registry: Path,
    source_path: Path,
    source_sha256: str,
    calendar: pd.DatetimeIndex,
    recorded_at: pd.Timestamp,
) -> dict:
    """Append one normalized owner input, never backdate its actual visibility.

    The normalized owner input carries per-product gross daily growth computed
    within a single provider vintage, avoiding cross-vintage factor-scale jumps.
    This function does not acquire data, submit orders or authenticate a vendor.
    """
    registration = json.loads((registry / "registration.json").read_text())
    protocol_raw = (registry / "protocol.json").read_bytes()
    if hashlib.sha256(protocol_raw).hexdigest() != registration["protocol_sha256"]:
        raise ValueError("registered protocol hash mismatch")
    protocol = json.loads(protocol_raw)
    raw = source_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != source_sha256:
        raise ValueError("owner input hash mismatch")
    source = json.loads(raw)
    day = pd.Timestamp(source["trade_date"])
    available = pd.Timestamp(source["available_at"])
    if recorded_at.tzinfo is None or available.tzinfo is None or day.tzinfo is not None:
        raise ValueError("explicit observation timezone and naive session date required")
    cutoff = day.tz_localize("Asia/Shanghai") + pd.Timedelta(hours=15, minutes=5)
    if (
        calendar.has_duplicates
        or not calendar.is_monotonic_increasing
        or day not in calendar
        or day < pd.Timestamp(protocol["first_eligible_session"])
        or available < cutoff
        or recorded_at < available
        or recorded_at < pd.Timestamp(registration["registered_at"])
    ):
        raise ValueError("invalid paper date or availability")
    required = {protocol["stock_product"], protocol["commodity_product"]}
    growth = source["gross_growth"]
    if set(growth) != required or any(not math.isfinite(v) or v <= 0 for v in growth.values()):
        raise ValueError("positive finite growth for each registered product required")
    observations = registry / "observations"
    previous = sorted(observations.glob("*.json")) if observations.exists() else []
    if previous:
        prior = json.loads(previous[-1].read_text())
        if recorded_at < pd.Timestamp(prior["recorded_at"]):
            raise ValueError("appended observation cannot backdate recorded visibility")
        last = pd.Timestamp(previous[-1].stem)
        expected = calendar[calendar > last]
        if len(expected) == 0 or day != expected[0]:
            raise ValueError("observations must be consecutive without rewriting")
    elif day != pd.Timestamp(protocol["first_eligible_session"]) or any(
        v != 1 for v in growth.values()
    ):
        raise ValueError("first paper mark must start at one on the registered session")
    result = {
        "trade_date": str(day.date()),
        "available_at": available.isoformat(),
        "recorded_at": recorded_at.isoformat(),
        "owner_input_sha256": source_sha256,
        "protocol_sha256": registration["protocol_sha256"],
        "gross_growth": growth,
        "real_orders": False,
    }
    observations.mkdir(exist_ok=True)
    with (observations / (str(day.date()) + ".json")).open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
    return result
