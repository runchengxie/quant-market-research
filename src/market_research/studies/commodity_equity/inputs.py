"""Validate frozen supplier receipts, series identity and calendar completeness."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _read_hashed(path: Path, expected: str) -> bytes:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("frozen input hash mismatch")
    return raw


def read_bundle(path: Path) -> tuple[dict, dict, list]:
    manifest = json.loads(path.read_text())
    if manifest.get("schema_version") != 1:
        raise ValueError("bundle schema_version must be 1")
    frames, calendars, receipts = {}, {}, []
    for source in manifest["sources"]:
        receipt_path = Path(source["receipt_path"])
        if not receipt_path.is_absolute():
            receipt_path = path.parent / receipt_path
        rows = json.loads(_read_hashed(receipt_path, source["receipt_sha256"]))
        ids = source["ids"]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate selected receipt identity")
        selected = [row for row in rows if row["id"] in ids]
        if len(selected) != len(ids):
            raise ValueError("missing or duplicate receipt identity")
        for row in selected:
            receipts.append(
                {
                    k: row.get(k)
                    for k in [
                        "id",
                        "api",
                        "params",
                        "code",
                        "rows",
                        "sha256",
                        "observed_at",
                        "status",
                    ]
                }
            )
            if not row.get("sha256"):
                continue
            raw = _read_hashed(receipt_path.parent / (row["id"] + ".json"), row["sha256"])
            payload = json.loads(raw)
            if payload.get("code") != 0:
                continue
            body = payload.get("data") or {}
            data = pd.DataFrame(body.get("items") or [], columns=body.get("fields") or [])
            if len(data) != row["rows"]:
                raise ValueError("receipt row count mismatch")
            if data.empty:
                continue
            if row["api"] == "trade_cal":
                exchange = row["params"]["exchange"]
                if not data.exchange.eq(exchange).all() or not data.is_open.eq(1).all():
                    raise ValueError("calendar identity or open-session mismatch")
                dates = pd.to_datetime(data.cal_date, format="%Y%m%d", errors="raise")
                if dates.isna().any() or dates.duplicated().any():
                    raise ValueError("invalid calendar dates")
                calendars.setdefault(exchange, []).extend(dates.tolist())
                continue
            if row["api"] not in {"index_daily", "fut_index_daily"}:
                raise ValueError("unsupported frozen endpoint")
            code = row["params"]["ts_code"]
            if code not in manifest["series"] or not data.ts_code.eq(code).all():
                raise ValueError("series identity mismatch")
            dates = pd.to_datetime(data.trade_date, format="%Y%m%d", errors="raise")
            values = pd.to_numeric(data.close, errors="raise")
            if dates.isna().any() or dates.duplicated().any():
                raise ValueError("duplicate or missing quote dates")
            if not np.isfinite(values).all() or (values <= 0).any():
                raise ValueError("levels must be finite and positive")
            frame = pd.Series(values.to_numpy(), index=dates, name=code).sort_index()
            frames.setdefault(code, []).append(frame)
    series = {}
    for code, parts in frames.items():
        combined = pd.concat(parts).sort_index()
        if combined.index.duplicated().any():
            raise ValueError("duplicate dates across frozen quote batches")
        series[code] = combined
    return (
        series,
        {k: pd.DatetimeIndex(v).drop_duplicates().sort_values() for k, v in calendars.items()},
        receipts,
    )


def audit_pair(
    equity: pd.Series,
    commodity: pd.Series,
    equity_calendar: pd.DatetimeIndex,
    commodity_calendar: pd.DatetimeIndex,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> tuple[dict, pd.DataFrame | None]:
    start = max(start, equity.index.min(), commodity.index.min())
    end = min(end, equity.index.max(), commodity.index.max())
    eq = equity_calendar[(equity_calendar >= start) & (equity_calendar <= end)]
    co = commodity_calendar[(commodity_calendar >= start) & (commodity_calendar <= end)]
    common = eq.intersection(co)

    def iso(dates):
        return [d.date().isoformat() for d in dates]

    eq_missing, co_missing = eq.difference(equity.index), co.difference(commodity.index)
    eq_extra = equity.loc[start:end].index.difference(eq)
    co_extra = commodity.loc[start:end].index.difference(co)
    eligible = (
        len(common) >= 2
        and not len(eq_missing)
        and not len(co_missing)
        and not len(eq_extra)
        and not len(co_extra)
    )
    audit = {
        "eligible": bool(eligible),
        "start": str(start.date()),
        "end": str(end.date()),
        "equity_missing": iso(eq_missing),
        "commodity_missing": iso(co_missing),
        "equity_off_calendar": iso(eq_extra),
        "commodity_off_calendar": iso(co_extra),
        "equity_only_sessions": iso(eq.difference(co)),
        "commodity_only_sessions": iso(co.difference(eq)),
        "common_sessions": len(common),
    }
    aligned = (
        pd.DataFrame({"equity": equity.reindex(common), "commodity": commodity.reindex(common)})
        if eligible
        else None
    )
    return audit, aligned
