from datetime import date

import duckdb

from market_research.liquidity_universe import lifecycle_screen, scenario_stock_limits


def test_lifecycle_uses_previous_market_session_and_strict_delist_boundary():
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE f(market VARCHAR,symbol VARCHAR,date DATE,eligible BOOLEAN,market_cap_usd DOUBLE)"
    )
    con.execute(
        "INSERT INTO f VALUES ('A-share','x','2020-01-02',true,2e8),('A-share','x','2020-01-03',true,2e8),('A-share','y','2020-01-03',true,2e8),('A-share','x','2020-01-06',true,2e8)"
    )
    con.execute("CREATE TABLE m(symbol VARCHAR,list_date DATE,delist_date DATE)")
    con.execute("INSERT INTO m VALUES ('x','2010-01-01','2020-01-03'),('y','2020-01-03',NULL)")
    lifecycle_screen(con, "f", "m", "screened")
    assert con.execute(
        "SELECT symbol,date FROM screened WHERE eligible ORDER BY date,symbol"
    ).fetchall() == [("x", date(2020, 1, 3))]


def test_stock_limits_include_zero_bucket_dates_and_relative_remainders():
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE f(market VARCHAR,symbol VARCHAR,date DATE,eligible BOOLEAN,market_cap_usd DOUBLE)"
    )
    con.execute(
        "INSERT INTO f VALUES ('A-share','x','2020-01-02',true,2e8),('A-share','x','2020-01-03',true,2e9)"
    )
    view = dict(
        included_markets=["A-share"],
        common_start="2020-01-02",
        common_end="2020-01-03",
        common_dates=2,
    )
    limits = scenario_stock_limits(con, "f", view)
    a = limits[0]
    assert a["absolute_min_daily_stocks"] == [0, 0, 0, 0, 0]
    assert a["relative_min_daily_stocks"] == [1, 0, 0, 0, 0]


def test_normalize_sh_sz_preserves_old_daily_history_and_converts_units(tmp_path):
    from market_research.liquidity_universe import normalize_a_share

    con = duckdb.connect()
    con.execute(
        "CREATE TABLE inputs(ts_code VARCHAR,trade_date VARCHAR,amount DOUBLE,total_mv DOUBLE,is_st BOOLEAN,is_suspended BOOLEAN)"
    )
    con.execute(
        "INSERT INTO inputs VALUES ('000001.SZ','20150105',3,4,false,false),('830001.BJ','20200102',3,4,false,false),('000022.SZ','20150105',3,4,false,false),('001872.SZ','20150105',3,4,true,false),('600001.SH','20270101',3,4,false,false)"
    )
    path = str(tmp_path / "daily.parquet")
    con.execute("COPY inputs TO ? (FORMAT PARQUET)", [path])
    normalize_a_share(con, [path], "20261015")
    assert con.execute(
        "SELECT symbol,date,turnover,market_cap,eligible FROM raw ORDER BY symbol"
    ).fetchall() == [
        ("000001.SZ", date(2015, 1, 5), 3000, 40000, True),
        ("001872.SZ", date(2015, 1, 5), 3000, 40000, False),
    ]
