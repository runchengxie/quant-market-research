"""Retrospective liquidity stress, frozen size-cohort continuity and clock windows."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .liquidity_rebuild import _identifier

WINDOWS = ("open30", "late_morning", "afternoon", "close30", "core")


def build_daily_panels(con, source: str, *, horizon: int = 20, minimum_stocks: int = 100):
    """Build compact monthly panels and formation-cohort diagnostics in DuckDB.

    The feature source is already lagged and qualified; future dates are used
    only for retrospective cohort evaluation. No return or executable capacity
    claim is formed. A missing target observation is never a zero-turnover row.
    """
    source = _identifier(source)
    if horizon < 1 or minimum_stocks < 1:
        raise ValueError("positive horizon and calendar threshold required")
    if con.execute(
        f"SELECT count(*) FROM (SELECT symbol,date FROM {source} GROUP BY ALL HAVING count(*)>1)"
    ).fetchone()[0]:
        raise ValueError("duplicate security-date keys")
    con.execute(f"""CREATE OR REPLACE VIEW stress_f AS SELECT *,CASE
      WHEN market_cap_usd<1e7 THEN 0 WHEN market_cap_usd<1e8 THEN 1
      WHEN market_cap_usd<1e9 THEN 2 WHEN market_cap_usd<1e10 THEN 3 ELSE 4 END bucket
      FROM {source}""")
    con.execute(f"""CREATE OR REPLACE TABLE stress_calendar AS SELECT date,
      row_number() OVER(ORDER BY date) sid,count(*) FILTER(WHERE eligible) valid_stocks
      FROM {source} GROUP BY date""")
    monthly = con.execute(f"""WITH d AS (
      SELECT c.date,b.bucket,count(f.symbol) n,median(f.adv20_usd) adv
      FROM stress_calendar c CROSS JOIN range(5) b(bucket)
      LEFT JOIN stress_f f ON f.date=c.date AND f.bucket=b.bucket AND f.eligible
      WHERE c.valid_stocks>={minimum_stocks}
        AND date_trunc('month',c.date)<(SELECT date_trunc('month',max(date)) FROM stress_calendar)
      GROUP BY c.date,b.bucket)
      SELECT year(date)::INT AS year,strftime(date,'%Y-%m') AS month,bucket,
        count(*) market_days,count(*) FILTER(WHERE n>0) active_days,
        min(n) min_daily_stocks,median(adv) median_daily_adv,p10
      FROM (SELECT *,quantile_cont(adv,.1) OVER(PARTITION BY date_trunc('month',date),bucket) p10 FROM d)
      GROUP BY ALL ORDER BY year,month,bucket""").fetchdf()
    # Formations are last source market dates of completed months with a full future horizon.
    con.execute(f"""CREATE OR REPLACE TEMP TABLE stress_formations AS
      WITH ends AS (SELECT max(date) date FROM stress_calendar
        WHERE date_trunc('month',date)<(SELECT date_trunc('month',max(date)) FROM stress_calendar)
        GROUP BY date_trunc('month',date))
      SELECT f.*,c.sid FROM stress_f f JOIN ends USING(date) JOIN stress_calendar c USING(date)
      WHERE f.eligible AND c.sid+{horizon}<=(SELECT max(sid) FROM stress_calendar)""")
    con.execute(f"""CREATE OR REPLACE TEMP TABLE stress_paths AS
      SELECT s.date formation_date,year(s.date)::INT AS year,s.bucket,s.symbol,s.adv20_usd baseline,
        c.sid-s.sid h,t.symbol IS NOT NULL observed,coalesce(t.eligible,false) usable,
        t.bucket target_bucket,t.adv20_usd target_adv
      FROM stress_formations s JOIN stress_calendar c ON c.sid>s.sid AND c.sid<=s.sid+{horizon}
      LEFT JOIN stress_f t ON t.date=c.date AND t.symbol=s.symbol""")
    cohorts = con.execute(f"""WITH stock AS (
       SELECT formation_date,year,bucket,symbol, min(baseline) baseline,
         count(*) FILTER(WHERE usable AND target_bucket=bucket) same_days,
         count(*) FILTER(WHERE usable) usable_days,
         count(*) FILTER(WHERE h={horizon} AND usable AND target_bucket=bucket) retained,
         count(*) FILTER(WHERE h={horizon} AND usable AND target_bucket<>bucket) migrated,
         count(*) FILTER(WHERE h={horizon} AND observed AND NOT usable) ineligible,
         count(*) FILTER(WHERE h={horizon} AND NOT observed) missing
       FROM stress_paths GROUP BY ALL),
      endpoint AS (SELECT formation_date,year,bucket,count(*) stocks,median(baseline) baseline,
        sum(retained) retained,sum(migrated) migrated,sum(ineligible) ineligible,sum(missing) missing,
        count(*) FILTER(WHERE same_days={horizon}) continuous,
        count(*) FILTER(WHERE usable_days={horizon}) usable_continuous FROM stock GROUP BY ALL),
      daily AS (SELECT formation_date,year,bucket,h,
         count(*) FILTER(WHERE usable)*1.0/count(*) coverage,
         median(target_adv) FILTER(WHERE usable) observed_median FROM stress_paths GROUP BY ALL),
      path AS (SELECT formation_date,year,bucket,min(coverage) min_coverage,
         min(observed_median) minimum_observed_median FROM daily GROUP BY ALL)
      SELECT e.*,p.min_coverage,
        CASE WHEN p.min_coverage>=.9 AND e.baseline>0
          THEN p.minimum_observed_median/e.baseline ELSE NULL END frozen_min_ratio
      FROM endpoint e JOIN path p USING(formation_date,year,bucket) ORDER BY formation_date,bucket""").fetchdf()
    return monthly, cohorts


def summarize_stress(monthly: pd.DataFrame) -> list[dict]:
    result = []
    for (year, bucket), group in monthly.groupby(["year", "bucket"], sort=True):
        good = group.loc[
            (group.active_days >= 10)
            & (group.active_days >= 0.8 * group.market_days)
            & group.median_daily_adv.notna()
        ]
        row = dict(
            year=int(year),
            bucket=int(bucket),
            months=len(good),
            min_daily_stocks=int(group.min_daily_stocks.min()),
            stress_months=[],
            stress_median_usd=None,
            normal_median_usd=None,
            retained_budget_fraction=None,
            status="insufficient_months",
        )
        if len(good) >= 6:
            ranked = good.sort_values(["median_daily_adv", "month"], kind="stable")
            n = math.ceil(0.2 * len(good))
            low = ranked.iloc[:n]
            normal = ranked.iloc[n:]
            s = float(low.median_daily_adv.median())
            v = float(normal.median_daily_adv.median())
            row.update(
                stress_months=sorted(low.month.tolist()),
                stress_median_usd=s,
                normal_median_usd=v,
                retained_budget_fraction=s / v if v > 0 else None,
                status="derived",
            )
        result.append(row)
    return result


def summarize_cohorts(cohorts: pd.DataFrame) -> list[dict]:
    result = []
    for (year, bucket), g in cohorts.groupby(["year", "bucket"], sort=True):
        n = int(g.stocks.sum())
        assert (g.retained + g.migrated + g.ineligible + g.missing).eq(g.stocks).all()
        result.append(
            dict(
                year=int(year),
                bucket=int(bucket),
                formations=len(g),
                formation_stock_observations=n,
                retained_fraction=float(g.retained.sum() / n),
                migrated_fraction=float(g.migrated.sum() / n),
                ineligible_fraction=float(g.ineligible.sum() / n),
                missing_fraction=float(g.missing.sum() / n),
                continuous_fraction=float(g.continuous.sum() / n),
                usable_continuous_fraction=float(g.usable_continuous.sum() / n),
                frozen_valid_formations=int(g.frozen_min_ratio.notna().sum()),
                frozen_min_ratio_median=float(g.frozen_min_ratio.median())
                if g.frozen_min_ratio.notna().any()
                else None,
                min_coverage=float(g.min_coverage.min()),
            )
        )
    return result


def window_masks(times: pd.Series) -> dict[str, pd.Series]:
    clock = times.dt.hour * 60 + times.dt.minute
    return dict(
        open30=(clock >= 570) & (clock < 600),
        late_morning=(clock >= 600) & (clock <= 690),
        afternoon=(clock >= 780) & (clock <= 900),
        close30=(clock >= 870) & (clock <= 900),
        core=((clock >= 600) & (clock <= 690)) | ((clock >= 780) & (clock < 870)),
    )


def validate_turnover(values) -> None:
    """Reject nonfinite/negative source turnover before qualification arithmetic."""
    values = np.asarray(values)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("source turnover must be finite and nonnegative")
