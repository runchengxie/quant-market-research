from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from scripts.audit_liquidity_followups import audit_dates


def write_parquet(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path)


def test_exchange_drilldown_counts_missing_and_mismatched_rows_without_symbols(tmp_path: Path):
    minute = tmp_path / "minute"
    daily = tmp_path / "daily"
    day = "20241128"
    write_parquet(
        minute / f"trade_date={day}" / "part-00000.parquet",
        [
            {"ts_code": "111111.SH", "trade_time": datetime(2024, 11, 28, 9, 30), "amount": 1000.0},
            {"ts_code": "920001.BJ", "trade_time": datetime(2024, 11, 28, 9, 30), "amount": 900.0},
        ],
    )
    write_parquet(
        daily / f"trade_date={day}" / "part.parquet",
        [
            {"ts_code": "111111.SH", "amount": 1.0},
            {"ts_code": "920001.BJ", "amount": 1.0},
            {"ts_code": "920002.BJ", "amount": 2.0},
        ],
    )
    suspensions = tmp_path / "suspend.parquet"
    write_parquet(
        suspensions,
        [{"ts_code": "920002.BJ", "trade_date": day, "suspend_timing": "S", "suspend_type": "S"}],
    )

    result = audit_dates(minute, daily, suspensions, [day])

    assert result["universe_denominator"]["status"] == "unavailable"
    assert result["observed_rows"]["daily_zero_turnover_rows"] == 0
    assert result["observed_rows"]["daily_rows"] == 3
    exchanges = {row["exchange"]: row for row in result["dates"][0]["exchanges"]}
    assert exchanges["BJ"]["daily_only"] == 1
    assert exchanges["BJ"]["daily_only_suspended"] == 1
    assert exchanges["BJ"]["matched_rel_diff_over_1pct"] == 1
    assert "920001.BJ" not in str(result)
    assert "111111.SH" not in str(result)
