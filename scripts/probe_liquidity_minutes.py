#!/usr/bin/env python3
"""Continuous-month recorded-clock sensitivity; does not certify bar intervals."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["features", "minute-root", "daily-root", "output"]:
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    if a.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("external outputs required")
    a.output.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.read_parquet(str(a.features)).create_view("f")
    days = (
        con.execute(
            "SELECT DISTINCT strftime(date,'%Y%m%d') FROM f WHERE date BETWEEN DATE '2025-01-01' AND DATE '2025-01-31' ORDER BY 1"
        )
        .fetchnumpy()["strftime(date, '%Y%m%d')"]
        .tolist()
    )
    rows = []
    receipts = []
    stock_days = []
    for day in days:
        minute = a.minute_root / f"trade_date={day}" / "part-00000.parquet"
        daily = a.daily_root / f"trade_date={day}" / "part.parquet"
        receipts.append(dict(date=day, minute_sha256=sha(minute), daily_sha256=sha(daily)))
        con.read_parquet(str(minute), hive_partitioning=False).create_view("m")
        con.read_parquet(str(daily), hive_partitioning=False).create_view("d")
        for table, keys in [("m", "ts_code,trade_time"), ("d", "ts_code")]:
            assert not con.execute(
                f"SELECT count(*) FROM (SELECT {keys} FROM {table} GROUP BY ALL HAVING count(*)>1)"
            ).fetchone()[0]
        assert not con.execute(
            "SELECT count(*) FROM m WHERE amount IS NULL OR NOT isfinite(amount) OR amount<0"
        ).fetchone()[0]
        t = "strftime(CAST(trade_time AS TIMESTAMP),'%H:%M')"
        assert not con.execute(
            f"SELECT count(*) FROM m WHERE strftime(CAST(trade_time AS TIMESTAMP),'%Y%m%d')<>? OR NOT ({t} BETWEEN '09:25' AND '11:30' OR {t} BETWEEN '13:00' AND '15:00')",
            [day],
        ).fetchone()[0]
        data = con.execute(
            f"""WITH sums AS (SELECT ts_code,count(*) bars,sum(amount) total,
          sum(amount) FILTER(WHERE {t}>='09:30' AND {t}<'10:00') open_a,
          sum(amount) FILTER(WHERE {t}>'09:30' AND {t}<='10:00') open_b,
          sum(amount) FILTER(WHERE {t}>='14:30' AND {t}<='15:00') close_a,
          sum(amount) FILTER(WHERE {t}>'14:30' AND {t}<='15:00') close_b,
          count(*) FILTER(WHERE {t}='09:30') edge_open,
          count(*) FILTER(WHERE {t}='15:00') edge_close
          FROM m GROUP BY ts_code)
          SELECT f.symbol,m.*,d.amount daily_amount FROM f LEFT JOIN sums m ON f.symbol=m.ts_code
          LEFT JOIN d ON f.symbol=d.ts_code WHERE f.eligible AND strftime(f.date,'%Y%m%d')=?""",
            [day],
        ).fetchdf()
        valid = (
            (data.bars >= 240)
            & (data.total > 0)
            & (data.daily_amount > 0)
            & (abs(data.total / (data.daily_amount * 1000) - 1) <= 0.01)
        )
        accepted = data.loc[valid].copy()
        assert len(accepted) > 0
        # Independently reconstruct every accepted stock-day using pandas from raw minute rows.
        m = pd.read_parquet(minute, columns=["ts_code", "trade_time", "amount"])
        m = m.loc[m.ts_code.isin(accepted.symbol)]
        clock = pd.to_datetime(m.trade_time).dt.strftime("%H:%M")
        total = m.groupby("ts_code").amount.sum()
        for key, mask in [
            ("open_a", (clock >= "09:30") & (clock < "10:00")),
            ("open_b", (clock > "09:30") & (clock <= "10:00")),
            ("close_a", (clock >= "14:30") & (clock <= "15:00")),
            ("close_b", (clock > "14:30") & (clock <= "15:00")),
        ]:
            expect = m.loc[mask].groupby("ts_code").amount.sum().reindex(accepted.symbol)
            assert np.allclose(
                accepted[key], expect.to_numpy(), equal_nan=True, rtol=1e-10, atol=0.01
            )
            accepted[key] = accepted[key] / accepted.total
        assert np.allclose(
            accepted.total, total.reindex(accepted.symbol).to_numpy(), rtol=1e-10, atol=0.01
        )
        accepted["date"] = day
        stock_days.append(accepted[["symbol", "date", "open_a", "open_b", "close_a", "close_b"]])
        rows.append(
            dict(
                date=day,
                candidates=len(data),
                accepted=len(accepted),
                excluded=int((~valid).sum()),
                open_edge_present=int((accepted.edge_open > 0).sum()),
                close_edge_present=int((accepted.edge_close > 0).sum()),
            )
        )
        print(day, len(accepted), "independently reconciled stock-days", flush=True)
    pooled = pd.concat(stock_days, ignore_index=True)
    pooled.to_parquet(a.output / "minute-windows.private.parquet", index=False)
    result = dict(
        schema_version="liquidity.minute-clock-probe.v1",
        month="2025-01",
        dates=len(rows),
        accepted_stock_days=len(pooled),
        feature_sha256=sha(a.features),
        quality=rows,
        source_receipts=receipts,
        reviewed=True,
        review_method="All accepted window amounts and daily totals independently regrouped from raw minute rows with pandas after DuckDB construction.",
        producer_sha256=sha(Path(__file__)),
        native_interval_semantics_verified=False,
        interpretation="Recorded-clock boundary sensitivity in one consecutive month. Differences do not identify the correct interval convention. Not representative of other months, years or actual fills.",
        sources=["https://tushare.pro/document/2?doc_id=370"],
        statistics={
            k: dict(observations=int(pooled[k].notna().sum()), median=float(pooled[k].median()))
            for k in ["open_a", "open_b", "close_a", "close_b"]
        },
        boundary_difference=dict(
            open_median=float((pooled.open_b - pooled.open_a).median()),
            open_absolute_p95=float((pooled.open_b - pooled.open_a).abs().quantile(0.95)),
            close_median=float((pooled.close_b - pooled.close_a).median()),
        ),
    )
    (a.output / "minute-probe.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    print("Continuous-month minute probe reviewed", flush=True)


if __name__ == "__main__":
    main()
