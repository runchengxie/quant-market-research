"""Build a public-safe capacity data-coverage summary from reviewed aggregates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path.name}")
    return value


def iso_date(value: str) -> str:
    return f"{value[:4]}-{value[4:6]}-{value[6:8]}" if len(value) == 8 and value.isdigit() else value


def build(
    liquidity: dict[str, Any],
    minute_audit: dict[str, Any],
    minute_receipt: dict[str, Any],
    calendar_receipt: dict[str, Any],
    execution: dict[str, Any],
) -> dict[str, Any]:
    latest = {row["market"]: row for row in liquidity["markets"]}
    profiles = liquidity["source_profiles"]
    periods = []
    for row in liquidity["periods"]:
        periods.append(
            {
                "period": row["period"],
                "start": row["common_start"],
                "end": row["common_end"],
                "common_dates": row["common_dates"],
                "markets": row["included_markets"],
            }
        )

    minute_summary = minute_receipt["summary"]
    audit_quality = minute_audit["quality"]
    snapshot_rows = sum(int(row["sampled_snapshots"]) for row in execution["audit"])
    usable_snapshot_rows = sum(int(row["valid_books"]) for row in execution["audit"])
    if usable_snapshot_rows > snapshot_rows:
        raise ValueError("valid L2 snapshots exceed the selected snapshot count")

    market_rows = []
    sources = {
        "US": "SimFin close × volume; turnover is a close-price proxy, not reported traded value. Sparse source date 2025-10-04 is excluded; latest eligible observation is 2025-10-03.",
        "HK": "RQData reported turnover in HKD; historical universe coverage remains unproven.",
        "A-share": "TuShare SH/SZ daily turnover; BSE excluded; prior-period status filters do not establish historical PIT.",
        "JP": "J-Quants daily traded value; market cap uses exploratory Yahoo share history.",
    }
    for name in ("US", "HK", "A-share", "JP"):
        profile = profiles[name]
        snapshot = latest[name]
        is_ashare = name == "A-share"
        market_rows.append(
            {
                "market": name,
                "daily": {
                    "start": profile["coverage_start"],
                    "end": profile["coverage_end"],
                    "latest": snapshot["as_of"],
                    "basis": sources[name],
                },
                "minute": (
                    {
                        "status": "available",
                        "start": iso_date(minute_summary["date_min"]),
                        "end": iso_date(minute_summary["date_max"]),
                        "sessions": minute_summary["dates"],
                        "rows": minute_summary["rows"],
                        "security_days": minute_summary["symbol_days"],
                        "calendar_gaps": int(calendar_receipt["remaining_calendar_gap_count"]),
                        "caveat": "Published TuShare operational version; nine exchange-calendar gaps remain and full native semantic rebaseline is incomplete.",
                    }
                    if is_ashare
                    else {
                        "status": "not_in_research_panel",
                        "caveat": "No minute source is included in this cross-market research panel.",
                    }
                ),
                "level2": (
                    {
                        "status": "sampled",
                        "snapshot_dates": len(execution["audit"]),
                        "snapshot_rows": snapshot_rows,
                        "usable_snapshot_rows": usable_snapshot_rows,
                        "event_dates": len(execution["event_audit"]),
                        "caveat": "Selected-date static snapshots only; event semantics and full-market coverage are not verified.",
                    }
                    if is_ashare
                    else {
                        "status": "not_in_research_panel",
                        "caveat": "No Level 2 source is included in this cross-market research panel.",
                    }
                ),
            }
        )

    return {
        "schema_version": "capacity-data-quality.v1",
        "generated_as_of": "2026-10-16",
        "daily_periods": periods,
        "markets": market_rows,
        "minute_daily_reconciliation": {
            "start": iso_date(minute_audit["coverage"]["date_min"]),
            "end": iso_date(minute_audit["coverage"]["date_max"]),
            "days": minute_audit["coverage"]["compared_days"],
            "matched_security_days": audit_quality["matched_security_days"],
            "daily_only_security_days": audit_quality["daily_only_security_days"],
            "minute_duplicate_keys": audit_quality["minute_duplicate_keys"],
            "invalid_amount_rows": audit_quality["minute_nonfinite_or_negative_amount_rows"]
            + audit_quality["daily_nonfinite_or_negative_amount_rows"],
            "median_daily_total_ratio": audit_quality["daily_total_ratio_quantiles"]["0.5"],
            "abs_diff_le_1_cny": audit_quality["matched_share_abs_diff_le_1_cny"],
            "abs_diff_le_100_cny": audit_quality["matched_share_abs_diff_le_100_cny"],
            "rel_diff_le_0_1pct": audit_quality["matched_share_rel_diff_le_0_1pct"],
            "rel_diff_over_1pct": audit_quality["matched_share_rel_diff_over_1pct"],
            "rel_diff_over_5pct": audit_quality["matched_share_rel_diff_over_5pct"],
            "rel_diff_over_10pct": audit_quality["matched_share_rel_diff_over_10pct"],
            "relative_diff_quantiles": audit_quality["matched_rel_diff_quantiles"],
            "daily_zero_turnover_rate": audit_quality["daily_zero_turnover_security_day_rate"],
            "yearly": minute_audit["by_year"],
            "total_ratio_quantiles": audit_quality["daily_total_ratio_quantiles"],
        },
        "intraday_concentration": {
            "days": minute_audit["coverage"]["compared_days"],
            "quantiles": {
                str(q): {
                    "top_5min_share": minute_audit["derived_diagnostics"]["market_top5min_share_by_day_quantiles"][str(q)],
                    "open_30min_share": minute_audit["derived_diagnostics"]["market_open30_share_by_day_quantiles"][str(q)],
                    "close_30min_share": minute_audit["derived_diagnostics"]["market_close30_share_by_day_quantiles"][str(q)],
                }
                for q in (0.5, 0.9, 0.99)
            },
        },
        "audit_receipts": {
            "minute_audit_sha256": hashlib.sha256(
                json.dumps(minute_audit, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest(),
            "minute_source_quality_status": minute_receipt.get("quality_status"),
            "full_minute_semantic_rebaseline_complete": calendar_receipt.get("full_dataset_semantic_rebaseline_complete"),
            "l2_measurement_evidence": execution["evidence"],
            "l2_actual_order_calibrated": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--liquidity", type=Path, required=True)
    parser.add_argument("--minute-audit", type=Path, required=True)
    parser.add_argument("--minute-receipt", type=Path, required=True)
    parser.add_argument("--calendar-receipt", type=Path, required=True)
    parser.add_argument("--execution", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(
        read_json(args.liquidity),
        read_json(args.minute_audit),
        read_json(args.minute_receipt),
        read_json(args.calendar_receipt),
        read_json(args.execution),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output.name}: {result['schema_version']}")


if __name__ == "__main__":
    main()
