from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from scripts.audit_ashare_minute_daily import audit


def _write_partition(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path)


def test_reconciles_amount_units_and_keeps_unmatched_security_days(tmp_path: Path) -> None:
    minute_root = tmp_path / "minute"
    daily_root = tmp_path / "daily"
    date = "20260105"
    _write_partition(
        minute_root / f"trade_date={date}" / "part-00000.parquet",
        [
            {"ts_code": "A", "trade_time": datetime(2026, 1, 5, 9, 30), "amount": 600.0},
            {"ts_code": "A", "trade_time": datetime(2026, 1, 5, 9, 31), "amount": 400.0},
            {"ts_code": "B", "trade_time": datetime(2026, 1, 5, 9, 30), "amount": 1_000.0},
            {"ts_code": "C", "trade_time": datetime(2026, 1, 5, 9, 30), "amount": 2_000.0},
            {"ts_code": "C", "trade_time": datetime(2026, 1, 5, 9, 30), "amount": 2_000.0},
        ],
    )
    _write_partition(
        daily_root / f"trade_date={date}" / "part.parquet",
        [
            {"ts_code": "A", "amount": 1.0},
            {"ts_code": "B", "amount": 1.0},
            {"ts_code": "D", "amount": 0.0},
        ],
    )

    result = audit(minute_root, daily_root)

    assert result["coverage"] == {
        "date_min": date,
        "date_max": date,
        "compared_days": 1,
        "missing_daily_partitions": 0,
    }
    quality = result["quality"]
    assert quality["matched_security_days"] == 2
    assert quality["minute_duplicate_keys"] == 1
    assert quality["minute_only_security_days"] == 1
    assert quality["daily_only_security_days"] == 1
    assert quality["daily_zero_turnover_security_day_rate"] == 1 / 3
    assert quality["matched_share_abs_diff_le_1_cny"] == 1.0
    assert result["derived_diagnostics"]["market_top5min_share_by_day_quantiles"]["0.5"] == 1.0
