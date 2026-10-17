import pandas as pd

from market_research.liquidity_stability import summarize_monthly_stability


def test_stability_uses_month_weighted_medians_and_reports_coverage():
    frame = pd.DataFrame(
        [
            {"market": "A", "year": 2025, "bucket": "<10m", "month": "2025-01", "monthly_adv_median": 10.0, "monthly_turnover_rate_median": 0.01, "security_days": 100},
            {"market": "A", "year": 2025, "bucket": "<10m", "month": "2025-02", "monthly_adv_median": 30.0, "monthly_turnover_rate_median": 0.03, "security_days": 900},
        ]
    )
    row = summarize_monthly_stability(frame)[0]
    assert row["months"] == 2
    assert row["security_days"] == 1000
    assert row["adv20_median_of_months_usd"] == 20.0
    assert row["adv20_monthly_p25_usd"] == 15.0
    assert row["adv20_monthly_p75_usd"] == 25.0
    assert row["turnover_rate_median_of_months"] == 0.02
