"""Recheck two raw snapshot dates and compare saved event/path evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow.parquet as pq

from market_research.studies.ashare_execution_costs.fitness import (
    prepare_paths,
    reconcile_selection,
    reference_timing,
)
from market_research.studies.ashare_execution_costs.replay import snapshot_path
from market_research.studies.ashare_execution_costs.pilot import book_metrics


def hash_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def clock_expression(name, profile):
    # Independent SQL clock formula; declared profile, no inferred aliases.
    v = f'TRY_CAST("{name}" AS BIGINT)'
    if profile == "relative_0930_ms":
        return f"({v}+34200000)"
    if profile == "native_hhmmssmmm":
        return (
            f"(({v}//10000000)*3600000+(({v}//100000)%100)*60000+(({v}//1000)%100)*1000+{v}%1000)"
        )
    raise ValueError("explicit supported clock profile required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--saved", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("new output directory required")
    args.output.mkdir(parents=True)
    spec = json.loads(args.spec.read_text())
    days = list(map(int, spec["comparison_days"]))
    con = duckdb.connect(
        config={
            "threads": "2",
            "memory_limit": "2GB",
            "temp_directory": str(args.output / "sql-temp"),
        }
    )
    audit = []
    receipts = []
    canonical = {}
    common = None
    for day in days:
        entry = next(e for e in spec["snapshot_sources"] if day in e["days"])
        source = Path(entry["path"])
        stat = source.stat()
        profile = entry["clock_profile"]
        security, clock = (
            ("ticker", "time_ms") if profile == "relative_0930_ms" else ("SecuCode", "TickTime")
        )
        con.read_parquet(str(source), file_row_number=True).create_view("raw", replace=True)
        milliseconds = clock_expression(clock, profile)
        # Scan only identity/date/clock columns; every source row of the declared day is eligible for this identity audit.
        raw = con.execute(
            f'''SELECT TRY_CAST("{security}" AS BIGINT) SecuCode, {milliseconds} absolute_ms,
                       file_row_number source_row FROM raw WHERE TradingDay=?''',
            [day],
        ).df()
        nulls = int(raw[["SecuCode", "absolute_ms"]].isna().any(axis=1).sum())
        raw = raw.dropna().astype("int64")
        raw["minute"] = raw.absolute_ms // 60000
        stock = raw.SecuCode.floordiv(1000).isin(
            [0, 1, 2, 3, 300, 301, 600, 601, 603, 605, 688, 689]
        )
        continuous = ((raw.absolute_ms >= 34200000) & (raw.absolute_ms < 41400000)) | (
            (raw.absolute_ms >= 46800000) & (raw.absolute_ms < 53820000)
        )
        sampled = raw.loc[stock & continuous & raw.SecuCode.mod(37).eq(0)]
        first = sampled.sort_values(["absolute_ms", "source_row"]).drop_duplicates(
            ["SecuCode", "minute"]
        )
        selected = args.saved / f"selected_books_{entry['days'][0]}.parquet"
        books = pd.read_parquet(selected)
        books = books.loc[books.TradingDay.eq(day)].copy()
        if profile == "relative_0930_ms":
            books["SecuCode"] = pd.to_numeric(books.ticker).astype("int64")
            books["absolute_ms"] = books.time_ms + 34200000
        else:
            t = books.TickTime
            books["absolute_ms"] = (
                (t // 10000000) * 3600000
                + ((t // 100000) % 100) * 60000
                + ((t // 1000) % 100) * 1000
                + t % 1000
            )
            books["time_ms"] = books.absolute_ms - 34200000
        books["minute"] = books.absolute_ms // 60000
        reconcile = reconcile_selection(
            first[["SecuCode", "minute", "absolute_ms", "source_row"]],
            books[["SecuCode", "minute", "absolute_ms", "source_row"]],
        )
        codes = set(books.SecuCode.astype(int))
        common = codes if common is None else common & codes
        # Compare with this same day's observed daily trading records, not historical eligibility.
        daily_files = sorted((Path(spec["daily_root"]) / f"trade_date={day}").glob("*.parquet"))
        daily = pd.concat(
            [pd.read_parquet(p, columns=["symbol", "amount"]) for p in daily_files],
            ignore_index=True,
        )
        daily["SecuCode"] = pd.to_numeric(
            daily.symbol.astype(str).str.split(".").str[0], errors="coerce"
        )
        daily = daily.loc[daily.SecuCode.notna() & daily.amount.gt(0)]
        daily = daily.loc[
            daily.SecuCode.floordiv(1000).isin([0, 1, 2, 3, 300, 301, 600, 601, 603, 605, 688, 689])
            & daily.SecuCode.mod(37).eq(0)
        ]
        traded = set(daily.SecuCode.astype(int))
        raw_codes = set(raw.loc[stock & continuous].SecuCode)
        absent = traded - raw_codes
        missing_minutes = len(codes) * 237 - len(first)
        by_code = first.groupby("SecuCode").minute.nunique()
        gaps = {
            "securities_with_any_missing_minute": int(by_code.lt(237).sum()),
            "expected_minutes_for_observed_securities": len(codes) * 237,
            "missing_minutes": missing_minutes,
            "daily_positive_amount_sampled_securities": len(traded),
            "daily_traded_but_no_continuous_raw_quotes": len(absent),
        }
        path = args.output / f"private-source-selection-{day}.parquet"
        first.to_parquet(path, index=False)
        audit.append(
            {
                "day": str(day),
                "source_metadata_rows": pq.ParquetFile(source).metadata.num_rows,
                "raw_declared_day_rows": len(raw) + nulls,
                "null_identity_or_clock_rows": nulls,
                "selection": reconcile,
                "coverage": gaps,
            }
        )
        receipts.append(
            {
                "kind": "raw_identity_scan",
                "path": str(source),
                "bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
                "content_hash_not_recomputed": True,
                "selected_saved_sha256": hash_file(selected),
                "daily_source_sha256": {str(p): hash_file(p) for p in daily_files},
            }
        )
        if (source.stat().st_size, source.stat().st_mtime_ns) != (stat.st_size, stat.st_mtime_ns):
            raise ValueError("source changed during scan")
        books["book_valid"] = book_metrics(
            *[
                books[[f"{side}{field}{i}" for i in range(1, 11)]].to_numpy()
                for side, field in [
                    ("Bid", "Price"),
                    ("Ask", "Price"),
                    ("Bid", "Volume"),
                    ("Ask", "Volume"),
                ]
            ]
        )["valid"]
        audit[-1]["coverage"]["deficient_minute_counts"] = {
            str(int(m)): int(n) for m, n in first.groupby("minute").size().items() if n < len(codes)
        }
        canonical[day] = books
        print(f"completed raw selection audit {day}", flush=True)
    events = []
    for day in days:
        orders = args.saved / f"orders_{day}_common.parquet"
        trades = args.saved / f"trades_{day}_common.parquet"
        con.read_parquet(str(orders)).create_view("orders_day", replace=True)
        pre = args.saved / f"preopening_orders_{day}_common.parquet"
        if pre.exists():
            con.read_parquet(str(pre)).create_view("pre", replace=True)
            con.execute(
                "CREATE OR REPLACE VIEW all_orders AS SELECT * FROM orders_day UNION ALL BY NAME SELECT * FROM pre"
            )
        else:
            con.execute("CREATE OR REPLACE VIEW all_orders AS SELECT * FROM orders_day")
        con.read_parquet(str(trades)).create_view("trades_day", replace=True)
        available = {r[0] for r in con.execute("DESCRIBE all_orders").fetchall()}
        for market, predicate in [
            ("shanghai", "SecuCode>=600000"),
            ("shenzhen", "SecuCode<400000"),
        ]:
            con.execute(
                f"CREATE OR REPLACE VIEW orders_market AS SELECT * FROM all_orders WHERE {predicate}"
            )
            con.execute(
                f"CREATE OR REPLACE VIEW trades_market AS SELECT * FROM trades_day WHERE {predicate}"
            )
            counts = (
                con.sql(
                    "SELECT count(*) trade_rows,count_if(Price<=0) nonpositive_price FROM trades_market"
                )
                .df()
                .iloc[0]
                .to_dict()
            )
            refs = [
                reference_timing(con, "orders_market", "trades_market", candidate)
                for candidate in ["OrderID", "DBOrderID"]
                if candidate in available
            ]
            events.append(
                {
                    "day": str(day),
                    "market": market,
                    "trade_rows": int(counts["trade_rows"]),
                    "nonpositive_price_rows": int(counts["nonpositive_price"] or 0),
                    "reference_candidates": refs,
                }
            )
        for p in [orders, trades, *([pre] if pre.exists() else [])]:
            receipts.append({"kind": "saved_event", "path": str(p), "sha256": hash_file(p)})
        print(f"completed candidate timing {day}", flush=True)
    rows = []
    path_scope = []
    for day, books in canonical.items():
        paths, scope = prepare_paths(books, day, common)
        scope["day"] = str(day)
        scope["fresh_terminal_benchmark_securities"] = 0
        path_scope.append(scope)
        for code, path in paths.items():
            for quantity in (1000, 10000, 100000):
                for side in ("buy", "sell"):
                    for mode in ("market", "twap", "limit_wait"):
                        # High budget isolates share-depth assumptions, not a portfolio financing claim.
                        result = snapshot_path(
                            path,
                            quantity=quantity,
                            budget_cny=1e9,
                            mode=mode,
                            side=side,
                            horizon_ms=300000 - int(path.iloc[0].time_ms),
                        )
                        result.update(
                            SecuCode=code, day=str(day), quantity=quantity, side=side, mode=mode
                        )
                        rows.append(result)
                        if (
                            quantity == 1000
                            and side == "buy"
                            and mode == "market"
                            and result["terminal_mid_cny"] is not None
                        ):
                            scope["fresh_terminal_benchmark_securities"] += 1
        print(f"completed fixed-day paths {day}", flush=True)
    (args.output / "private-paths.json").write_text(json.dumps(rows, indent=2) + "\n")
    frame = pd.DataFrame(rows)
    aggregates = []
    for (day, quantity, side, mode), group in frame.groupby(["day", "quantity", "side", "mode"]):
        values = pd.to_numeric(group.total_shortfall_bp, errors="coerce").dropna()
        aggregates.append(
            {
                "day": day,
                "quantity": int(quantity),
                "side": side,
                "mode": mode,
                "paths": len(group),
                "full_fill_paths": int(group.remaining_quantity.eq(0).sum()),
                "median_fill_fraction": float((group.filled_quantity / quantity).median()),
                "cost_observed_paths": len(values),
                "shortfall_p50_bp": float(values.median()) if len(values) else None,
                "shortfall_p90_bp": float(values.quantile(0.9)) if len(values) else None,
            }
        )
    proposed = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "days": list(map(str, days)),
            "common_observed_securities": len(common),
            "whole_warehouse_audited": False,
            "actual_order_calibrated": False,
            "event_semantics_verified": False,
            "causal_impact_identified": False,
        },
        "raw_selection": audit,
        "event_timing": events,
        "path_scope": path_scope,
        "path_aggregates": aggregates,
        "assumptions": [
            "Saved events belong to declared extraction days; keys show candidate presence only.",
            "Daily positive-amount records are an observed trading comparison, not an eligibility master.",
            "Fixed 09:30–09:35 window; arrival delay at most 60 seconds; last quote freshness at most 60 seconds.",
            "Common securities condition on survival; no market-wide temporal trend is identified.",
            "Three share quantities, no fees, lots, own impact, passive queue or participation limit; independent snapshot refresh.",
        ],
        "review_status": "proposed_not_yet_reviewed",
    }
    (args.output / "fitness.proposed.json").write_text(json.dumps(proposed, indent=2) + "\n")
    (args.output / "private-receipt.json").write_text(
        json.dumps(
            {
                "sources": receipts,
                "spec_sha256": hash_file(args.spec),
                "runner_sha256": hash_file(Path(__file__)),
                "fitness_sha256": hash_file(
                    Path(__file__).parents[1]
                    / "src/market_research/studies/ashare_execution_costs/fitness.py"
                ),
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
