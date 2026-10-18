#!/usr/bin/env python3
"""Recompute local, retrospective liquidity evidence; emit no raw rows publicly."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from market_research.liquidity_rebuild import build_features, summarize_period
from market_research.liquidity_universe import normalize_a_share

MARKETS = ["US", "HK", "A-share", "JP"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def literal(value) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def key_check(con, table, keys):
    count = con.execute(
        f"SELECT count(*) FROM (SELECT {keys} FROM {table} GROUP BY ALL HAVING count(*)>1)"
    ).fetchone()[0]
    if count:
        raise ValueError(f"{table}: {count} duplicate join keys")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    repo = Path(__file__).resolve().parents[1]
    if output == repo or repo in output.parents:
        raise ValueError("research output must be outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(args.config.read_text())
    cutoff = date.fromisoformat(cfg["cutoff"])
    sources = {
        name: sorted(Path(p).resolve() for p in __import__("glob").glob(pattern))
        for name, pattern in cfg["sources"].items()
    }
    if any(not files for files in sources.values()):
        raise ValueError("every declared source must resolve to files")
    before = {
        str(p): (p.stat().st_size, p.stat().st_mtime_ns)
        for files in sources.values()
        for p in files
    }
    con = duckdb.connect()
    con.execute("SET threads=2")
    con.execute("SET memory_limit='1GB'")
    con.execute(f"SET temp_directory={literal(output / 'spill')}")
    fx_frame = pd.read_csv(sources["fx"][0], compression="zip")
    fx_frame.columns = fx_frame.columns.str.strip()
    fx_rows = []
    for currency in ["USD", "HKD", "CNY", "JPY"]:
        values = pd.to_numeric(fx_frame["USD"], errors="coerce") / pd.to_numeric(
            fx_frame[currency], errors="coerce"
        )
        fx_rows.append(
            pd.DataFrame(
                {
                    "date": pd.to_datetime(fx_frame["Date"]).dt.date,
                    "currency": currency,
                    "usd_per_native": values,
                }
            )
        )
    fx_data = pd.concat(fx_rows).dropna()
    con.register("fx_input", fx_data)
    con.execute("CREATE TABLE fx AS SELECT * FROM fx_input")
    profiles = {}
    files_out = []

    for market in MARKETS:
        print(f"{market}: normalizing read-only sources", flush=True)
        if market == "A-share":
            normalize_a_share(
                con, [str(p) for p in sources["a_clean"]],
                cutoff.strftime("%Y%m%d"), cfg.get("a_share_start", "20150105"),
            )
        elif market == "US":
            con.execute(
                """CREATE TABLE raw AS SELECT 'US' market,Ticker symbol,
              try_cast(Date AS DATE) date,'USD' currency,
              try_cast(Close AS DOUBLE)*try_cast(Volume AS DOUBLE) turnover,
              try_cast(Close AS DOUBLE)*try_cast("Shares Outstanding" AS DOUBLE) market_cap,
              coalesce(try_cast(Close AS DOUBLE)>0,false) eligible
              FROM read_csv(?,delim=';',header=true,all_varchar=true)
              WHERE Date>='2019-11-01' AND Date<=?""",
                [str(sources["us"][0]), str(cutoff)],
            )
        elif market == "HK":
            con.execute(
                "CREATE TABLE hk_daily AS SELECT * FROM read_parquet(?) WHERE trade_date>='20191101'",
                [[str(p) for p in sources["hk_daily"]]],
            )
            con.execute(
                "CREATE TABLE hk_value AS SELECT symbol,trade_date,hk_total_market_val FROM read_parquet(?) WHERE trade_date>='20191101'",
                [[str(p) for p in sources["hk_value"]]],
            )
            con.execute(
                "CREATE TABLE hk_master AS SELECT * FROM read_parquet(?)",
                [str(sources["hk_master"][0])],
            )
            key_check(con, "hk_value", "symbol,trade_date")
            key_check(con, "hk_master", "symbol")
            con.execute(
                """CREATE TABLE raw AS SELECT 'HK' market,d.symbol,
              try_strptime(d.trade_date,'%Y%m%d')::DATE date,'HKD' currency,
              d.total_turnover turnover,v.hk_total_market_val market_cap,
              coalesce(m.type='CS' AND try_strptime(d.trade_date,'%Y%m%d')::DATE>=try_cast(m.listed_date AS DATE)
                AND (try_cast(m.de_listed_date AS DATE) IS NULL OR try_strptime(d.trade_date,'%Y%m%d')::DATE<try_cast(m.de_listed_date AS DATE)),false) eligible
              FROM hk_daily d LEFT JOIN hk_value v USING(symbol,trade_date) LEFT JOIN hk_master m USING(symbol)
              WHERE d.trade_date<=?""",
                [cutoff.strftime("%Y%m%d")],
            )
            for table in ["hk_daily", "hk_value", "hk_master"]:
                con.execute(f"DROP TABLE {table}")
        else:
            con.execute(
                """CREATE TABLE jp_shares AS SELECT cast(date AS DATE) date,
              lpad(cast(symbol AS VARCHAR),5,'0') symbol,shares_outstanding
              FROM read_parquet(?) WHERE date>='2019-11-01' """,
                [str(sources["jp_shares"][0])],
            )
            con.execute(
                """CREATE TABLE jp_master AS SELECT try_strptime(cast(date AS VARCHAR),'%Y%m%d')::DATE date,
              lpad(cast(ticker AS VARCHAR),5,'0') symbol,try_cast(Mkt AS INTEGER) market_code
              FROM read_parquet(?) WHERE date>=20191101""",
                [str(sources["jp_master"][0])],
            )
            key_check(con, "jp_shares", "symbol,date")
            key_check(con, "jp_master", "symbol,date")
            con.execute(
                """CREATE TABLE raw AS SELECT 'JP' market,lpad(d.Code,5,'0') symbol,
              d.Date date,'JPY' currency,d.Va turnover,d.C*s.shares_outstanding market_cap,
              coalesce(m.market_code IN (101,102,104,106,107,111,112,113),false) eligible
              FROM read_parquet(?,union_by_name=true) d
              LEFT JOIN jp_shares s ON s.symbol=lpad(d.Code,5,'0') AND s.date=d.Date
              LEFT JOIN jp_master m ON m.symbol=lpad(d.Code,5,'0') AND m.date=d.Date
              WHERE d.Date>='2019-11-01' AND d.Date<=?""",
                [[str(p) for p in sources["jp_daily"]], cutoff],
            )
            con.execute("DROP TABLE jp_shares")
            con.execute("DROP TABLE jp_master")
        build_features(con, "raw", "fx", "features_market", minimum_session_stocks=100)
        profile = con.execute("""SELECT count(*),count(DISTINCT symbol),min(date),max(date),
          count_if(eligible) FROM features_market""").fetchone()
        reasons = dict(
            con.execute("""SELECT coalesce(exclusion_reason,'included'),count(*)
          FROM features_market GROUP BY exclusion_reason""").fetchall()
        )
        profiles[market] = dict(
            source_rows=profile[0],
            observed_stocks=profile[1],
            coverage_start=str(profile[2]),
            coverage_end=str(profile[3]),
            eligible_observations=profile[4],
            exclusions=reasons,
            duplicate_keys=0,
        )
        dest = output / f"features-{market}.parquet"
        con.execute(f"COPY features_market TO {literal(dest)} (FORMAT PARQUET, COMPRESSION ZSTD)")
        files_out.append(dest)
        print(
            f"{market}: {profile[0]:,} source rows; {profile[4]:,} eligible observations",
            flush=True,
        )
        con.execute("DROP TABLE features_market")
        con.execute("DROP TABLE raw")
    con.execute(
        "CREATE VIEW features AS SELECT * FROM read_parquet(["
        + ",".join(literal(p) for p in files_out)
        + "])"
    )
    latest = []
    for market in MARKETS:
        end = con.execute(
            "SELECT max(date) FROM features WHERE market=? AND eligible", [market]
        ).fetchone()[0]
        if end:
            latest.extend(summarize_period(con, "features", end, end, [market])["markets"])
    common = con.execute("""SELECT date FROM features WHERE eligible GROUP BY date
      HAVING count(DISTINCT market)=4 ORDER BY date DESC LIMIT 1""").fetchone()
    periods = []
    if common:
        row = summarize_period(con, "features", common[0], common[0], MARKETS)
        row.update(period="common snapshot", status="derived")
        periods.append(row)
    for label, start, end in [
        ("2020-2024", date(2020, 1, 1), date(2024, 12, 31)),
        ("2025", date(2025, 1, 1), date(2025, 12, 31)),
        ("2026 YTD", date(2026, 1, 1), cutoff),
    ]:
        row = summarize_period(con, "features", start, end, MARKETS)
        row.update(
            period=label,
            status="incomplete"
            if row["missing_markets"]
            or (
                label != "2020-2024"
                and row["common_end"]
                and (end - date.fromisoformat(row["common_end"])).days > 7
            )
            else "derived",
        )
        periods.append(row)
    print("Hashing input versions and checking source stability", flush=True)
    public_receipts = []
    private_receipts = {}
    for name, files in sources.items():
        records = []
        digest = hashlib.sha256()
        for index, path in enumerate(files):
            signature = (path.stat().st_size, path.stat().st_mtime_ns)
            if signature != before[str(path)]:
                raise RuntimeError(f"input changed during run: source={name}")
            checksum = sha256(path)
            if (path.stat().st_size, path.stat().st_mtime_ns) != signature:
                raise RuntimeError(f"input changed while hashing: source={name}")
            digest.update(f"{index}:{path.name}:{signature[0]}:{checksum}\n".encode())
            records.append(
                dict(path=str(path), bytes=signature[0], mtime_ns=signature[1], sha256=checksum)
            )
        private_receipts[name] = records
        public_receipts.append(
            dict(
                source_id=name,
                files=len(files),
                bytes=sum(r["bytes"] for r in records),
                sha256=digest.hexdigest(),
            )
        )
    code_receipts = {
        name: sha256(path)
        for name, path in [
            ("runner", Path(__file__)),
            ("features", repo / "src/market_research/liquidity_rebuild.py"),
        ]
    }
    (output / "executed-code").mkdir(exist_ok=True)
    import shutil

    for path in [Path(__file__), repo / "src/market_research/liquidity_rebuild.py"]:
        shutil.copy2(path, output / "executed-code" / path.name)
    summary = dict(
        code_receipts=code_receipts,
        schema_version="liquidity.rebuilt.v1",
        generated_on=str(date.today()),
        method=dict(
            roll_days=20,
            metric="lagged_ADV20_mean",
            currency="USD",
            source_project="quant-market-research",
            snapshot_note="Latest snapshots differ by market; common snapshot uses one shared trading date",
            market_cap_anchor="prior contiguous market session",
            feature_lag_sessions=1,
            minimum_session_stocks=100,
            calendar_method="source dates with at least 100 observed securities; sparse dates excluded before rolling features",
            fx_method="ECB reference USD/native cross rate, latest strictly earlier publication date, maximum age 7 calendar days",
            zero_and_missing="Observed zero turnover included; missing market sessions invalidate the 20-session window",
            historical_pit_eligible=False,
        ),
        markets=latest,
        periods=periods,
        source_profiles=profiles,
        source_receipts=public_receipts,
        caveats=[
            "日股市值使用Yahoo历史股数侧表，覆盖不完整且未证明历史修订安全，只作探索性比较。",
            "共同日期只统一观察时间，不会消除各来源证券范围、估值和状态记录的差异。",
            "本结果是可复算的回顾性流动性描述，不是策略容量、真实成交或历史PIT证明。",
        ],
    )
    (output / "private-input-receipt.json").write_text(json.dumps(private_receipts, indent=2))
    (output / "summary.proposed.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    print("Proposed aggregates ready for independent review", flush=True)


if __name__ == "__main__":
    main()
