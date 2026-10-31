"""Run the five predeclared follow-up studies from explicit frozen inputs.

All raw inputs stay with the data owner. Writes a new external output directory;
no API calls, moving aliases, provider credentials or historical optimization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir

import numpy as np
import pandas as pd

from market_research.studies.asset_returns.analysis import validate_levels
from market_research.studies.asset_returns.allocation import compare_allocation
from market_research.studies.asset_returns.constituents import constituent_retention
from market_research.studies.asset_returns.etf import etf_gap
from market_research.studies.asset_returns.inputs import month_end_levels, read_frozen_response
from market_research.studies.asset_returns.robustness import (
    annual_contributions,
    endpoint_sensitivity,
    relative_waiting,
)


def _native(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"unsupported result type: {type(value).__name__}")


def run(previous: Path, previous_owner: Path, owner: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError("select a new output directory")
    if any(
        (p / ".git").exists()
        for p in [output.resolve(), *output.resolve().parents]
        if p not in {Path.home(), Path(gettempdir())}
    ):
        raise ValueError("results must remain outside repositories")
    old = {}
    sources = []
    for name in ["all_share", "large_cap", "small_cap", "multi_asset"]:
        p = previous / "inputs" / (name + ".csv")
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        old_result = json.loads((previous / "runs" / name / "results.json").read_text())
        if old_result["provenance"]["input_sha256"] != digest:
            raise ValueError("first-round frozen input changed")
        old[name] = pd.read_csv(p)
        sources.append({"id": name, "sha256": digest})
    raw = owner / "raw"
    receipt_bytes = (raw / "receipt.json").read_bytes()
    receipts = json.loads(receipt_bytes)
    frames = {}
    for row in receipts:
        if row.get("code") != 0 or not row.get("rows"):
            continue
        f = read_frozen_response(raw / (row["id"] + ".json"), row["sha256"])
        key = (row["api"], row["params"].get("ts_code", row["params"].get("index_code")))
        frames.setdefault(key, []).append(f)
        sources.append({"id": row["id"], "sha256": row["sha256"]})
    cal_receipts = json.loads((previous_owner / "raw/receipt.json").read_text())
    cal_row = next(r for r in cal_receipts if r["id"] == "calendar")
    calendar = read_frozen_response(previous_owner / "raw/calendar.json", cal_row["sha256"])
    sessions = pd.DatetimeIndex(pd.to_datetime(calendar.cal_date))
    endpoint_calendar = sessions[(sessions >= "2017-01-01") & (sessions <= "2025-12-31")]
    sensitivity = {}
    for name in ["all_share", "large_cap", "small_cap"]:
        sensitivity[name] = {
            "grid": endpoint_sensitivity(old[name], "total"),
            "annual": annual_contributions(old[name], "total"),
        }
    sensitivity["gold"] = {
        "grid": endpoint_sensitivity(old["all_share"], "gold"),
        "annual": annual_contributions(old["all_share"], "gold"),
    }
    waiting = {
        "small_vs_large": relative_waiting(old["small_cap"], "total", "benchmark"),
        "equity_vs_gold": relative_waiting(old["all_share"], "total", "gold"),
        "equity_vs_treasury": relative_waiting(old["multi_asset"], "total", "bond"),
    }
    allocations = []
    allocations.append(
        {"id": "equity_only", **compare_allocation(old["multi_asset"], {"total": 1.0}, "buy_hold")}
    )
    for ident, weights in [
        ("stock_bond_60_40", {"total": 0.6, "bond": 0.4}),
        ("stock_bond_gold_equal", {"total": 1 / 3, "bond": 1 / 3, "gold": 1 / 3}),
    ]:
        for policy in ["buy_hold", "annual", "threshold_5pp"]:
            for cost in [0, 10, 50]:
                allocations.append(
                    {"id": ident, **compare_allocation(old["multi_asset"], weights, policy, cost)}
                )
    etfs = {}
    normalized_etfs = {}
    index_map = {"510300.SH": "large_cap", "159919.SZ": "large_cap", "512100.SH": "small_cap"}
    for code, index_name in index_map.items():
        required = ["fund_daily", "fund_adj", "fund_nav", "fund_div", "fund_basic"]
        absent = [api for api in required if (api, code) not in frames]
        if absent:
            etfs[code] = {"status": "blocked", "missing_apis": absent}
            continue
        bars = pd.concat(frames["fund_daily", code], ignore_index=True)
        factors = pd.concat(frames["fund_adj", code], ignore_index=True)
        nav = pd.concat(frames["fund_nav", code], ignore_index=True)
        dividends = pd.concat(frames["fund_div", code], ignore_index=True)
        if (
            bars.trade_date.duplicated().any()
            or factors.trade_date.duplicated().any()
            or nav.nav_date.duplicated().any()
        ):
            etfs[code] = {"status": "blocked", "reason": "duplicate_date_requires_version_audit"}
            continue
        bars["date"] = pd.to_datetime(bars.trade_date)
        factors["date"] = pd.to_datetime(factors.trade_date)
        nav["date"] = pd.to_datetime(nav.nav_date)
        monthly = {}
        errors = []
        for source, column in [
            (bars, "close"),
            (factors, "adj_factor"),
            (nav, "unit_nav"),
            (nav, "adj_nav"),
        ]:
            try:
                monthly[column] = (
                    month_end_levels(
                        source[["date", column]].rename(columns={column: "close"}),
                        endpoint_calendar,
                    )
                    .set_index("date")
                    .close
                )
            except ValueError as exc:
                errors.append(str(exc))
        if errors:
            etfs[code] = {
                "status": "blocked",
                "reason": "missing_month_end_or_invalid_quote",
                "details": errors,
            }
            continue
        index = old[index_name].copy()
        index["date"] = pd.to_datetime(index.date)
        monthly["index_total"] = index.set_index("date").total.reindex(monthly["close"].index)
        joined = pd.DataFrame(monthly).rename_axis("date").reset_index()
        validate_levels(joined, list(monthly))
        expected = set(endpoint_calendar)
        missing = sorted(expected - set(bars.date))
        in_period_div = dividends.loc[
            (dividends.ex_date.fillna("") >= "20170101")
            & (dividends.ex_date.fillna("") <= "20251231")
        ]
        # Count records, not paid events: proposals and implementations can duplicate.
        div_dates = in_period_div.ex_date.dropna().nunique()
        basics = pd.concat(frames["fund_basic", code], ignore_index=True)
        expected_name = "沪深300" if index_name == "large_cap" else "中证1000"
        if not basics.benchmark.fillna("").str.contains(expected_name, regex=False).all():
            raise ValueError("fund benchmark mapping not verified")
        result = etf_gap(joined)
        etfs[code] = {
            "status": "descriptive_proxy",
            **result,
            "raw_dividend_records_in_period": len(in_period_div),
            "unique_dividend_ex_dates": int(div_dates),
            "missing_daily_market_sessions": len(missing),
            "month_end_marks_verified": len(joined),
            "nav_publication_after_valuation_date_count": int(
                (pd.to_datetime(nav.ann_date) > nav.date).sum()
            ),
            "tracking_index_verified_from_fund_basic": True,
        }
        normalized_etfs[code] = joined
    constituents = {}
    for code, count in [("000300.SH", 300), ("000852.SH", 1000)]:
        parts = frames.get(("index_weight", code), [])
        if len(parts) != 11:
            constituents[code] = {"status": "blocked", "returned_annual_queries": len(parts)}
            continue
        selected = []
        dates = []
        for f in parts:
            latest = f.trade_date.max()
            snap = f.loc[f.trade_date.eq(latest)].copy()
            actual = pd.Timestamp(latest)
            expected_date = sessions[(sessions.year == actual.year) & (sessions.month == 12)].max()
            if actual != expected_date:
                raise ValueError("annual weights not on verified final session")
            dates.append(actual)
            snap["date"] = pd.to_datetime(snap.trade_date)
            snap["symbol"] = snap.con_code
            snap["weight"] = pd.to_numeric(snap.weight) / 100
            selected.append(snap[["date", "symbol", "weight"]])
        constituents[code] = {
            "status": "snapshot_audit",
            **constituent_retention(pd.concat(selected), count, weight_quantum=0.00001),
        }
    code_files = [
        Path(__file__),
        *sorted(
            (Path(__file__).parents[1] / "src/market_research/studies/asset_returns").glob("*.py")
        ),
    ]
    report = {
        "schema_version": 1,
        "study_id": "asset-robustness-20261031",
        "protocol": "five predeclared follow-ups; no parameter optimization",
        "provenance": {
            "inputs": sources,
            "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
            "code_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in code_files},
        },
        "sensitivity": sensitivity,
        "waiting": waiting,
        "allocations": allocations,
        "etfs": etfs,
        "constituents": constituents,
    }
    serialized = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False, default=_native)
    output.mkdir(parents=True, exist_ok=False)
    (output / "results.json").write_text(serialized + "\n")
    for code, f in normalized_etfs.items():
        f.to_csv(output / (code.replace(".", "_") + "_monthly.csv"), index=False)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--previous-owner", type=Path, required=True)
    parser.add_argument("--owner", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    r = run(a.previous, a.previous_owner, a.owner, a.output)
    print(
        json.dumps(
            {
                "etf_status": {k: v["status"] for k, v in r["etfs"].items()},
                "constituent_status": {k: v["status"] for k, v in r["constituents"].items()},
                "allocation_scenarios": len(r["allocations"]),
            }
        )
    )
