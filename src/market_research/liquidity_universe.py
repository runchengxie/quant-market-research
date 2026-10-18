"""Retrospective lifecycle sensitivity and conservative daily scenario sample sizes."""

from .liquidity_rebuild import _identifier


def lifecycle_screen(con, features: str, master: str, output: str) -> None:
    """Cross-check current lifecycle dates at the previous observed market session.

    This is a retrospective sensitivity screen, never a PIT membership certificate.
    The input feature table must already use a qualified market observation calendar.
    Unknown identities/dates are excluded; delist dates are exclusive.
    """
    features, master, output = map(_identifier, (features, master, output))
    if con.execute(
        f"SELECT count(*) FROM (SELECT symbol FROM {master} GROUP BY symbol HAVING count(*)>1)"
    ).fetchone()[0]:
        raise ValueError("duplicate lifecycle master symbols")
    con.execute(f"""CREATE OR REPLACE VIEW {output} AS
      WITH dates AS (SELECT DISTINCT market,date FROM {features}),
      calendar AS (SELECT *,lag(date) OVER(PARTITION BY market ORDER BY date) prior_date FROM dates)
      SELECT f.* REPLACE (coalesce(f.eligible AND m.list_date<=c.prior_date
        AND (m.delist_date IS NULL OR m.delist_date>c.prior_date),false) AS eligible)
      FROM {features} f JOIN calendar c USING(market,date)
      LEFT JOIN {master} m ON f.symbol=m.symbol""")


def scenario_stock_limits(con, features: str, view: dict) -> list[dict]:
    """Minimum daily eligible stocks, counting empty buckets as zero.

    Quintile counts follow NTILE(5): remainder stocks go to the earliest groups.
    Dates must be the exact shared calendar used by the published period.
    """
    features = _identifier(features)
    markets = view["included_markets"]
    if not markets or not view["common_dates"]:
        return []
    placeholders = ",".join("?" for _ in markets)
    con.execute(
        f"""CREATE OR REPLACE TEMP TABLE scenario_dates AS
      SELECT date FROM {features} WHERE eligible AND date BETWEEN ?::DATE AND ?::DATE
      AND market IN ({placeholders}) GROUP BY date HAVING count(DISTINCT market)=?""",
        [view["common_start"], view["common_end"], *markets, len(markets)],
    )
    if con.execute("SELECT count(*) FROM scenario_dates").fetchone()[0] != view["common_dates"]:
        raise ValueError("scenario calendar differs from published period")
    result = []
    for market in markets:
        daily = con.execute(
            f"""SELECT d.date,
          count(*) FILTER(WHERE f.market_cap_usd<1e7),
          count(*) FILTER(WHERE f.market_cap_usd>=1e7 AND f.market_cap_usd<1e8),
          count(*) FILTER(WHERE f.market_cap_usd>=1e8 AND f.market_cap_usd<1e9),
          count(*) FILTER(WHERE f.market_cap_usd>=1e9 AND f.market_cap_usd<1e10),
          count(*) FILTER(WHERE f.market_cap_usd>=1e10),count(f.symbol)
          FROM scenario_dates d LEFT JOIN {features} f ON f.date=d.date AND f.market=? AND f.eligible
          GROUP BY d.date""",
            [market],
        ).fetchall()
        result.append(
            dict(
                market=market,
                absolute_min_daily_stocks=[min(row[1 + i] for row in daily) for i in range(5)],
                relative_min_daily_stocks=[
                    min(row[6] // 5 + int(i < row[6] % 5) for row in daily) for i in range(5)
                ],
            )
        )
    return result


def normalize_a_share(con, files: list[str], cutoff: str, start: str = "20150105") -> None:
    """Normalize SH/SZ daily-clean data; physically exclude BSE and predecessor copies."""
    con.execute(
        """CREATE OR REPLACE TABLE raw AS
      SELECT 'A-share' market,ts_code symbol,try_strptime(trade_date,'%Y%m%d')::DATE date,
        'CNY' currency,amount*1000.0 turnover,total_mv*10000.0 market_cap,
        coalesce(is_st=false AND is_suspended=false,false) eligible
      FROM read_parquet(?,union_by_name=true) WHERE trade_date>=? AND trade_date<=?
      AND regexp_full_match(ts_code,'(00[0-9]{4}|30[0-9]{4}|60[0-9]{4}|68[0-9]{4})\\.(SH|SZ)')
      AND ts_code NOT IN ('000022.SZ','000043.SZ','300114.SZ')""",
        [files, start, cutoff],
    )
