import duckdb
import pytest

from market_research.liquidity_relative import rank_features, summarize_relative


def fixture():
    con = duckdb.connect()
    con.execute("""CREATE TABLE features AS SELECT market,symbol,date,cap::DOUBLE market_cap_usd,
      turnover::DOUBLE adv20_usd,turnover::DOUBLE*0.8 median20_usd,date-1 fx_date,true eligible
      FROM (VALUES ('A-share','b',DATE '2025-01-02',100.0,10.0),
        ('A-share','a',DATE '2025-01-02',100.0,20.0),
        ('A-share','c',DATE '2025-01-02',300.0,30.0),
        ('A-share','d',DATE '2025-01-02',400.0,40.0),
        ('A-share','e',DATE '2025-01-02',500.0,50.0),
        ('US','a',DATE '2025-01-02',1.0,100.0),
        ('US','b',DATE '2025-01-02',2.0,200.0)) t(market,symbol,date,cap,turnover)""")
    template = dict(
        common_start="2025-01-02",
        common_end="2025-01-02",
        common_dates=1,
        included_markets=["A-share", "US"],
        missing_markets=[],
        period="common snapshot",
        status="derived",
        markets=[
            dict(
                market=m,
                eligible_observations=n,
                eligible_stocks=n,
                unique_stocks=n,
                aggregation="snapshot",
                coverage_start="2025-01-02",
                coverage_end="2025-01-02",
                as_of="2025-01-02",
                buckets=[],
            )
            for m, n in [("A-share", 5), ("US", 2)]
        ],
    )
    return con, template


def test_quintiles_rank_each_market_day_and_break_cap_ties_by_symbol():
    con, template = fixture()
    rank_features(con, "features", "ranked")
    assert con.execute(
        "SELECT symbol,relative_bucket FROM ranked WHERE market='A-share' ORDER BY relative_bucket"
    ).fetchall() == [("a", 0), ("b", 1), ("c", 2), ("d", 3), ("e", 4)]
    result = summarize_relative(con, "ranked", template)
    a, us = result["markets"]
    assert a["buckets"][0]["median_usd"] == 20
    assert a["buckets"][0]["median20_median_usd"] == 16
    assert a["buckets"][0]["cap_min_usd"] == 100
    assert a["buckets"][0]["cap_max_usd"] == 100
    assert sum(b["observations"] for b in a["buckets"]) == 5
    assert us["buckets"][2]["observations"] == 0
    assert us["buckets"][2]["median_usd"] is None
    assert "below_100m_observations" not in a


def test_historical_grain_and_common_dates_are_preserved_when_stocks_move():
    con, template = fixture()
    con.execute(
        "INSERT INTO features SELECT market,symbol,date+1,1000-market_cap_usd,adv20_usd,median20_usd,fx_date+1,eligible FROM features"
    )
    con.execute(
        "INSERT INTO features SELECT market,symbol,date+1,market_cap_usd,adv20_usd,median20_usd,fx_date+1,eligible FROM features WHERE market='US' AND date='2025-01-03'"
    )
    template.update(common_end="2025-01-03", common_dates=2)
    for m in template["markets"]:
        m.update(
            aggregation="security_day",
            eligible_observations=m["eligible_observations"] * 2,
            coverage_end="2025-01-03",
            as_of="2025-01-03",
        )
        m.pop("eligible_stocks")
    rank_features(con, "features", "ranked")
    a = summarize_relative(con, "ranked", template)["markets"][0]
    assert a["eligible_observations"] == 10
    assert a["buckets"][0]["count"] == 2
    assert sum(b["observations"] for b in a["buckets"]) == 10
    assert sum(b["count"] for b in a["buckets"]) > a["unique_stocks"]


def test_duplicate_keys_and_changed_base_coverage_fail():
    con, template = fixture()
    con.execute("INSERT INTO features SELECT * FROM features LIMIT 1")
    with pytest.raises(ValueError, match="duplicate"):
        rank_features(con, "features", "ranked")
    con, template = fixture()
    rank_features(con, "features", "ranked")
    template["common_dates"] = 2
    with pytest.raises(ValueError, match="coverage"):
        summarize_relative(con, "ranked", template)


def test_nondivisible_population_allocates_extra_stocks_to_earlier_quintiles():
    con, _ = fixture()
    con.execute(
        "INSERT INTO features SELECT market,'f',date,600,60,48,fx_date,eligible FROM features WHERE market='A-share' LIMIT 1"
    )
    con.execute(
        "INSERT INTO features SELECT market,'g',date,700,70,56,fx_date,eligible FROM features WHERE market='A-share' LIMIT 1"
    )
    rank_features(con, "features", "ranked")
    assert con.execute(
        "SELECT count(*) FROM ranked WHERE market='A-share' GROUP BY relative_bucket ORDER BY relative_bucket"
    ).fetchall() == [(2,), (2,), (1,), (1,), (1,)]
