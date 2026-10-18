"""Frozen-name dollar-turnover sensitivities; no fill or share-accounting claims."""

from __future__ import annotations

import numpy as np


def evaluate_budget(turnover, position: float, participation: float) -> dict:
    """Credit only known nonnegative amounts; retain unknowns in the original denominator.

    Rows are original stock-formations, columns are subsequent source sessions.
    First day is the first known-credit coverage day, not an executable exit time.
    """
    values = np.asarray(turnover, dtype=float)
    if (
        values.ndim != 2
        or values.shape[1] == 0
        or not np.isfinite(position)
        or position <= 0
        or not np.isfinite(participation)
        or not 0 < participation <= 1
        or np.isinf(values).any()
        or (values < 0).any()
    ):
        raise ValueError("invalid dollar-turnover budget inputs")
    credits = np.nancumsum(values, axis=1) * participation
    reached = credits >= position
    covered = reached[:, -1]
    unresolved = ~covered & np.isnan(values).any(axis=1)
    return dict(
        covered=covered,
        unresolved=unresolved,
        not_covered=~covered & ~unresolved,
        first_day=np.where(covered, reached.argmax(axis=1) + 1, np.nan),
        uncredited_fraction=np.maximum(0, 1 - credits[:, -1] / position),
    )


def sell_credit(amount, low, high, down_limit, full_suspension: bool) -> tuple:
    """Return unguarded/guarded native turnover and a mutually exclusive audit state.

    A lower-limit touch blocks the *whole day* in a deliberately conservative
    sensitivity. Absence from suspension events is not independent proof of trading.
    """

    def valid(x):
        return x is not None and np.isfinite(x)

    if full_suspension:
        if valid(amount) and amount > 0:
            return np.nan, np.nan, "suspension_conflict"
        return 0.0, 0.0, "full_suspension"
    if amount is None or (not valid(amount) and np.isnan(amount)):
        return np.nan, np.nan, "missing_daily"
    if not valid(amount) or amount < 0:
        return np.nan, np.nan, "invalid_daily"
    if not valid(low) or not valid(high) or not 0 < low <= high:
        return amount, np.nan, "invalid_price"
    if not valid(down_limit) or down_limit <= 0:
        return amount, np.nan, "unknown_limit"
    if low < down_limit - 0.011:
        return amount, np.nan, "price_limit_conflict"
    if low <= down_limit + 0.005:
        return amount, 0.0, "lower_touch"
    return amount, amount, "credited"


def frozen_paths(con, start_year: int, end_year: int, *, horizon: int = 20):
    """Join f features, d daily, l lower limits, s full-suspension events.

    Original size buckets remain frozen even when later capitalization changes.
    A full future source-session horizon is required; future eligibility is not
    used to discard original names. Daily native amount remains in thousands CNY.
    """
    if horizon < 1 or start_year > end_year:
        raise ValueError("invalid formation range or horizon")
    for t in ["f", "d", "l", "s"]:
        if con.execute(
            f"SELECT count(*) FROM (SELECT symbol,date FROM {t} GROUP BY ALL HAVING count(*)>1)"
        ).fetchone()[0]:
            raise ValueError(f"duplicate security-date keys in {t}")
    con.execute("""CREATE OR REPLACE TEMP TABLE exit_calendar AS
      SELECT date,row_number() OVER(ORDER BY date) sid,min(usd_per_native) fx,
        count(DISTINCT usd_per_native) fx_versions FROM f GROUP BY date""")
    if con.execute(
        "SELECT count(*) FROM exit_calendar WHERE fx_versions<>1 OR NOT isfinite(fx) OR fx<=0"
    ).fetchone()[0]:
        raise ValueError("inconsistent daily feature FX")
    return con.execute(
        f"""WITH ends AS (
      SELECT max(date) date FROM exit_calendar WHERE year(date) BETWEEN ? AND ?
      GROUP BY date_trunc('month',date)),
      forms AS (SELECT f.*,c.sid,CASE WHEN market_cap_usd<1e7 THEN 0
        WHEN market_cap_usd<1e8 THEN 1 WHEN market_cap_usd<1e9 THEN 2
        WHEN market_cap_usd<1e10 THEN 3 ELSE 4 END bucket
        FROM f JOIN ends USING(date) JOIN exit_calendar c USING(date)
        WHERE f.eligible AND c.sid+{horizon}<=(SELECT max(sid) FROM exit_calendar))
      SELECT f.date formation,f.symbol,f.bucket,f.adv20_usd,c.date,c.sid-f.sid h,c.fx,
        d.amount,d.low,d.high,l.down_limit,coalesce(s.full_suspension,false) full_suspension
      FROM forms f JOIN exit_calendar c ON c.sid>f.sid AND c.sid<=f.sid+{horizon}
      LEFT JOIN d ON d.symbol=f.symbol AND d.date=c.date
      LEFT JOIN l ON l.symbol=f.symbol AND l.date=c.date
      LEFT JOIN s ON s.symbol=f.symbol AND s.date=c.date
      ORDER BY formation,symbol,h""",
        [start_year, end_year],
    ).fetchdf()


def summarize_budget(turnover, position: float, participation: float) -> dict:
    r = evaluate_budget(turnover, position, participation)
    n = len(r["covered"])
    if n == 0:
        raise ValueError("empty original cohort")
    completed = r["first_day"][r["covered"]]
    residual = r["uncredited_fraction"]
    total = float(residual.sum())
    worst_count = max(1, int(np.ceil(0.1 * n)))
    return dict(
        stocks=n,
        covered=int(r["covered"].sum()),
        not_covered=int(r["not_covered"].sum()),
        unresolved=int(r["unresolved"].sum()),
        covered_day_p50=float(np.quantile(completed, 0.5)) if len(completed) else None,
        covered_day_p95=float(np.quantile(completed, 0.95)) if len(completed) else None,
        all_names_day_max=int(completed.max()) if len(completed) == n else None,
        uncredited_fraction=total / n,
        top_decile_uncredited_share=float(np.sort(residual)[-worst_count:].sum() / total)
        if total > 0
        else None,
    )
