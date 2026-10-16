from datetime import date, timedelta

import duckdb
import pandas as pd
import pytest

from market_research.liquidity_rebuild import build_features, summarize_period


def fixture_connection():
    con = duckdb.connect()
    rows = []
    for market in ["A-share", "US"]:
        for day in range(24):
            rows.append(
                dict(
                    market=market,
                    symbol="one",
                    date=date(2025, 1, 1) + timedelta(days=day),
                    currency="CNY" if market == "A-share" else "USD",
                    turnover=float(day + 1) * 100,
                    market_cap=70000000.0,
                    eligible=True,
                )
            )
    raw = pd.DataFrame(rows)
    fx = pd.DataFrame(
        [
            dict(
                date=date(2024, 12, 31) + timedelta(days=day),
                currency=currency,
                usd_per_native=rate,
            )
            for day in range(25)
            for currency, rate in [("CNY", 1 / 7), ("USD", 1.0)]
        ]
    )
    con.register("raw_df", raw)
    con.register("fx_df", fx)
    con.execute("CREATE TABLE raw AS SELECT * FROM raw_df")
    con.execute("CREATE TABLE fx AS SELECT * FROM fx_df")
    return con


def test_rolling_mean_median_and_market_cap_are_strictly_lagged():
    con = fixture_connection()
    con.execute("UPDATE raw SET turnover=99999999,market_cap=999999999 WHERE date='2025-01-21'")
    build_features(con, "raw", "fx", "features")
    row = con.execute(
        "SELECT adv20_native,median20_native,market_cap_native,fx_date,adv20_usd FROM features WHERE market='A-share' AND date='2025-01-21'"
    ).fetchone()
    assert row[0] == 1050
    assert row[1] == 1050
    assert row[2] == 70000000
    assert row[3] == date(2025, 1, 20)
    assert row[4] == pytest.approx(150)


def test_missing_market_session_does_not_extend_the_window_or_become_zero():
    con = fixture_connection()
    con.execute(
        "INSERT INTO raw SELECT market,'two',date,currency,turnover,market_cap,eligible FROM raw WHERE market='US'"
    )
    con.execute("DELETE FROM raw WHERE market='US' AND symbol='one' AND date='2025-01-10'")
    build_features(con, "raw", "fx", "features")
    row = con.execute(
        "SELECT exclusion_reason FROM features WHERE market='US' AND symbol='one' AND date='2025-01-24'"
    ).fetchone()
    assert row[0] == "missing_market_sessions"
    assert con.execute(
        "SELECT eligible FROM features WHERE market='US' AND symbol='two' AND date='2025-01-24'"
    ).fetchone() == (True,)


def test_observed_zero_turnover_counts_but_null_turnover_does_not():
    con = fixture_connection()
    con.execute("UPDATE raw SET turnover=0 WHERE date='2025-01-10' AND market='US'")
    con.execute("UPDATE raw SET turnover=NULL WHERE date='2025-01-10' AND market='A-share'")
    build_features(con, "raw", "fx", "features")
    assert con.execute(
        "SELECT adv20_native,eligible FROM features WHERE market='US' AND date='2025-01-21'"
    ).fetchone() == (1000, True)
    assert con.execute(
        "SELECT exclusion_reason FROM features WHERE market='A-share' AND date='2025-01-21'"
    ).fetchone() == ("missing_turnover",)


def test_duplicate_source_or_fx_keys_fail_before_join():
    for table in ["raw", "fx"]:
        con = fixture_connection()
        con.execute(f"INSERT INTO {table} SELECT * FROM {table} LIMIT 1")
        with pytest.raises(ValueError, match="duplicate"):
            build_features(con, "raw", "fx", "features")


def test_fx_cannot_use_same_day_or_a_stale_rate():
    con = fixture_connection()
    con.execute("UPDATE fx SET usd_per_native=100 WHERE date='2025-01-21'")
    build_features(con, "raw", "fx", "features")
    assert con.execute(
        "SELECT adv20_usd FROM features WHERE market='A-share' AND date='2025-01-21'"
    ).fetchone()[0] == pytest.approx(150)
    con.execute("DELETE FROM fx WHERE date>'2025-01-01'")
    build_features(con, "raw", "fx", "stale")
    assert con.execute(
        "SELECT exclusion_reason FROM stale WHERE date='2025-01-21' LIMIT 1"
    ).fetchone() == ("missing_or_stale_fx",)


def test_pooled_observations_reconcile_even_when_stocks_change_buckets():
    con = fixture_connection()
    con.execute("UPDATE raw SET market_cap=700000000 WHERE date>='2025-01-22' AND market='A-share'")
    build_features(con, "raw", "fx", "features")
    result = summarize_period(
        con, "features", date(2025, 1, 21), date(2025, 1, 24), ["A-share", "US"]
    )
    a = next(m for m in result["markets"] if m["market"] == "A-share")
    assert sum(b["observations"] for b in a["buckets"]) == a["eligible_observations"] == 4
    assert a["unique_stocks"] == 1
    assert sum(b["count"] for b in a["buckets"]) == 2
    assert result["common_start"] == "2025-01-21"
    assert result["common_end"] == "2025-01-24"


def test_empty_requested_market_is_not_replaced_and_empty_bucket_is_null():
    con = fixture_connection()
    build_features(con, "raw", "fx", "features")
    result = summarize_period(
        con, "features", date(2025, 1, 21), date(2025, 1, 24), ["A-share", "US", "JP"]
    )
    assert result["missing_markets"] == ["JP"]
    assert {m["market"] for m in result["markets"]} == {"A-share", "US"}
    assert all(
        b["median_usd"] is None
        for m in result["markets"]
        for b in m["buckets"]
        if b["observations"] == 0
    )


def test_sparse_extra_dates_do_not_pollute_the_market_session_calendar():
    con = fixture_connection()
    con.execute(
        "INSERT INTO raw SELECT market,'two',date,currency,turnover,market_cap,eligible FROM raw WHERE market='US'"
    )
    con.execute("INSERT INTO raw VALUES ('US','one','2025-01-25','USD',1000000000,70000000,true)")
    con.execute(
        "INSERT INTO raw VALUES ('US','one','2025-01-26','USD',100,70000000,true),('US','two','2025-01-26','USD',100,70000000,true)"
    )
    build_features(con, "raw", "fx", "features", minimum_session_stocks=2)
    assert con.execute(
        "SELECT exclusion_reason FROM features WHERE market='US' AND date='2025-01-25'"
    ).fetchone() == ("sparse_non_market_date",)
    assert con.execute(
        "SELECT adv20_native,eligible FROM features WHERE market='US' AND symbol='one' AND date='2025-01-26'"
    ).fetchone() == (1450, True)
