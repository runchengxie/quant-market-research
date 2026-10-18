#!/usr/bin/env python3
"""Build external, retrospective SH/SZ stress/cohort and sampled clock-window evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from market_research.liquidity_rebuild import BUCKET_LABELS
from market_research.liquidity_stress import (
    build_daily_panels,
    summarize_cohorts,
    summarize_stress,
    window_masks,
    validate_turnover,
)


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def write(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--features", type=Path, required=True)
    p.add_argument("--base", type=Path, required=True)
    p.add_argument("--minute-root", type=Path, required=True)
    p.add_argument("--daily-root", type=Path, required=True)
    p.add_argument("--date-audit", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if a.output.resolve().is_relative_to(repo):
        raise ValueError("research outputs must remain external")
    a.output.mkdir(parents=True, exist_ok=True)
    feature_sha = sha(a.features)
    base = json.loads(a.base.read_text())
    assert feature_sha == next(
        r["sha256"] for r in base["source_receipts"] if r["source_id"] == "a_sh_sz_features"
    )
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    con.execute("SET temp_directory='" + str(a.output / "spill").replace("'", "''") + "'")
    con.execute("SET max_temp_directory_size='20GiB'")
    con.read_parquet(str(a.features)).create_view("f")
    assert (
        con.execute(
            "SELECT count(*) FROM f WHERE market<>'A-share' OR symbol LIKE '%.BJ'"
        ).fetchone()[0]
        == 0
    )
    print("Building monthly stress and frozen cohorts", flush=True)
    monthly, cohorts = build_daily_panels(con, "f")
    monthly.to_parquet(a.output / "monthly.private.parquet", index=False)
    cohorts.to_parquet(a.output / "cohorts.private.parquet", index=False)
    audit = json.loads(a.date_audit.read_text())
    selected = []
    dates = [
        r["date"]
        for r in audit["dates"]
        if r["status"] == "compared"
        and r["duplicate_minute_keys"] == 0
        and 0.995 <= r["minute_amount_to_daily_amount_total_ratio"] <= 1.005
    ]
    for year in sorted({d[:4] for d in dates}):
        group = sorted(d for d in dates if d.startswith(year))
        selected += sorted({group[0], group[len(group) // 2], group[-1]})
    marks = ",".join("?" for _ in selected)
    feature_days = con.execute(
        f"SELECT symbol,date,eligible,market_cap_usd FROM f WHERE strftime(date,'%Y%m%d') IN ({marks})",
        selected,
    ).fetchdf()
    window_rows = []
    quality = []
    receipts = []

    def canonical(s):
        return s.str.fullmatch(r"(00\d{4}|30\d{4}|60\d{4}|68\d{4})\.(SH|SZ)") & ~s.isin(
            ["000022.SZ", "000043.SZ", "300114.SZ"]
        )

    for day in selected:
        minute_path = a.minute_root / f"trade_date={day}" / "part-00000.parquet"
        daily_path = a.daily_root / f"trade_date={day}" / "part.parquet"
        signatures = [(p.stat().st_size, p.stat().st_mtime_ns) for p in [minute_path, daily_path]]
        minute = (
            pq.ParquetFile(minute_path)
            .read(columns=["ts_code", "trade_time", "amount"])
            .to_pandas()
        )
        raw_rows = len(minute)
        minute = minute.loc[canonical(minute.ts_code)].copy()
        daily = pq.ParquetFile(daily_path).read(columns=["ts_code", "amount"]).to_pandas()
        daily = daily.loc[canonical(daily.ts_code)].copy()
        if minute.duplicated(["ts_code", "trade_time"]).any() or daily.ts_code.duplicated().any():
            raise ValueError("duplicate minute or daily keys")
        validate_turnover(minute.amount)
        validate_turnover(daily.amount)
        if minute.trade_time.dt.strftime("%Y%m%d").ne(day).any():
            raise ValueError("foreign timestamp date")
        clock = minute.trade_time.dt.hour * 60 + minute.trade_time.dt.minute
        if (~(((clock >= 565) & (clock <= 690)) | ((clock >= 780) & (clock <= 900)))).any():
            raise ValueError("unexpected minute clock")
        totals = minute.groupby("ts_code").agg(total=("amount", "sum"), bars=("amount", "size"))
        features = feature_days.loc[
            feature_days.date.eq(pd.Timestamp(day)) & feature_days.eligible
        ].set_index("symbol")
        x = features.join(totals).join(daily.set_index("ts_code").amount.rename("daily"))
        x["reason"] = np.select(
            [
                x.daily.isna(),
                x.total.isna(),
                (x.daily <= 0) | (x.total <= 0),
                x.bars < 240,
                ((x.total - x.daily * 1000).abs() / (x.daily * 1000)) > 0.01,
            ],
            [
                "missing_daily",
                "missing_minute",
                "nonpositive_total",
                "short_day",
                "amount_mismatch",
            ],
            default="accepted",
        )
        accepted = x.loc[x.reason.eq("accepted")].copy()
        accepted["bucket"] = np.searchsorted(
            [1e7, 1e8, 1e9, 1e10], accepted.market_cap_usd, side="right"
        )
        masks = window_masks(minute.trade_time)
        for window, mask in masks.items():
            amounts = minute.loc[mask].groupby("ts_code").amount.sum()
            # Absence of all bars in a window is missing, never zero-filled.
            z = accepted.join(amounts.rename("window_amount"))
            z["share"] = z.window_amount / z.total
            z["date"] = day
            z["year"] = int(day[:4])
            z["window"] = window
            window_rows.append(
                z[["date", "year", "bucket", "window", "share"]].reset_index(drop=True)
            )
        reasons = {str(k): int(v) for k, v in x.reason.value_counts().items()}
        assert sum(reasons.values()) == len(features)
        quality.append(
            dict(
                date=day,
                raw_minute_rows=raw_rows,
                sh_sz_minute_rows=len(minute),
                eligible_candidates=len(features),
                accepted=len(accepted),
                reasons=reasons,
            )
        )
        for file, (size, mtime) in zip([minute_path, daily_path], signatures, strict=True):
            assert (file.stat().st_size, file.stat().st_mtime_ns) == (size, mtime)
        receipts.append(
            dict(date=day, minute_sha256=sha(minute_path), daily_sha256=sha(daily_path))
        )
        print(day, len(accepted), "matched full-day observations", flush=True)
    windows = pd.concat(window_rows, ignore_index=True)
    windows.to_parquet(a.output / "windows.private.parquet", index=False)
    window_summary = []
    for (year, bucket, window), group in windows.groupby(["year", "bucket", "window"], sort=True):
        values = group.share.dropna()
        window_summary.append(
            dict(
                year=int(year),
                bucket=int(bucket),
                window=window,
                dates=int(group.date.nunique()),
                observations=len(values),
                missing_window_observations=int(group.share.isna().sum()),
                p25=float(values.quantile(0.25)) if len(values) else None,
                median=float(values.median()) if len(values) else None,
                p75=float(values.quantile(0.75)) if len(values) else None,
            )
        )
    assert sha(a.features) == feature_sha
    result = dict(
        schema_version="liquidity.stress-persistence.v1",
        market="A-share SH/SZ",
        historical_pit_eligible=False,
        actual_execution_calibrated=False,
        buckets=list(BUCKET_LABELS),
        feature_sha256=feature_sha,
        methods=dict(
            stress="Completed months; at least 10 and 80% active market dates; at least 6 eligible months/year/bucket. Bottom ceil(20% of months) by monthly median of daily cross-sectional ADV20 medians. Compare with remaining months within the same year.",
            cohorts="Freeze eligible size-bucket membership at each completed month-end. Require full next-20-source-session horizon; classify final membership, continuous usability in any group, and same-bucket continuity without replacing missing or ineligible rows. Frozen-cohort minimum observed median/baseline requires >=90% eligible coverage on every future session.",
            minutes="First/middle/last previously audited qualifying date per year, not random. SH/SZ eligible feature rows; unique same-date bars; >=240 recorded bars; positive turnover; minute sum within 1% of daily amount*1000. Window shares pool security-days; absent window records stay missing. Timestamp endpoints are recorded-clock filters, not verified bar-interval semantics.",
            clock_windows=dict(
                open30="09:30 <= t < 10:00",
                late_morning="10:00 <= t <= 11:30",
                afternoon="13:00 <= t <= 15:00",
                close30="14:30 <= t <= 15:00",
                core="10:00 <= t <= 11:30 or 13:00 <= t < 14:30",
            ),
            denominator="Full observed minute turnover, including any auction bars. Windows overlap; shares must not be summed.",
        ),
        stress=summarize_stress(monthly),
        cohorts=summarize_cohorts(cohorts),
        windows=window_summary,
        minute_quality=quality,
        source_receipts=receipts,
        date_audit_sha256=sha(a.date_audit),
        code_receipts={
            p.name: sha(p)
            for p in [Path(__file__), repo / "src/market_research/liquidity_stress.py"]
        },
    )
    write(a.output / "summary.proposed.json", result)
    print("Proposal ready for independent review", flush=True)


if __name__ == "__main__":
    main()
