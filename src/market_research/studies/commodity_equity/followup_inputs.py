"""Hash-bound task exports and conservative release-event reconstruction."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from .inputs import _read_hashed


def read_exports(sources: list[dict]) -> tuple[dict, list]:
    frames, receipts = {}, []
    for source in sources:
        path = Path(source["receipt_path"])
        rows = json.loads(_read_hashed(path, source["receipt_sha256"]))
        for row in rows:
            receipts.append(
                {k: row.get(k) for k in ["id", "api", "code", "rows", "sha256", "params", "status"]}
            )
            if not row.get("sha256"):
                continue
            payload = json.loads(_read_hashed(path.parent / (row["id"] + ".json"), row["sha256"]))
            if payload.get("code") != 0:
                continue
            body = payload.get("data") or {}
            frame = pd.DataFrame(body.get("items") or [], columns=body.get("fields") or [])
            if len(frame) != row["rows"]:
                raise ValueError("export receipt row count mismatch")
            if row["api"] == "eco_cal" and len(frame) >= 100:
                raise ValueError("economic calendar response may be capped")
            code = row["params"].get("ts_code")
            if (
                code
                and not frame.empty
                and ("ts_code" not in frame or not frame.ts_code.eq(code).all())
            ):
                raise ValueError("fund/source identity mismatch")
            key = (row["api"], code)
            frames.setdefault(key, []).append(frame)
    return {key: pd.concat(parts, ignore_index=True) for key, parts in frames.items()}, receipts


def event_records(events: pd.DataFrame) -> pd.DataFrame:
    """Publication dates do not authenticate the value's historical vintage.

    Economic-calendar clock timezone is not certified. Admit reconstructed
    events on the following full local calendar day, never intraday.
    """
    selected = []
    for row in events.to_dict("records"):
        event = str(row.get("event", ""))
        if event.startswith("中国官方制造业PMI"):
            series = "pmi"
        elif event.startswith("中国PPI年率"):
            series = "ppi"
        else:
            continue
        if row.get("country") != "中国":
            raise ValueError("macro event country mismatch")
        raw = str(row.get("value", "")).strip().replace("%", "")
        if not re.fullmatch(r"[+-]?\d+(\.\d+)?", raw):
            continue
        date = pd.to_datetime(str(row["date"]), format="%Y%m%d")
        selected.append(
            {
                "series": series,
                "available_at": (date + pd.Timedelta(days=1)).isoformat(),
                "value": float(raw),
                "vintage_verified": False,
                "source": "economic_calendar_observed_now",
                "event": event,
            }
        )
    return pd.DataFrame(
        selected, columns=["series", "available_at", "value", "vintage_verified", "source", "event"]
    )
