#!/usr/bin/env python3
"""Reproduce the constrained grouped valuation checkpoint from frozen local inputs."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from market_research.studies.grouped_valuation_ledger import LedgerVerifier, run_ledger


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + "\n")


def action_audit(path, members):
    frame = pd.read_parquet(path)
    names = set(members.ts_code)
    implemented = frame.loc[frame.ts_code.isin(names) & frame.div_proc.eq("实施")]
    window = implemented.loc[
        implemented.ex_date.ge(members.entry_date.min())
        & implemented.ex_date.le(members.endpoint_date.max())
    ]
    fields = [
        "record_date",
        "ex_date",
        "pay_date",
        "div_listdate",
        "imp_ann_date",
        "cash_div_tax",
        "stk_div",
    ]
    duplicates = window.duplicated(["ts_code", "ex_date"], keep=False)
    return dict(
        raw_share_ready=False,
        independent_event_completeness=False,
        revision_safe=False,
        signal_names=len(names),
        snapshot_names=frame.ts_code.nunique(),
        signal_names_without_snapshot_rows=len(names - set(frame.ts_code)),
        implemented_window_rows=len(window),
        implemented_missing_ex_date_rows=int(implemented.ex_date.isna().sum()),
        missing_fields={f: int(window[f].isna().sum()) for f in fields},
        positive_cash_missing_pay_date=int(
            (window.cash_div_tax.gt(0) & window.pay_date.isna()).sum()
        ),
        positive_stock_missing_listing_date=int(
            (window.stk_div.gt(0) & window.div_listdate.isna()).sum()
        ),
        repeated_symbol_ex_date_rows=int(duplicates.sum()),
        caveats=[
            "Snapshot-row absence does not prove no corporate action.",
            "Repeated event rows require equivalent-version collapse/conflict audit.",
            "Investor dividend tax, record-date entitlement and all-event completeness uncertified.",
            "Rights, mergers, fractional shares and terminal recoveries not certified.",
            "Adjusted units only; no cash dividend or split postings.",
        ],
    )


HOLDING_SCHEMA = pa.schema(
    [
        ("date", pa.string()),
        ("lot_id", pa.string()),
        ("symbol", pa.string()),
        ("cohort", pa.string()),
        ("units", pa.float64()),
        ("original_weight", pa.float64()),
        ("requested_date", pa.string()),
        ("last_observed_price", pa.float64()),
        ("last_observed_date", pa.string()),
        ("mark_price", pa.float64()),
        ("mark_source", pa.string()),
        ("marked_value", pa.float64()),
    ]
)
ORDER_SCHEMA = pa.schema(
    [
        ("date", pa.string()),
        ("lot_id", pa.string()),
        ("symbol", pa.string()),
        ("cohort", pa.string()),
        ("requested_date", pa.string()),
        ("side", pa.string()),
        ("original_weight", pa.float64()),
        ("budget", pa.float64()),
        ("units", pa.float64()),
        ("requested_units", pa.float64()),
        ("price", pa.float64()),
        ("notional", pa.float64()),
        ("fee", pa.float64()),
        ("status", pa.string()),
        ("reason", pa.string()),
    ]
)


class AuditSink:
    def __init__(self, path, initial):
        path.mkdir()
        self.path = path
        self.verifier = LedgerVerifier(initial)
        self.daily = []
        self.holdings = []
        self.orders = []
        self.reasons = Counter()
        self.fills = Counter()
        self.delays = []
        self.rows = Counter()
        self.hw = pq.ParquetWriter(path / "holdings.parquet", HOLDING_SCHEMA, compression="zstd")
        self.ow = pq.ParquetWriter(path / "orders.parquet", ORDER_SCHEMA, compression="zstd")
        self.last_holdings = []
        self.date_index = {}

    def __call__(self, daily, holdings, orders):
        self.verifier.check(daily, holdings, orders)
        self.date_index[daily["date"]] = len(self.daily)
        self.daily.append(daily)
        self.last_holdings = holdings
        self.holdings.extend(holdings)
        self.orders.extend(orders)
        self.rows["holdings"] += len(holdings)
        self.rows["orders"] += len(orders)
        for o in orders:
            if o["reason"]:
                self.reasons[o["side"] + ":" + o["reason"]] += 1
            else:
                self.fills[o["side"]] += 1
                if o["side"] == "sell":
                    self.delays.append(
                        self.date_index[o["date"]] - self.date_index[o["requested_date"]]
                    )
        if len(self.daily) % 20 == 0:
            self.flush()

    def flush(self):
        if self.holdings:
            self.hw.write_table(pa.Table.from_pylist(self.holdings, schema=HOLDING_SCHEMA))
            self.holdings.clear()
        if self.orders:
            self.ow.write_table(pa.Table.from_pylist(self.orders, schema=ORDER_SCHEMA))
            self.orders.clear()

    def close(self):
        self.flush()
        self.hw.close()
        self.ow.close()
        pd.DataFrame(self.daily).to_csv(self.path / "daily.csv", index=False)
        pd.DataFrame(self.last_holdings, columns=HOLDING_SCHEMA.names).to_csv(
            self.path / "terminal_holdings.csv", index=False
        )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-run", type=Path, required=True)
    p.add_argument("--dividend", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--pilot", action="store_true")
    p.add_argument(
        "--scenarios",
        nargs="+",
        default=["touch10", "close10", "touch0", "touch30"],
        choices=["touch10", "close10", "touch0", "touch30"],
    )
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.is_relative_to(repo) or output.exists():
        raise ValueError("output must be a new external directory")
    receipt_path = args.source_run / "receipt.json"
    receipt = json.loads(receipt_path.read_text())
    members_path = args.source_run / "private_factor_members.parquet"
    if digest(members_path) != receipt["outputs"][members_path.name]:
        raise ValueError("frozen member hash mismatch")
    paths = receipt["arguments"]
    calendar_path = Path(paths["calendar"])
    if digest(calendar_path) != receipt["inputs"][str(calendar_path)]:
        raise ValueError("frozen calendar hash mismatch")
    prices = Path(paths["daily_clean"])
    manifest = prices / "manifest.yml"
    if digest(manifest) != receipt["inputs"][str(manifest)]:
        raise ValueError("frozen price manifest hash mismatch")
    columns = [
        "ts_code",
        "formation_date",
        "entry_date",
        "endpoint_date",
        "group",
        "metric",
        "quintile",
        "delist_date",
    ]
    members = pd.read_parquet(members_path, columns=columns)
    members = members.loc[
        members["group"].eq("all_market") & members.metric.isin(["pb_parent", "pe_deducted_proxy"])
    ].copy()
    if members.duplicated(["metric", "entry_date", "ts_code"]).any():
        raise ValueError("duplicate member identity")
    if not members.formation_date.lt(members.entry_date).all():
        raise ValueError("signal not strictly before entry")
    calendar = pd.read_parquet(calendar_path)
    sessions = sorted(
        calendar.loc[calendar.exchange.eq("SSE") & calendar.is_open.eq(1), "cal_date"].astype(str)
    )
    action = action_audit(args.dividend, members)
    if args.pilot:
        members = members.loc[members.metric.eq("pb_parent") & members.quintile.eq(1)]
        dates = sorted(members.entry_date.unique())[:3]
        members = members.loc[members.entry_date.isin(dates)].sort_values("ts_code")
        members = members.groupby("entry_date", group_keys=False).head(12)
    end = members.endpoint_date.max()
    final_ix = sessions.index(end)
    days = [d for d in sessions if members.entry_date.min() <= d <= sessions[final_ix + 20]]
    inputs = {
        str(x): digest(x)
        for x in [receipt_path, members_path, calendar_path, manifest, args.dividend]
    }
    source_files = [
        Path(__file__),
        repo / "src/market_research/studies/grouped_valuation_ledger.py",
        repo / "tests/test_grouped_valuation_ledger.py",
        repo / "uv.lock",
    ]
    source_hashes = {str(x.relative_to(repo)): digest(x) for x in source_files}
    output.mkdir(parents=True)
    write_json(output / "action_audit.json", action)
    write_json(
        output / "started.json",
        dict(
            pid=os.getpid(),
            started_utc=datetime.now(timezone.utc).isoformat(),
            arguments={k: str(v) for k, v in vars(args).items()},
            source_hashes=source_hashes,
        ),
    )
    summaries = []
    configs = {
        "touch10": ("any_touch", 10.0),
        "close10": ("close_flag", 10.0),
        "touch0": ("any_touch", 0.0),
        "touch30": ("any_touch", 30.0),
    }
    price_cols = [
        "ts_code",
        "trade_date",
        "adj_close",
        "close",
        "high",
        "low",
        "up_limit",
        "down_limit",
        "amount",
        "is_suspended",
        "is_limit_up",
        "is_limit_down",
    ]
    for (metric, q), block in members.groupby(["metric", "quintile"], sort=True):
        names = sorted(block.ts_code.unique())
        price_frames = []
        missing_files = []
        for name in names:
            f = prices / "data" / f"{name}.parquet"
            if not f.exists():
                missing_files.append(name)
                continue
            inputs.setdefault(str(f), digest(f))
            price_frames.append(
                pd.read_parquet(
                    f,
                    columns=price_cols,
                    filters=[("trade_date", ">=", days[0]), ("trade_date", "<=", days[-1])],
                )
            )
        daily_prices = {d: {} for d in days}
        for frame in price_frames:
            for r in frame.itertuples(index=False, name=None):
                symbol, day, *rest = r
                if day in daily_prices:
                    if symbol in daily_prices[day]:
                        raise ValueError("duplicate daily price identity")
                    daily_prices[day][symbol] = dict(zip(price_cols[2:], rest))
        del price_frames
        cohorts = {d: sorted(b.ts_code.tolist()) for d, b in block.groupby("entry_date")}
        delists = dict(
            block.dropna(subset=["delist_date"])[["ts_code", "delist_date"]]
            .drop_duplicates()
            .values
        )
        for scenario in args.scenarios:
            policy, fee = configs[scenario]
            key = f"{metric}_q{q}_{scenario}"
            print("ledger_start", key, "names", len(names), "days", len(days), flush=True)
            sink = AuditSink(output / key, 1_000_000.0)
            try:
                run_ledger(
                    days,
                    lambda d: daily_prices[d],
                    cohorts,
                    delist_dates=delists,
                    fee_bps=fee,
                    fill_policy=policy,
                    liquidation_date=end,
                    sink=sink,
                )
            finally:
                sink.close()
            final = sink.daily[-1]
            endpoint = next(x for x in sink.daily if x["date"] == end)
            summary = dict(
                portfolio=key,
                metric=metric,
                quintile=int(q),
                scenario=scenario,
                cohorts=len(cohorts),
                original_member_months=len(block),
                unique_names=len(names),
                sessions=len(days),
                entry_date=days[0],
                liquidation_date=end,
                last_date=days[-1],
                missing_symbol_files=len(missing_files),
                strict_nav_days=sum(x["strict_nav"] is not None for x in sink.daily),
                final=final,
                liquidation_endpoint=endpoint,
                zero_unresolved_total_return=final["zero_unresolved_nav"] / 1_000_000.0 - 1,
                strict_total_return=final["strict_nav"] / 1_000_000.0 - 1
                if final["strict_nav"] is not None
                else None,
                reasons=dict(sink.reasons),
                filled_orders=dict(sink.fills),
                delayed_sales=sum(x > 0 for x in sink.delays),
                max_exit_delay_sessions=max(sink.delays, default=0),
                max_cash_replay_error=sink.verifier.max_cash_error,
                rows=dict(sink.rows),
                max_pending_exit_lots=max(x["pending_exit_lots"] for x in sink.daily),
                raw_share_ready=False,
                revision_safe=False,
            )
            write_json(output / key / "summary.json", summary)
            summaries.append(summary)
            print(
                "ledger_done",
                key,
                "cash_error",
                sink.verifier.max_cash_error,
                "unresolved",
                final["unresolved_lots"],
                flush=True,
            )
    # Detect changed source files/inputs before sealing the reproducible run.
    for path, sha in inputs.items():
        if digest(path) != sha:
            raise ValueError(f"input changed during run: {path}")
    for rel, sha in source_hashes.items():
        if digest(repo / rel) != sha:
            raise ValueError("code changed during run")
    write_json(
        output / "summary.json",
        dict(
            status="completed_unpublished_proxy_checkpoint",
            pilot=args.pilot,
            portfolios=summaries,
            raw_share_ready=False,
            revision_safe=False,
            warning="Adjusted-unit hypothetical ledger, not realized returns or trading assurance.",
        ),
    )
    artifacts = {str(x.relative_to(output)): digest(x) for x in output.rglob("*") if x.is_file()}
    write_json(
        output / "receipt.json",
        dict(
            schema_version="grouped_valuation_ledger.v1",
            status="completed_unpublished_proxy_checkpoint",
            generated_utc=datetime.now(timezone.utc).isoformat(),
            git_head=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=repo, text=True
            ).strip(),
            inputs=inputs,
            source_hashes=source_hashes,
            outputs=artifacts,
            args={k: str(v) for k, v in vars(args).items()},
            resource_policy="single process, one basket quote cache, 20-session parquet buffers; BLAS=1",
            raw_share_ready=False,
            revision_safe=False,
        ),
    )
    print("completed", output, flush=True)


if __name__ == "__main__":
    main()
