#!/usr/bin/env python3
"""Build month-weighted stability summaries from reviewed liquidity features."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd

from market_research.liquidity_stability import summarize_monthly_stability


MARKETS = ("US", "HK", "A-share", "JP")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output == repo or repo in output.parents:
        raise ValueError("research outputs must stay outside repository")
    files = {market: args.features / f"features-{market}.parquet" for market in MARKETS}
    signatures = {m: (p.stat().st_size, p.stat().st_mtime_ns) for m, p in files.items()}
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='1GB'")
    monthly = []
    for market, path in files.items():
        literal = str(path).replace("'", "''")
        query = f"""
          WITH daily AS (
            SELECT date_trunc('month', date)::DATE AS month_start,
                   year(date)::INTEGER AS year,
                   CASE WHEN market_cap_usd < 1e7 THEN '< $10m'
                        WHEN market_cap_usd < 1e8 THEN '$10m-$100m'
                        WHEN market_cap_usd < 1e9 THEN '$100m-$1bn'
                        WHEN market_cap_usd < 1e10 THEN '$1bn-$10bn'
                        ELSE '>= $10bn' END AS bucket,
                   date,
                   median(adv20_usd) AS daily_adv_median,
                   median(adv20_usd / NULLIF(market_cap_usd, 0)) AS daily_turnover_rate_median,
                   count(*)::BIGINT AS security_days
            FROM read_parquet('{literal}')
            WHERE eligible AND market_cap_usd >= 0 AND adv20_usd >= 0
            GROUP BY ALL
          )
          SELECT '{market}' AS market, year, bucket,
                 strftime(month_start, '%Y-%m') AS month,
                 median(daily_adv_median) AS monthly_adv_median,
                 median(daily_turnover_rate_median) AS monthly_turnover_rate_median,
                 sum(security_days)::BIGINT AS security_days
          FROM daily GROUP BY ALL ORDER BY year, bucket, month
        """
        monthly.append(con.execute(query).fetchdf())
    frame = pd.concat(monthly, ignore_index=True)
    result = {
        "schema_version": "liquidity.stability.v1",
        "method": {
            "aggregation": "daily cross-sectional median, then monthly median of daily medians, then annual distribution across monthly values",
            "uncertainty_band": "P25-P75 across observed monthly medians; descriptive temporal spread, not a confidence interval",
            "turnover_rate": "ADV20 USD / prior-session market capitalization USD",
            "pit_eligible": False,
            "cross_market_ranking": False,
            "scope": "eligible observed feature rows only; no absent or suspended securities imputed",
        },
        "input_receipts": [
            {"market": market, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for market, path in files.items()
        ],
        "summary": summarize_monthly_stability(frame),
    }
    if any(signatures[m] != (p.stat().st_size, p.stat().st_mtime_ns) for m, p in files.items()):
        raise RuntimeError("feature input changed during calculation")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"Wrote {len(result['summary'])} market-year-bucket stability cells")


if __name__ == "__main__":
    main()
