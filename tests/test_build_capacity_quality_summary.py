from __future__ import annotations

from scripts.build_capacity_quality_summary import build


def test_builds_allowlisted_coverage_and_quality_aggregates() -> None:
    names = ["US", "HK", "A-share", "JP"]
    liquidity = {
        "markets": [{"market": name, "as_of": "2025-10-03"} for name in names],
        "source_profiles": {
            name: {"coverage_start": "2019-11-01", "coverage_end": "2026-10-15"}
            for name in names
        },
        "periods": [
            {
                "period": "2026 YTD",
                "common_start": "2026-01-05",
                "common_end": "2026-04-30",
                "common_dates": 71,
                "included_markets": ["HK", "A-share", "JP"],
            }
        ],
    }
    minute_audit = {
        "coverage": {"date_min": "20220715", "date_max": "20261013", "compared_days": 1019},
        "quality": {
            "matched_security_days": 5_411_206,
            "daily_only_security_days": 2_084,
            "minute_duplicate_keys": 0,
            "minute_nonfinite_or_negative_amount_rows": 0,
            "daily_nonfinite_or_negative_amount_rows": 0,
            "daily_total_ratio_quantiles": {"0.5": 0.9997, "0.01": 0.9965},
            "matched_share_abs_diff_le_1_cny": 0.9,
            "matched_share_abs_diff_le_100_cny": 0.97,
            "matched_share_rel_diff_le_0_1pct": 0.97,
            "matched_share_rel_diff_over_1pct": 0.02,
            "matched_share_rel_diff_over_5pct": 0.001,
            "matched_share_rel_diff_over_10pct": 0.0002,
            "matched_rel_diff_quantiles": {"0.5": 0.00001},
            "daily_zero_turnover_security_day_rate": 0.0,
        },
        "derived_diagnostics": {
            "market_top5min_share_by_day_quantiles": {"0.5": 0.08, "0.9": 0.1, "0.99": 0.12},
            "market_open30_share_by_day_quantiles": {"0.5": 0.3, "0.9": 0.34, "0.99": 0.37},
            "market_close30_share_by_day_quantiles": {"0.5": 0.12, "0.9": 0.14, "0.99": 0.16},
        },
        "by_year": {"2022": {"matched_security_days": 10}},
    }
    minute_receipt = {
        "summary": {"date_min": "20220715", "date_max": "20261013", "dates": 1019, "rows": 1_304_100_646, "symbol_days": 5_411_206},
        "quality_status": "tushare_native_baseline_required",
    }
    calendar_receipt = {"remaining_calendar_gap_count": 9, "full_dataset_semantic_rebaseline_complete": False}
    execution = {
        "pooled": {"snapshots": 306_483},
        "audit": [{"sampled_snapshots": 311_395, "valid_books": 306_483}],
        "comparison": {"days": [20210104, 20260416]},
        "event_audit": {"20210104": {}, "20260416": {}},
        "evidence": "descriptive_historical_static_expansion",
        "actual_order_calibrated": False,
    }

    result = build(liquidity, minute_audit, minute_receipt, calendar_receipt, execution)

    assert result["daily_periods"][0]["markets"] == ["HK", "A-share", "JP"]
    ashare = next(row for row in result["markets"] if row["market"] == "A-share")
    assert ashare["minute"]["calendar_gaps"] == 9
    assert ashare["level2"]["snapshot_rows"] == 311_395
    assert ashare["level2"]["usable_snapshot_rows"] == 306_483
    assert result["minute_daily_reconciliation"]["matched_security_days"] == 5_411_206
    assert result["audit_receipts"]["full_minute_semantic_rebaseline_complete"] is False
    assert "/home/" not in str(result)
    assert "/mnt/" not in str(result)
