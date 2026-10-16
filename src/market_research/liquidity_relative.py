"""Relative size buckets over the already reviewed eligible liquidity universe."""

from __future__ import annotations

from copy import deepcopy

from .liquidity_rebuild import _identifier

RELATIVE_LABELS = ("0–20%", "20–40%", "40–60%", "60–80%", "80–100%")


def rank_features(con, features: str, output: str) -> None:
    features, output = map(_identifier, (features, output))
    if con.execute(f"""SELECT count(*) FROM (SELECT market,symbol,date FROM {features}
        WHERE eligible GROUP BY ALL HAVING count(*)>1)""").fetchone()[0]:
        raise ValueError("duplicate eligible security/date keys")
    con.execute(f"""CREATE OR REPLACE TABLE {output} AS SELECT *,
      ntile(5) OVER(PARTITION BY market,date ORDER BY market_cap_usd,symbol)-1 relative_bucket
      FROM {features} WHERE eligible""")


def summarize_relative(con, ranked: str, template: dict) -> dict:
    """Keep the absolute view's exact dates/universe; repartition by daily size rank.

    Quintiles are assigned within each eligible market/day by prior-session USD
    cap, ascending; equal caps use stable symbol order. Integer group sizes can
    differ by one. Historical views pool equally weighted security-days.
    """
    ranked = _identifier(ranked)
    result = deepcopy(template)
    included = template["included_markets"]
    if not included or not template["common_dates"]:
        return result
    placeholders = ",".join("?" for _ in included)
    con.execute(
        f"""CREATE OR REPLACE TEMP TABLE relative_period AS
      WITH common AS (SELECT date FROM {ranked} WHERE date BETWEEN ?::DATE AND ?::DATE
        AND market IN ({placeholders}) GROUP BY date HAVING count(DISTINCT market)=?)
      SELECT r.* FROM {ranked} r JOIN common USING(date) WHERE market IN ({placeholders})""",
        [template["common_start"], template["common_end"], *included, len(included), *included],
    )
    bounds = con.execute(
        "SELECT min(date),max(date),count(DISTINCT date) FROM relative_period"
    ).fetchone()
    if (str(bounds[0]), str(bounds[1]), bounds[2]) != (
        template["common_start"],
        template["common_end"],
        template["common_dates"],
    ):
        raise ValueError("relative date coverage differs from reviewed base")
    for item in result["markets"]:
        market = item["market"]
        n, stocks = con.execute(
            "SELECT count(*),count(DISTINCT symbol) FROM relative_period WHERE market=?", [market]
        ).fetchone()
        if n != item["eligible_observations"] or stocks != item["unique_stocks"]:
            raise ValueError("relative universe differs from reviewed base")
        for key in ["below_100m_observations", "sub_100m_count", "sub_100m_median_usd"]:
            item.pop(key, None)
        item["buckets"] = []
        for bucket, label in enumerate(RELATIVE_LABELS):
            row = con.execute(
                """SELECT count(*),count(DISTINCT symbol),
              median(adv20_usd),avg(adv20_usd),quantile_cont(adv20_usd,0.9),
              median(median20_usd),avg(median20_usd),quantile_cont(median20_usd,0.9),
              min(market_cap_usd),max(market_cap_usd)
              FROM relative_period WHERE market=? AND relative_bucket=?""",
                [market, bucket],
            ).fetchone()
            item["buckets"].append(
                dict(
                    zip(
                        [
                            "label",
                            "observations",
                            "count",
                            "median_usd",
                            "mean_usd",
                            "p90_usd",
                            "median20_median_usd",
                            "median20_mean_usd",
                            "median20_p90_usd",
                            "cap_min_usd",
                            "cap_max_usd",
                        ],
                        [label, *row],
                        strict=True,
                    )
                )
            )
        assert sum(b["observations"] for b in item["buckets"]) == n
    return result
