"""Reconcile published A-share TuShare minute turnover to daily turnover.

The scan reads one date partition at a time and writes aggregate-only JSON.
Raw security-level comparisons are held in memory only for the current date.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq


def audit(minute_root: Path, daily_root: Path) -> dict[str, object]:
    parts = sorted(minute_root.glob("trade_date=*/part-00000.parquet"))
    if not parts:
        raise ValueError("minute root has no trade_date partitions")

    dates: list[dict[str, object]] = []
    abs_diffs: list[np.ndarray] = []
    rel_diffs: list[np.ndarray] = []
    yearly: dict[str, dict[str, object]] = {}
    duplicate_total = 0
    invalid_minute_rows = 0
    invalid_daily_rows = 0

    for minute_path in parts:
        date = minute_path.parent.name.split("=", 1)[1]
        daily_path = daily_root / f"trade_date={date}" / "part.parquet"
        if not daily_path.is_file():
            dates.append({"date": date, "status": "daily_partition_missing"})
            continue

        minute = pq.read_table(
            minute_path, columns=["ts_code", "trade_time", "amount"]
        ).to_pandas()
        daily = pq.read_table(daily_path, columns=["ts_code", "amount"]).to_pandas()
        duplicate_day = int(minute.duplicated(["ts_code", "trade_time"]).sum())
        duplicate_total += duplicate_day
        minute_amount = minute["amount"].to_numpy()
        daily_amount = daily["amount"].to_numpy()
        invalid_minute_rows += int(
            (~np.isfinite(minute_amount)).sum() + (minute_amount < 0).sum()
        )
        invalid_daily_rows += int(
            (~np.isfinite(daily_amount)).sum() + (daily_amount < 0).sum()
        )

        by_security = minute.groupby("ts_code", sort=False).agg(
            minute_amount=("amount", "sum"), minute_rows=("amount", "size")
        )
        daily_by_security = daily.set_index("ts_code")["amount"].rename(
            "daily_amount_thousand_cny"
        )
        joined = daily_by_security.to_frame().join(by_security, how="outer")
        matched = joined.dropna(
            subset=["daily_amount_thousand_cny", "minute_amount"]
        )
        expected = matched["daily_amount_thousand_cny"].to_numpy() * 1_000.0
        observed = matched["minute_amount"].to_numpy()
        absolute = np.abs(observed - expected)
        relative = absolute / np.maximum(np.abs(expected), 1.0)
        abs_diffs.append(absolute)
        rel_diffs.append(relative)
        year = date[:4]
        year_stats = yearly.setdefault(
            year,
            {
                "matched_security_days": 0,
                "daily_security_days": 0,
                "daily_only_security_days": 0,
                "minute_only_security_days": 0,
                "daily_zero_turnover_security_days": 0,
                "relative_diff_over_0_1pct": 0,
                "relative_diff_over_1pct": 0,
                "relative_diff_over_5pct": 0,
                "relative_diff_over_10pct": 0,
            },
        )
        year_stats["matched_security_days"] += len(matched)
        year_stats["daily_security_days"] += len(daily)
        year_stats["daily_only_security_days"] += int(
            joined["daily_amount_thousand_cny"].notna().sum() - len(matched)
        )
        year_stats["minute_only_security_days"] += int(
            joined["minute_amount"].notna().sum() - len(matched)
        )
        year_stats["daily_zero_turnover_security_days"] += int((daily_amount == 0).sum())
        for threshold, key in (
            (0.001, "relative_diff_over_0_1pct"),
            (0.01, "relative_diff_over_1pct"),
            (0.05, "relative_diff_over_5pct"),
            (0.10, "relative_diff_over_10pct"),
        ):
            year_stats[key] += int((relative > threshold).sum())

        clock = minute["trade_time"].dt.hour * 60 + minute["trade_time"].dt.minute
        bucket = (clock // 5).rename("bucket")
        five_minute = minute.groupby(bucket, sort=False)["amount"].sum().to_numpy()
        total = float(minute["amount"].sum())
        open_30 = float(minute.loc[(clock >= 570) & (clock < 600), "amount"].sum())
        close_30 = float(minute.loc[(clock >= 870) & (clock <= 900), "amount"].sum())
        dates.append(
            {
                "date": date,
                "status": "compared",
                "daily_securities": len(daily),
                "minute_securities": len(by_security),
                "matched_securities": len(matched),
                "daily_only": int(joined["daily_amount_thousand_cny"].notna().sum() - len(matched)),
                "minute_only": int(joined["minute_amount"].notna().sum() - len(matched)),
                "minute_rows": len(minute),
                "daily_zero_turnover": int((daily_amount == 0).sum()),
                "duplicate_minute_keys": duplicate_day,
                "matched_abs_diff_le_1_cny": int((absolute <= 1.0).sum()),
                "matched_abs_diff_le_100_cny": int((absolute <= 100.0).sum()),
                "matched_rel_diff_le_0_1pct": int((relative <= 0.001).sum()),
                "matched_rel_diff_over_1pct": int((relative > 0.01).sum()),
                "matched_rel_diff_over_5pct": int((relative > 0.05).sum()),
                "matched_rel_diff_over_10pct": int((relative > 0.10).sum()),
                "market_top5min_share": float(five_minute.max() / total) if total > 0 else None,
                "market_open30_share": open_30 / total if total > 0 else None,
                "market_close30_share": close_30 / total if total > 0 else None,
                "market_total_ratio": (
                    total / float(daily_amount.sum() * 1_000.0)
                    if daily_amount.sum() != 0
                    else None
                ),
            }
        )

    compared = [row for row in dates if row["status"] == "compared"]
    absolute = np.concatenate(abs_diffs) if abs_diffs else np.array([], dtype=float)
    relative = np.concatenate(rel_diffs) if rel_diffs else np.array([], dtype=float)
    matched_count = sum(int(row["matched_securities"]) for row in compared)
    daily_count = sum(int(row["daily_securities"]) for row in compared)

    def quantiles(values: np.ndarray, points: tuple[float, ...]) -> dict[str, float]:
        return {str(point): float(np.quantile(values, point)) for point in points}

    def weighted_share(key: str) -> float | None:
        denominator = sum(int(row["matched_securities"]) for row in compared)
        if not denominator:
            return None
        numerator = sum(int(row[key]) for row in compared)
        return numerator / denominator

    def day_quantiles(key: str) -> dict[str, float]:
        values = np.asarray([float(row[key]) for row in compared if row[key] is not None])
        return quantiles(values, (0.5, 0.9, 0.99)) if len(values) else {}

    return {
        "schema_version": "a_share_minute_daily_reconciliation.v1",
        "generated_as_of": "2026-10-16",
        "source_scope": {
            "market": "A-share SH/SZ/BJ",
            "granularity": "published TuShare 1m vs TuShare daily",
            "daily_amount_conversion": "daily.amount * 1000 CNY; minute.amount in CNY",
            "minute_date_partitions": len(parts),
        },
        "coverage": {
            "date_min": compared[0]["date"] if compared else None,
            "date_max": compared[-1]["date"] if compared else None,
            "compared_days": len(compared),
            "missing_daily_partitions": sum(row["status"] == "daily_partition_missing" for row in dates),
        },
        "quality": {
            "minute_duplicate_keys": duplicate_total,
            "minute_nonfinite_or_negative_amount_rows": invalid_minute_rows,
            "daily_nonfinite_or_negative_amount_rows": invalid_daily_rows,
            "matched_security_days": matched_count,
            "daily_only_security_days": sum(int(row["daily_only"]) for row in compared),
            "minute_only_security_days": sum(int(row["minute_only"]) for row in compared),
            "matched_abs_diff_cny_quantiles": quantiles(absolute, (0.5, 0.9, 0.99, 1.0)),
            "matched_rel_diff_quantiles": quantiles(relative, (0.5, 0.9, 0.99, 1.0)),
            "matched_share_abs_diff_le_1_cny": float((absolute <= 1.0).mean()) if len(absolute) else None,
            "matched_share_abs_diff_le_100_cny": float((absolute <= 100.0).mean()) if len(absolute) else None,
            "matched_share_rel_diff_le_0_1pct": float((relative <= 0.001).mean()) if len(relative) else None,
            "matched_share_rel_diff_over_1pct": float((relative > 0.01).mean()) if len(relative) else None,
            "matched_share_rel_diff_over_5pct": float((relative > 0.05).mean()) if len(relative) else None,
            "matched_share_rel_diff_over_10pct": float((relative > 0.10).mean()) if len(relative) else None,
            "daily_zero_turnover_security_day_rate": (
                sum(int(row["daily_zero_turnover"]) for row in compared) / daily_count
                if daily_count
                else None
            ),
            "daily_total_ratio_quantiles": quantiles(
                np.asarray([float(row["market_total_ratio"]) for row in compared if row["market_total_ratio"] is not None]),
                (0.01, 0.5, 0.99),
            ),
        },
        "derived_diagnostics": {
            "market_top5min_share_by_day_quantiles": day_quantiles("market_top5min_share"),
            "market_open30_share_by_day_quantiles": day_quantiles("market_open30_share"),
            "market_close30_share_by_day_quantiles": day_quantiles("market_close30_share"),
        },
        "by_year": yearly,
        "privacy": "aggregate only; no security identifiers or per-date detail in output",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minute-root", type=Path, required=True)
    parser.add_argument("--daily-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.minute_root, args.daily_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
