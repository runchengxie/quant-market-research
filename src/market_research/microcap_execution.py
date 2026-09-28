"""Diagnostic small-cap execution replay with explicit data-quality boundaries."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml


PANEL_COLUMNS = {
    "ts_code", "trade_date", "close", "adj_close", "total_mv", "amount",
    "is_st", "is_suspended", "list_date", "delist_date",
}


def _iso(day: str) -> str:
    if len(day) != 8 or not day.isdigit():
        raise ValueError("dates must use YYYYMMDD")
    return f"{day[:4]}-{day[4:6]}-{day[6:]}"


def decision_clock(day: str, entry: str, valuation: str) -> dict[str, str]:
    decision, next_session, last = _iso(day), _iso(entry), _iso(valuation)
    return {
        "schema_version": "research.clock.v1",
        "timezone": "Asia/Shanghai",
        "information_cutoff_at": f"{decision}T20:00:00+08:00",
        "signal_at": f"{decision}T20:01:00+08:00",
        "decision_at": f"{decision}T20:02:00+08:00",
        "earliest_order_at": f"{next_session}T09:30:00+08:00",
        "execution_window_start_at": f"{next_session}T09:30:00+08:00",
        "execution_window_end_at": f"{next_session}T15:00:00+08:00",
        "valuation_at": f"{last}T16:00:00+08:00",
        "timing_policy_id": "microcap.modeled_after_close_next_session.v1",
        "trading_calendar_ref": "microcap.daily_clean_sessions",
    }


def load_clean_panel(asset: Path, instruments: Path, start: str, end: str) -> pd.DataFrame:
    """Read only the requested sessions from the published per-symbol clean asset."""
    import duckdb

    files = str(asset / "data" / "*.parquet")
    manifest_path = asset / "manifest.yml"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"clean daily asset has no manifest: {asset}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("status") != "completed":
        raise ValueError(f"clean daily asset has no completed manifest: {asset}")
    st_source = (manifest.get("inputs") or {}).get("st_history_file")
    if not st_source:
        raise ValueError("clean daily asset has no dated ST source lineage")
    st_path = Path(st_source)
    receipt_path = st_path.with_suffix(".receipt.json")
    if not st_path.is_file() or not receipt_path.is_file():
        raise FileNotFoundError(f"published ST history or receipt is missing: {st_path}")
    st_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if st_receipt.get("quality_status") != "complete":
        raise ValueError("published ST history is not quality complete")
    if not instruments.is_file():
        raise FileNotFoundError(f"instrument snapshot is missing: {instruments}")
    connection = duckdb.connect()
    try:
        panel = connection.execute(
            """SELECT ts_code, trade_date, close, adj_close, total_mv, amount,
                      is_st, is_suspended, list_date
               FROM read_parquet(?) WHERE trade_date BETWEEN ? AND ?""",
            [files, start, end],
        ).fetchdf()
    finally:
        connection.close()
    basic = pd.read_parquet(instruments, columns=["ts_code", "delist_date"])
    if basic.ts_code.duplicated().any():
        raise ValueError("instrument snapshot has duplicate symbols")
    return panel.merge(basic, on="ts_code", how="left", validate="many_to_one")


def load_limit_rows(asset: Path, days: list[str]) -> pd.DataFrame:
    if not (asset / "manifest.yml").is_file():
        raise FileNotFoundError(f"limit asset has no manifest: {asset}")
    frames = []
    for day in days:
        files = sorted((asset / "data" / f"trade_date={day}").glob("*.parquet"))
        if not files:
            raise FileNotFoundError(f"limit asset has no partition for {day}")
        frames.extend(
            pd.read_parquet(path, columns=["ts_code", "trade_date", "up_limit", "down_limit"])
            for path in files
        )
    result = pd.concat(frames, ignore_index=True)
    if result.duplicated(["trade_date", "ts_code"]).any():
        raise ValueError("limit asset has duplicate symbol/date keys")
    return result


def historical_name_mask(namechange: pd.DataFrame, source: pd.DataFrame) -> pd.Series:
    """Require a known, non-ST name outside the delisting period at each decision."""
    required = {"ts_code", "name", "change_reason", "start_date", "end_date", "ann_date"}
    if missing := required - set(namechange):
        raise ValueError(f"namechange asset is missing {sorted(missing)}")
    events = namechange[list(required)].copy()
    for column in ("start_date", "end_date", "ann_date"):
        events[column] = events[column].fillna("99999999").astype(str)
    eligible = pd.Series(False, index=source.index)
    for day, rows in source.groupby("trade_date", sort=False):
        active = events.loc[
            events.start_date.le(day) & events.end_date.ge(day) & events.ann_date.lt(day)
        ]
        active = active.sort_values(["ts_code", "start_date", "ann_date"]).drop_duplicates(
            "ts_code", keep="last"
        )
        allowed = active.loc[
            ~active.name.str.contains("ST", na=True)
            & ~active.change_reason.eq("退市整理期"), "ts_code"
        ]
        eligible.loc[rows.index] = rows.ts_code.isin(allowed).to_numpy()
    return eligible


def build_replay_inputs(
    panel: pd.DataFrame,
    limits: pd.DataFrame,
    suspensions: pd.DataFrame,
    *,
    constituent_count: int,
    namechange: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, str]], dict[str, int]]:
    """Build targets and price marks, refusing unknown status and price gaps."""
    if missing := PANEL_COLUMNS - set(panel):
        raise ValueError(f"clean panel is missing {sorted(missing)}")
    if constituent_count <= 0:
        raise ValueError("constituent_count must be positive")
    source = panel.copy()
    source["trade_date"] = source.trade_date.astype(str)
    source["ts_code"] = source.ts_code.astype(str)
    if source.duplicated(["trade_date", "ts_code"]).any():
        raise ValueError("clean panel has duplicate symbol/date keys")
    days = sorted(source.trade_date.unique().tolist())
    if len(days) < 3:
        raise ValueError("at least three market sessions are required")
    name_eligible = (
        historical_name_mask(namechange, source)
        if namechange is not None else pd.Series(True, index=source.index)
    )
    listed = source.list_date.notna() & source.list_date.astype(str).le(source.trade_date)
    delisted = source.delist_date.notna() & source.delist_date.astype(str).le(source.trade_date)
    eligible = (
        listed & ~delisted & name_eligible & source.is_st.eq(False).fillna(False)
        & source.is_suspended.eq(False).fillna(False)
        & source.total_mv.gt(0) & source.amount.gt(0)
        & source.close.gt(0) & source.adj_close.gt(0)
    )
    candidates = source.loc[eligible].sort_values(["trade_date", "total_mv", "ts_code"])
    rows: list[dict[str, object]] = []
    clocks: dict[str, dict[str, str]] = {}
    for index, day in enumerate(days[:-1]):
        selected = candidates.loc[candidates.trade_date.eq(day)].head(constituent_count)
        if len(selected) != constituent_count:
            raise ValueError(f"{day} has only {len(selected)} eligible names")
        entry = days[index + 1]
        clocks[day] = decision_clock(day, entry, days[-1])
        rows.extend(
            {"rebalance_date": day, "entry_date": entry,
             "symbol": symbol, "weight": 1.0 / constituent_count}
            for symbol in selected.ts_code
        )
    positions = pd.DataFrame(rows)
    first_selected = positions.groupby("symbol").rebalance_date.min().to_dict()
    selected_symbols = set(first_selected)
    source = source.loc[source.ts_code.isin(selected_symbols)].copy()
    active = source.loc[source.apply(
        lambda row: row.trade_date >= first_selected[row.ts_code], axis=1
    )].copy()
    delist_dates = (
        source.loc[source.delist_date.notna(), ["ts_code", "delist_date"]]
        .drop_duplicates("ts_code").set_index("ts_code").delist_date.astype(str).to_dict()
    )

    event_keys = set()
    if not suspensions.empty:
        required = {"ts_code", "trade_date", "suspend_type"}
        if missing := required - set(suspensions):
            raise ValueError(f"suspension events are missing {sorted(missing)}")
        event_keys = set(
            zip(
                suspensions.loc[suspensions.suspend_type.eq("S"), "trade_date"].astype(str),
                suspensions.loc[suspensions.suspend_type.eq("S"), "ts_code"].astype(str),
                strict=True,
            )
        )
    known = active.set_index(["trade_date", "ts_code"])
    synthetic = []
    delist_carry_rows = 0
    for symbol, first in first_selected.items():
        previous = None
        for day in (date for date in days if date >= first):
            key = (day, symbol)
            if key in known.index:
                value = known.loc[key, "adj_close"]
                if pd.notna(value) and float(value) > 0:
                    previous = float(value)
                continue
            delisted = day >= delist_dates.get(symbol, "99999999")
            if previous is None or (not delisted and key not in event_keys):
                raise ValueError(f"unexplained daily price gap for {symbol} on {day}")
            delist_carry_rows += int(delisted)
            synthetic.append({
                "trade_date": day, "ts_code": symbol, "close": None,
                "adj_close": previous, "amount": 0.0, "is_suspended": not delisted,
                "delist_date": delist_dates.get(symbol),
            })
    prices = pd.concat([active, pd.DataFrame(synthetic)], ignore_index=True)
    limit_rows = limits[["trade_date", "ts_code", "up_limit", "down_limit"]].copy()
    limit_rows["trade_date"] = limit_rows.trade_date.astype(str)
    if limit_rows.duplicated(["trade_date", "ts_code"]).any():
        raise ValueError("limit input has duplicate symbol/date keys")
    prices = prices.merge(limit_rows, on=["trade_date", "ts_code"], how="left", validate="one_to_one")
    for column in ("close", "adj_close", "amount", "up_limit", "down_limit"):
        prices[column] = pd.to_numeric(prices[column], errors="coerce")
    suspended = prices.is_suspended.eq(True).fillna(False)
    delisted = prices.delist_date.notna() & prices.delist_date.astype(str).le(prices.trade_date)
    required = ~(suspended | delisted)
    if prices.loc[required, ["close", "adj_close", "amount", "up_limit", "down_limit"]].isna().any().any():
        raise ValueError("active pricing has unknown prices, liquidity or price limits")
    if prices.loc[required, "adj_close"].le(0).any():
        raise ValueError("active pricing has nonpositive adjusted marks")
    prices["limit_up"] = required & prices.close.ge(prices.up_limit - 0.005)
    prices["limit_down"] = required & prices.close.le(prices.down_limit + 0.005)
    prices["tradable"] = required & prices.amount.gt(0)
    pricing = prices.rename(columns={"ts_code": "symbol"})[
        ["trade_date", "symbol", "adj_close", "amount", "tradable", "limit_up", "limit_down"]
    ]
    return positions, pricing, clocks, {
        "confirmed_suspension_carry_rows": len(synthetic) - delist_carry_rows,
        "post_delist_nontradable_carry_rows": delist_carry_rows,
        "historical_name_excluded_rows": int((~name_eligible).sum()) if namechange is not None else 0,
    }


def run_diagnostic(
    *, daily_asset: Path, limit_asset: Path, instruments: Path, suspensions: Path,
    namechange_asset: Path,
    output_dir: Path, start: str, end: str, constituent_count: int = 400,
) -> dict[str, object]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"output directory is not empty: {output_dir}")
    try:
        panel = load_clean_panel(daily_asset, instruments, start, end)
        days = sorted(panel.trade_date.astype(str).unique().tolist())
        limits = load_limit_rows(limit_asset, days)
        events = pd.read_parquet(suspensions, columns=["ts_code", "trade_date", "suspend_type"])
        namechange = pd.read_parquet(namechange_asset)
        positions, pricing, clocks, audit = build_replay_inputs(
            panel, limits, events, constituent_count=constituent_count, namechange=namechange
        )
    except (ValueError, FileNotFoundError) as error:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "summary.json").write_text(
            json.dumps({"evidence_tier": "blocked", "start": start, "end": end,
                        "constituent_count": constituent_count, "reason": str(error)},
                       ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        raise
    from portfolio_backtester.execution_sim import ExecutionSimConfig, audit_delisting_exits
    from market_research.runtime_jobs import publish_verified_frames, run_sequenced_job

    config = ExecutionSimConfig(
        enabled=True, portfolio_value=1_000_000.0, participation_rate=0.05,
        liquidity_cols=("amount",), liquidity_notional_multiplier=1000.0,
        buy_max_days=5, sell_max_days=10, enforce_t1=True,
        enforce_price_limits=True, limit_up_col="limit_up", limit_down_col="limit_down",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    result_dir, receipt = run_sequenced_job(
        output_dir / ".runtime", "microcap", positions, pricing, clocks, asdict(config),
        transaction_cost_bps=5.0,
    )
    selected = set(positions.symbol)
    delist_dates = {
        str(row.ts_code): str(row.delist_date)
        for row in panel.loc[panel.ts_code.isin(selected) & panel.delist_date.notna(),
                             ["ts_code", "delist_date"]].drop_duplicates("ts_code").itertuples()
    }
    try:
        exit_audit = audit_delisting_exits(
            pd.read_parquet(result_dir / "fills.parquet"), pricing, delist_dates,
            price_col="adj_close",
        )
    except ValueError as error:
        (output_dir / "summary.json").write_text(
            json.dumps({"evidence_tier": "blocked", "start": start, "end": end,
                        "constituent_count": constituent_count, "reason": str(error)},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        raise
    publish_verified_frames(result_dir, output_dir)
    (output_dir / "decision_clocks.json").write_text(
        json.dumps(clocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    sources = {"daily_manifest": daily_asset / "manifest.yml",
               "limit_manifest": limit_asset / "manifest.yml", "instruments": instruments,
               "suspensions": suspensions, "namechange": namechange_asset}
    report: dict[str, object] = {
        "evidence_tier": "diagnostic", "constituent_count": constituent_count,
        "start": start, "end": end, "decision_count": len(clocks),
        "terminal_nav": float(
            pd.read_parquet(output_dir / "daily_ledger.parquet").nav.iloc[-1]
            / config.portfolio_value
        ),
        "runtime_job_id": receipt["job_id"],
        "reason": "input release times, raw corporate actions and delisting cash settlement are unverified",
        "audit": audit,
        "delisting_exit_audit": exit_audit.to_dict("records"),
        "source_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sources.items()
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Microcap public execution engine diagnostic")
    parser.add_argument("--daily-asset", type=Path, required=True)
    parser.add_argument("--limit-asset", type=Path, required=True)
    parser.add_argument("--instruments", type=Path, required=True)
    parser.add_argument("--suspensions", type=Path, required=True)
    parser.add_argument("--namechange-asset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--constituent-count", type=int, default=400)
    args = parser.parse_args()
    print(json.dumps(run_diagnostic(
        daily_asset=args.daily_asset, limit_asset=args.limit_asset,
        instruments=args.instruments, suspensions=args.suspensions,
        namechange_asset=args.namechange_asset,
        output_dir=args.output_dir, start=args.start, end=args.end,
        constituent_count=args.constituent_count,
    ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
