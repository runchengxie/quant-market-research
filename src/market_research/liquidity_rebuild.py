"""Auditable retrospective liquidity features; not a historical execution universe."""

from __future__ import annotations

import re
from datetime import date

BUCKET_LABELS = ("< $10m", "$10m-$100m", "$100m-$1bn", "$1bn-$10bn", ">= $10bn")


def _identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", value):
        raise ValueError("simple SQL identifiers required")
    return value


def build_features(
    con, source: str, fx: str, output: str, *, minimum_session_stocks: int = 1
) -> None:
    """Use exactly the prior 20 market sessions and strictly earlier reference FX.

    Source columns: market, symbol, date, currency, turnover (native), market_cap
    (native), eligible (retrospective source rule). All observed rows establish
    the market calendar, including zero-turnover and ineligible observations.
    """
    source, fx, output = map(_identifier, (source, fx, output))
    if not isinstance(minimum_session_stocks, int) or minimum_session_stocks < 1:
        raise ValueError("minimum_session_stocks must be a positive integer")
    for table, keys in [(source, "market,symbol,date"), (fx, "currency,date")]:
        if con.execute(
            f"SELECT count(*) FROM (SELECT {keys} FROM {table} GROUP BY ALL HAVING count(*)>1)"
        ).fetchone()[0]:
            raise ValueError(f"duplicate keys in {table}")
        conditions = " OR ".join(f"{key} IS NULL" for key in keys.split(","))
        if con.execute(f"SELECT count(*) FROM {table} WHERE {conditions}").fetchone()[0]:
            raise ValueError(f"null keys in {table}")
    if con.execute(
        f"SELECT count(*) FROM {fx} WHERE usd_per_native IS NULL OR NOT isfinite(usd_per_native) OR usd_per_native<=0"
    ).fetchone()[0]:
        raise ValueError("FX rates must be finite and positive")
    con.execute(f"""CREATE OR REPLACE TABLE {output} AS
      WITH calendar AS (
        SELECT market,date FROM {source} GROUP BY market,date
          HAVING count(DISTINCT symbol)>={minimum_session_stocks}
      ), sessions AS (
        SELECT r.*,dense_rank() OVER(PARTITION BY r.market ORDER BY r.date) session_id
        FROM {source} r JOIN calendar USING(market,date)
      ), prior AS (
        SELECT market,symbol,date,currency,
          lag(market_cap) OVER w market_cap_native,
          lag(eligible) OVER w prior_eligible,
          session_id-lag(session_id,20) OVER w session_distance,
          count(*) OVER past history_count,
          count(CASE WHEN turnover>=0 AND isfinite(turnover) THEN turnover END) OVER past turnover_count,
          avg(CASE WHEN turnover>=0 AND isfinite(turnover) THEN turnover END) OVER past adv20_native,
          median(CASE WHEN turnover>=0 AND isfinite(turnover) THEN turnover END) OVER past median20_native
        FROM sessions
        WINDOW w AS(PARTITION BY market,symbol ORDER BY date),
          past AS(PARTITION BY market,symbol ORDER BY date ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING)
      ), converted AS (
        SELECT p.*,f.date fx_date,f.usd_per_native,
          p.market_cap_native*f.usd_per_native market_cap_usd,
          p.adv20_native*f.usd_per_native adv20_usd,
          p.median20_native*f.usd_per_native median20_usd
        FROM prior p ASOF LEFT JOIN {fx} f ON p.currency=f.currency AND p.date>f.date
      ), reasons AS (
        SELECT *, CASE
          WHEN history_count<20 THEN 'insufficient_history'
          WHEN session_distance<>20 THEN 'missing_market_sessions'
          WHEN turnover_count<>20 THEN 'missing_turnover'
          WHEN NOT coalesce(prior_eligible,false) THEN 'prior_source_ineligible'
          WHEN market_cap_native IS NULL OR NOT isfinite(market_cap_native) OR market_cap_native<=0 THEN 'missing_prior_cap'
          WHEN fx_date IS NULL OR date-fx_date>7 THEN 'missing_or_stale_fx'
          WHEN NOT isfinite(adv20_usd) OR NOT isfinite(median20_usd) OR NOT isfinite(market_cap_usd) THEN 'numeric_overflow'
          ELSE NULL END exclusion_reason
        FROM converted
      ) SELECT *,exclusion_reason IS NULL eligible FROM reasons
      UNION ALL BY NAME
      SELECT market,symbol,date,currency,'sparse_non_market_date' exclusion_reason,false eligible
        FROM {source} r WHERE NOT EXISTS(SELECT 1 FROM calendar c WHERE c.market=r.market AND c.date=r.date)
    """)


def summarize_period(con, features: str, start: date, end: date, markets: list[str]) -> dict:
    """Pool eligible security-days on the intersection of available market dates.

    Bucket counts are distinct stocks and may overlap across buckets over time.
    Observations are additive security-days. Missing requested markets are explicit.
    """
    features = _identifier(features)
    available = {
        row[0]
        for row in con.execute(
            f"SELECT DISTINCT market FROM {features} WHERE eligible AND date BETWEEN ? AND ?",
            [start, end],
        ).fetchall()
    }
    included = [market for market in markets if market in available]
    result = dict(
        requested_start=str(start),
        requested_end=str(end),
        included_markets=included,
        missing_markets=[m for m in markets if m not in available],
        common_start=None,
        common_end=None,
        common_dates=0,
        markets=[],
    )
    if not included:
        return result
    placeholders = ",".join("?" for _ in included)
    con.execute(
        f"""CREATE OR REPLACE TEMP TABLE liquidity_period_rows AS
      WITH common AS (
        SELECT date FROM {features} WHERE eligible AND date BETWEEN ? AND ?
          AND market IN ({placeholders}) GROUP BY date HAVING count(DISTINCT market)=?
      ) SELECT f.*,CASE WHEN market_cap_usd<1e7 THEN 0 WHEN market_cap_usd<1e8 THEN 1
          WHEN market_cap_usd<1e9 THEN 2 WHEN market_cap_usd<1e10 THEN 3 ELSE 4 END bucket
        FROM {features} f JOIN common USING(date) WHERE f.eligible AND market IN ({placeholders})
    """,
        [start, end, *included, len(included), *included],
    )
    bounds = con.execute(
        "SELECT min(date),max(date),count(DISTINCT date) FROM liquidity_period_rows"
    ).fetchone()
    if not bounds[2]:
        return result
    result.update(common_start=str(bounds[0]), common_end=str(bounds[1]), common_dates=bounds[2])
    for market in included:
        total, stocks, below, first_fx, last_fx = con.execute(
            """SELECT count(*),count(DISTINCT symbol),
          count_if(market_cap_usd<1e8),min(fx_date),max(fx_date)
          FROM liquidity_period_rows WHERE market=?""",
            [market],
        ).fetchone()
        item = dict(
            market=market,
            status="derived",
            aggregation="snapshot" if bounds[2] == 1 else "security_day",
            as_of=str(bounds[1]),
            coverage_start=str(bounds[0]),
            coverage_end=str(bounds[1]),
            unique_stocks=stocks,
            eligible_observations=total,
            below_100m_observations=below,
            fx_start=str(first_fx),
            fx_end=str(last_fx),
            buckets=[],
        )
        for bucket, label in enumerate(BUCKET_LABELS):
            row = con.execute(
                """SELECT count(*),count(DISTINCT symbol),median(adv20_usd),avg(adv20_usd),
              quantile_cont(adv20_usd,0.1),quantile_cont(adv20_usd,0.25),
              quantile_cont(adv20_usd,0.75),quantile_cont(adv20_usd,0.9),
              count_if(adv20_usd=0),median(median20_usd),avg(median20_usd),
              quantile_cont(median20_usd,0.1),quantile_cont(median20_usd,0.25),
              quantile_cont(median20_usd,0.75),quantile_cont(median20_usd,0.9)
              FROM liquidity_period_rows WHERE market=? AND bucket=?""",
                [market, bucket],
            ).fetchone()
            observations = row[0]
            zero_count = row[8] or 0
            item["buckets"].append(
                dict(
                    label=label,
                    observations=observations,
                    count=row[1],
                    median_usd=row[2],
                    mean_usd=row[3],
                    p10_usd=row[4],
                    p25_usd=row[5],
                    p75_usd=row[6],
                    p90_usd=row[7],
                    zero_adv20_observations=zero_count,
                    zero_adv20_share=zero_count / observations if observations else None,
                    median20_median_usd=row[9],
                    median20_mean_usd=row[10],
                    median20_p10_usd=row[11],
                    median20_p25_usd=row[12],
                    median20_p75_usd=row[13],
                    median20_p90_usd=row[14],
                )
            )
        if bounds[2] == 1:
            item["eligible_stocks"] = stocks
            item["sub_100m_count"] = below
            item["sub_100m_median_usd"] = con.execute(
                "SELECT median(adv20_usd) FROM liquidity_period_rows WHERE market=? AND market_cap_usd<1e8",
                [market],
            ).fetchone()[0]
        assert sum(b["observations"] for b in item["buckets"]) == total
        result["markets"].append(item)
    return result
