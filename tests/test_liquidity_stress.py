import duckdb
import pandas as pd
import pytest

from market_research.liquidity_stress import build_daily_panels, summarize_stress, window_masks


def test_stress_requires_sufficient_months_and_ranks_within_year():
    rows = [
        dict(
            year=2020,
            bucket=2,
            month=f"2020-{i:02d}",
            market_days=20,
            active_days=20,
            min_daily_stocks=5,
            median_daily_adv=i,
        )
        for i in range(1, 7)
    ]
    result = summarize_stress(pd.DataFrame(rows))[0]
    assert result["stress_months"] == ["2020-01", "2020-02"]
    assert result["retained_budget_fraction"] == pytest.approx(1 / 3)
    assert summarize_stress(pd.DataFrame(rows[:5]))[0]["retained_budget_fraction"] is None


def test_frozen_cohort_preserves_missing_and_ineligible_members():
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE f(symbol VARCHAR,date DATE,eligible BOOLEAN,adv20_usd DOUBLE,market_cap_usd DOUBLE)"
    )
    con.execute("""INSERT INTO f VALUES
      ('x','2020-01-30',true,10,2e8),('y','2020-01-30',true,20,2e8),
      ('x','2020-01-31',true,10,2e8),('y','2020-01-31',true,20,2e8),
      ('x','2020-02-03',true,5,2e9),
      ('x','2020-02-04',true,5,2e8),('y','2020-02-04',false,10,2e8),
      ('x','2020-03-02',true,5,2e8)""")
    _, cohorts = build_daily_panels(con, "f", horizon=2, minimum_stocks=1)
    row = cohorts.iloc[0]
    assert row.stocks == 2 and row.retained == 1 and row.ineligible == 1 and row.missing == 0
    assert row.continuous == 0 and row.usable_continuous == 1 and row.min_coverage == 0.5
    assert pd.isna(row.frozen_min_ratio)


def test_clock_window_endpoints_and_auction_remainder():
    times = pd.Series(
        pd.to_datetime(
            [
                "2020-01-02 " + x
                for x in ["09:25", "09:30", "09:59", "10:00", "11:30", "13:00", "14:30", "15:00"]
            ]
        )
    )
    masks = window_masks(times)
    assert masks["open30"].tolist() == [False, True, True, False, False, False, False, False]
    assert masks["core"].tolist() == [False, False, False, True, True, True, False, False]
    assert masks["close30"].tolist() == [False, False, False, False, False, False, True, True]


def test_raw_turnover_validation_rejects_infinity_nan_and_negative():
    from market_research.liquidity_stress import validate_turnover

    validate_turnover([0.0, 1.0])
    for values in [[float("inf")], [float("nan")], [-1.0]]:
        with pytest.raises(ValueError, match="finite and nonnegative"):
            validate_turnover(values)
