"""Seal a fixed SPX direction baseline from fresh MDP receipt evidence."""
import argparse
import csv
import hashlib
import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SIGNAL = "spx-last-session-direction-csi300-open-next-open-v1"


def read_verified(run, record):
    if record["status"] != "ok":
        raise ValueError("Source request did not succeed")
    content = (run / record["file"]).read_bytes()
    if hashlib.sha256(content).hexdigest() != record["sha256"]:
        raise ValueError("Receipt content hash mismatch")
    return list(csv.DictReader(content.decode().splitlines()))


def seal_forecast(run: Path, output: Path) -> Path:
    receipt_bytes = (run / "receipt.json").read_bytes()
    receipt = json.loads(receipt_bytes)
    cutoff = datetime.fromisoformat(receipt["cutoff_utc"])
    reasons = []
    if receipt["protocol"] != "overseas-receipt-v1":
        raise ValueError("Unsupported receipt protocol")
    if not receipt["timely_capture"]:
        reasons.append("capture_outside_frozen_window")
    prediction = None
    selected = []
    try:
        calendar = read_verified(run, receipt["sources"]["calendar"])
        if (len(calendar) != 1 or calendar[0]["is_open"] != "1"
                or calendar[0]["cal_date"] != receipt["target_date"]):
            reasons.append("target_session_not_confirmed_open")
        rows = read_verified(run, receipt["sources"]["spx"])
        expected = cutoff.astimezone(ZoneInfo("America/New_York")).date()
        while expected.weekday() > 4:
            expected -= timedelta(days=1)
        usable = []
        seen = set()
        for row in rows:
            date = row["trade_date"]
            if date in seen:
                raise ValueError("Duplicate SPX dates")
            seen.add(date)
            close = datetime.fromisoformat(
                receipt["sources"]["spx"]["assumed_regular_close_utc"][date])
            price = float(row["close"])
            if not math.isfinite(price) or price <= 0:
                raise ValueError("Invalid SPX price")
            if close + timedelta(hours=1) <= cutoff:
                usable.append((date, price))
        usable.sort()
        selected = usable[-2:]
        if len(selected) != 2 or selected[-1][0] != expected.strftime("%Y%m%d"):
            reasons.append("expected_spx_weekday_missing")
        elif (datetime.strptime(selected[-1][0], "%Y%m%d")
              - datetime.strptime(selected[-2][0], "%Y%m%d")).days > 7:
            reasons.append("prior_spx_bar_stale")
        else:
            move = selected[-1][1] / selected[-2][1] - 1
            prediction = {"spx_return": move, "direction": (move > 0) - (move < 0)}
    except (KeyError, ValueError, OSError):
        reasons.append("missing_or_invalid_input")
    payload = {
        "signal_id": SIGNAL, "target": "CSI300 today open to next SSE session open direction",
        "model": "fixed sign of SPX last completed session close return; no fitting",
        "protocol": "overseas-forward-v1", "target_date": receipt["target_date"],
        "cutoff_utc": receipt["cutoff_utc"],
        "receipt_path": str(run.resolve()),
        "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "exclusion_reasons": reasons,
        "prediction": prediction, "selected_spx_bars": selected,
    }
    category = "signals" if receipt["mode"] == "scheduled" else "probes"
    output = output / category
    output.mkdir(parents=True, exist_ok=True)
    name = receipt["target_date"] if category == "signals" else run.name
    # Persist the prediction before observing its actual completed write time.
    # The manifest is the authoritative qualification record; the payload is immutable.
    payload_path = output / (name + ".prediction.json")
    content = (json.dumps(payload, indent=2, allow_nan=False) + "\n").encode()
    with payload_path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    sealed_at = datetime.now(ZoneInfo("UTC"))
    if sealed_at > cutoff:
        reasons.append("prediction_sealed_after_cutoff")
    payload.update(sealed_utc=sealed_at.isoformat(), eligible=not reasons,
                   prediction_file=payload_path.name,
                   prediction_sha256=hashlib.sha256(content).hexdigest())
    path = output / (name + ".json")
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt-directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(seal_forecast(args.receipt_directory, args.output))


if __name__ == "__main__":
    main()
