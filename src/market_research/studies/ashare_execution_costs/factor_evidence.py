"""Source-bound explanations for raw-price execution factor alarms.

This does not change factors or entitlements, or establish supplier internals.
Default preparation still rejects every unexplained change without this evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from fractions import Fraction

import pandas as pd


def _same(left, right):
    return (
        math.isfinite(float(left))
        and math.isfinite(float(right))
        and math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-10)
    )


class _Sources:
    def __init__(self, root):
        self.root = root
        self.hashes = {}

    def path(self, reference):
        path = self.root / reference["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != reference["sha256"]:
            raise ValueError("factor evidence source hash mismatch")
        self.hashes[str(path)] = digest
        return path

    def json(self, reference):
        return json.loads(self.path(reference).read_text())


def _response(sources, receipt_path, query):
    path = sources.path(
        {"path": str(receipt_path.parent / query["file"]), "sha256": query["sha256"]}
    )
    value = json.loads(path.read_text())
    if query["error_code"] != "0" or value.get("error_code") != "0":
        raise ValueError("independent source query incomplete")
    fields = value["fields"]
    if len(fields) != len(set(fields)) or len(value["rows"]) != query["rows"]:
        raise ValueError("independent source response coverage mismatch")
    return pd.DataFrame(value["rows"], columns=fields)


def _check_independent(symbol, day, previous_day, marks, queries, sources, receipt_path):
    required = ("raw_daily", "back_adjusted_daily", "adjustment_events", "dividends")
    selected = [q for q in queries if q["symbol"] == symbol]
    if len(selected) != 4 or {q["kind"] for q in selected} != set(required):
        raise ValueError("independent source query coverage incomplete")
    by_kind = {q["kind"]: q for q in selected}
    code = symbol[-2:].lower() + "." + symbol[:6]
    start, end = marks.trade_date.min(), marks.trade_date.max()
    for kind in required:
        if by_kind[kind]["params"]["code"] != code:
            raise ValueError("independent source query symbol mismatch")
    query = by_kind["adjustment_events"]["params"]
    if query["start_date"].replace("-", "") > start or query["end_date"].replace("-", "") < end:
        raise ValueError("independent corporate query coverage incomplete")
    query = by_kind["dividends"]["params"]
    if start[:4] != end[:4] or query["year"] != start[:4] or query["yearType"] != "operate":
        raise ValueError("independent dividend query coverage incomplete")
    data = {kind: _response(sources, receipt_path, by_kind[kind]) for kind in required}
    for kind in ("adjustment_events", "dividends"):
        events = data[kind]
        if "dividOperateDate" not in events or "code" not in events:
            raise ValueError("independent economic event schema missing")
        if len(events) and (
            not events.dividOperateDate.astype("string")
            .str.fullmatch(r"\d{4}-\d{2}-\d{2}")
            .fillna(False)
            .all()
            or pd.to_datetime(events.dividOperateDate, errors="coerce").isna().any()
        ):
            raise ValueError("independent economic event dates are unknown")
        if len(events) and (
            events.code.ne(code).any()
            or events.dividOperateDate.isin([f"{day[:4]}-{day[4:6]}-{day[6:]}"]).any()
        ):
            raise ValueError("independent source reports economic event or wrong symbol")
    raw, adjusted = data["raw_daily"].copy(), data["back_adjusted_daily"].copy()
    for kind, frame, flag in [("raw_daily", raw, "3"), ("back_adjusted_daily", adjusted, "1")]:
        query = by_kind[kind]["params"]
        lower, upper = query["start_date"].replace("-", ""), query["end_date"].replace("-", "")
        if query["adjustflag"] != flag or not lower <= previous_day < day <= upper:
            raise ValueError("independent daily query coverage incomplete")
        frame["trade_date"] = frame.date.str.replace("-", "")
        expected = set(
            marks.loc[
                marks.ts_code.eq(symbol) & marks.trade_date.between(lower, upper), "trade_date"
            ]
        )
        if (
            frame.code.ne(code).any()
            or frame.trade_date.duplicated().any()
            or set(frame.trade_date) != expected
            or not {previous_day, day} <= expected
        ):
            raise ValueError("independent daily response coverage incomplete")
    local = marks.loc[marks.ts_code.eq(symbol)].set_index("trade_date")
    for row in raw.itertuples():
        for external, internal in [
            ("open", "open"),
            ("high", "high"),
            ("low", "low"),
            ("close", "close"),
            ("preclose", "pre_close"),
        ]:
            if not _same(getattr(row, external), local.loc[row.trade_date, internal]):
                raise ValueError("independent raw price mismatch")
    joined = raw[["trade_date", "close"]].merge(
        adjusted[["trade_date", "close"]],
        on="trade_date",
        suffixes=("_raw", "_adjusted"),
        validate="one_to_one",
    )
    try:
        ratios = [
            Fraction(str(row.close_adjusted)) / Fraction(str(row.close_raw))
            for row in joined.itertuples()
        ]
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError("invalid independent adjusted ratio") from error
    if not ratios or any(value <= 0 for value in ratios) or len(set(ratios)) != 1:
        raise ValueError("independent adjusted ratio changes")


def validate_factor_evidence(
    marks, explained, manifest_path, *, daily_manifest_sha256, dividend_sha256
):
    """Validate every alarm from actual source records; never smooth factor data.

    Reobserved stability alone also needs unchanged raw reference prices and
    modeled known corporate events. Residual changes need independent raw /
    adjusted bars and full-window economic-event query coverage.
    """
    path = Path(manifest_path)
    packet = json.loads(path.read_text())
    if (
        packet.get("schema_version") != "execution-factor-evidence.v1"
        or packet.get("scope") != "raw_price_execution_event_screen"
        or packet.get("daily_manifest_sha256") != daily_manifest_sha256
        or packet.get("dividend_sha256") != dividend_sha256
    ):
        raise ValueError("factor evidence scope or input source differs")
    required = {"ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "adj_factor"}
    if not required <= set(marks) or marks.duplicated(["ts_code", "trade_date"]).any():
        raise ValueError("factor evidence marks schema or uniqueness invalid")
    study = packet.get("study", {})
    if (
        study.get("start") != marks.trade_date.min()
        or study.get("end") != marks.trade_date.max()
        or set(study.get("symbols", [])) != set(marks.ts_code)
    ):
        raise ValueError("original study window or symbols differ")
    factors = pd.to_numeric(marks.adj_factor, errors="coerce")
    if not factors.map(lambda value: pd.notna(value) and math.isfinite(value) and value > 0).all():
        raise ValueError("invalid factor in original study input")
    work = marks.sort_values(["ts_code", "trade_date"]).copy()
    work["previous_factor"] = work.groupby("ts_code").adj_factor.shift()
    work["previous_close"] = work.groupby("ts_code").close.shift()
    work["previous_day"] = work.groupby("ts_code").trade_date.shift()
    changed = work.previous_factor.notna() & (work.adj_factor / work.previous_factor - 1).abs().gt(
        1e-9
    )
    alarms = work.loc[changed].copy()
    alarms = alarms.loc[
        [(a, b) not in explained for a, b in zip(alarms.ts_code, alarms.trade_date)]
    ]
    sources = _Sources(path.parent)
    diagnostic = pd.read_parquet(sources.path(packet["diagnostic"]))
    if diagnostic.duplicated(["ts_code", "trade_date"]).any():
        raise ValueError("factor evidence diagnostic duplicate keys")
    diagnostic = diagnostic.set_index(["ts_code", "trade_date"])
    indexed = work.set_index(["ts_code", "trade_date"])
    for key, old in diagnostic.iterrows():
        symbol, day = key
        if symbol not in set(work.ts_code) or not study["start"] <= day <= study["end"]:
            continue
        if key not in indexed.index:
            raise ValueError("original canonical alarm row is missing")
        row = indexed.loc[key]
        if (
            not _same(old.adj_factor_clean, row.adj_factor)
            or not _same(old.prev, row.previous_factor)
            or old.prev_trade_date != row.previous_day
        ):
            raise ValueError("original canonical factor, prior value or prior day differs")
    if not set(zip(alarms.ts_code, alarms.trade_date)) <= set(diagnostic.index):
        raise ValueError("uncovered adjustment alarm in full study window")
    fresh = pd.concat([pd.read_parquet(sources.path(ref)) for ref in packet["reobservations"]])
    if fresh.duplicated(["ts_code", "trade_date"]).any():
        raise ValueError("factor reobservation duplicate keys")
    fresh = fresh.set_index(["ts_code", "trade_date"])
    receipt_path = sources.path(packet["independent_receipt"])
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("provider") != "baostock":
        raise ValueError("unknown independent factor evidence provider")
    stable = independent = 0
    decisions = []
    for row in alarms.itertuples():
        key = (row.ts_code, row.trade_date)
        old = diagnostic.loc[key]
        if not _same(old.adj_factor_clean, row.adj_factor) or not _same(
            old.prev, row.previous_factor
        ):
            raise ValueError("original factor evidence no longer matches study")
        if (
            not _same(row.pre_close, row.previous_close)
            or row.close <= 0
            or row.previous_close <= 0
        ):
            raise ValueError("factor alarm has changed or missing market reference")
        prior_key = (row.ts_code, row.previous_day)
        if key not in fresh.index or prior_key not in fresh.index:
            raise ValueError("factor reobservation coverage incomplete")
        pair = [fresh.loc[key].adj_factor, fresh.loc[prior_key].adj_factor]
        if any(not math.isfinite(float(value)) or float(value) <= 0 for value in pair):
            raise ValueError("invalid factor reobservation")
        if _same(*pair):
            if any(q["symbol"] == row.ts_code for q in receipt["queries"]):
                _check_independent(
                    row.ts_code,
                    row.trade_date,
                    row.previous_day,
                    work,
                    receipt["queries"],
                    sources,
                    receipt_path,
                )
            stable += 1
            basis = "reobserved_stability_and_unchanged_raw_reference"
        else:
            _check_independent(
                row.ts_code,
                row.trade_date,
                row.previous_day,
                work,
                receipt["queries"],
                sources,
                receipt_path,
            )
            independent += 1
            basis = "cross_source_no_observed_economic_adjustment"
        decisions.append({"symbol": row.ts_code, "day": row.trade_date, "basis": basis})
    return {
        "explained_changes": int(changed.sum()),
        "unexplained_changes": 0,
        "modeled_event_changes": int(changed.sum()) - len(alarms),
        "reobserved_stable_keys": stable,
        "cross_source_nonaction_keys": independent,
        "scope": "raw_price_execution_event_screen_not_complete_event_source",
        "factor_values_changed": False,
        "provider_internal_cause_proven": False,
        "revision_safe": False,
        "decisions": decisions,
        "evidence_manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "evidence_files_sha256": sources.hashes,
    }
