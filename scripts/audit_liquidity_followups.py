"""Drill into selected minute/daily mismatches by exchange, without publishing symbols."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pyarrow.parquet as pq


def _exchange(ts_code: str) -> str:
    suffix = ts_code.rsplit(".", 1)[-1]
    return suffix if suffix in {"SH", "SZ", "BJ"} else "other"


def audit_dates(
    minute_root: Path, daily_root: Path, suspension_file: Path, dates: list[str]
) -> dict[str, object]:
    if not dates or any(not re.fullmatch(r"\d{8}", value) for value in dates):
        raise ValueError("dates must be a nonempty list of YYYYMMDD values")
    if len(set(dates)) != len(dates):
        raise ValueError("dates must be unique")
    suspension = pq.read_table(
        suspension_file, columns=["ts_code", "trade_date"]
    ).to_pandas()
    daily_row_count = 0
    daily_zero_count = 0
    date_results = []

    for date in sorted(dates):
        minute_path = minute_root / f"trade_date={date}" / "part-00000.parquet"
        daily_path = daily_root / f"trade_date={date}" / "part.parquet"
        if not minute_path.is_file() or not daily_path.is_file():
            raise FileNotFoundError(f"both minute and daily partitions are required for {date}")
        minute = pq.read_table(
            minute_path, columns=["ts_code", "trade_time", "amount"]
        ).to_pandas()
        daily = pq.read_table(daily_path, columns=["ts_code", "amount"]
                              ).to_pandas()
        if minute.duplicated(["ts_code", "trade_time"]).any():
            raise ValueError(f"duplicate minute keys in {date}")
        if daily.duplicated(["ts_code"]).any():
            raise ValueError(f"duplicate daily security keys in {date}")
        daily_row_count += len(daily)
        daily_zero_count += int((daily["amount"] == 0).sum())

        minute_by_security = minute.groupby("ts_code", sort=False).agg(
            minute_amount=("amount", "sum"), minute_rows=("amount", "size")
        )
        daily_by_security = daily.set_index("ts_code")["amount"].rename(
            "daily_amount_thousand_cny"
        )
        joined = daily_by_security.to_frame().join(minute_by_security, how="outer")
        joined["exchange"] = joined.index.map(_exchange)
        joined["daily_amount_cny"] = joined["daily_amount_thousand_cny"] * 1000.0
        joined["matched"] = joined["daily_amount_cny"].notna() & joined[
            "minute_amount"
        ].notna()
        joined["daily_only"] = joined["daily_amount_cny"].notna() & joined[
            "minute_amount"
        ].isna()
        joined["relative_difference"] = (
            (joined["minute_amount"] - joined["daily_amount_cny"]).abs()
            / joined["daily_amount_cny"].abs().clip(lower=1.0)
        )
        suspended_codes = set(
            suspension.loc[suspension["trade_date"] == date, "ts_code"].astype(str)
        )
        joined["daily_only_suspended"] = joined.index.isin(suspended_codes) & joined[
            "daily_only"
        ]

        exchanges = []
        for exchange, group in joined.groupby("exchange", sort=True):
            daily_amount = group["daily_amount_cny"].sum(min_count=1)
            missing_amount = group.loc[group["daily_only"], "daily_amount_cny"].sum()
            matched = group.loc[group["matched"]]
            over_one = matched["relative_difference"] > 0.01
            exchanges.append(
                {
                    "exchange": exchange,
                    "daily_rows": int(group["daily_amount_cny"].notna().sum()),
                    "minute_securities": int(group["minute_amount"].notna().sum()),
                    "matched": int(group["matched"].sum()),
                    "daily_only": int(group["daily_only"].sum()),
                    "daily_only_suspended": int(group["daily_only_suspended"].sum()),
                    "daily_only_amount_share": (
                        float(missing_amount / daily_amount) if daily_amount > 0 else None
                    ),
                    "matched_rel_diff_over_1pct": int(over_one.sum()),
                    "matched_rel_diff_over_1pct_share": (
                        float(over_one.mean()) if len(over_one) else None
                    ),
                    "median_matched_relative_difference": (
                        float(matched["relative_difference"].median())
                        if len(matched)
                        else None
                    ),
                    "p90_matched_relative_difference": (
                        float(matched["relative_difference"].quantile(0.9))
                        if len(matched)
                        else None
                    ),
                }
            )
        date_results.append(
            {
                "date": date,
                "daily_rows": len(daily),
                "minute_rows": len(minute),
                "daily_zero_turnover_rows": int((daily["amount"] == 0).sum()),
                "daily_only": int(joined["daily_only"].sum()),
                "exchanges": exchanges,
            }
        )

    return {
        "schema_version": "liquidity_followup_audit.v1",
        "sample_dates": sorted(dates),
        "selection": "Targeted dates selected from the prior full reconciliation for low total ratios or high daily-only counts; not a random sample.",
        "method": {
            "daily_amount_to_cny": "daily.amount * 1000",
            "minute_amount_unit": "CNY",
            "key": "trade date × security; exchange from canonical suffix",
            "security_identifiers_published": False,
        },
        "observed_rows": {
            "daily_rows": daily_row_count,
            "daily_zero_turnover_rows": daily_zero_count,
            "daily_zero_turnover_row_rate": daily_zero_count / daily_row_count,
        },
        "universe_denominator": {
            "status": "unavailable",
            "zero_turnover_rate": None,
            "reason": "A complete point-in-time listed-security universe is not supplied to this audit. Zero counts cover returned daily rows only.",
        },
        "dates": date_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minute-root", type=Path, required=True)
    parser.add_argument("--daily-root", type=Path, required=True)
    parser.add_argument("--suspensions", type=Path, required=True)
    parser.add_argument("--dates", nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit_dates(args.minute_root, args.daily_root, args.suspensions, args.dates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {args.output.name}: {len(result['dates'])} targeted sessions")


if __name__ == "__main__":
    main()
