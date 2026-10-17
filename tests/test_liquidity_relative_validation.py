import pandas as pd
import pytest

from market_research.liquidity_relative_validation import verify_absolute_frame


def sample():
    frame = pd.DataFrame(
        dict(
            symbol=["one", "two"],
            market_cap_usd=[2e8, 3e8],
            adv20_usd=[10.0, 30.0],
            median20_usd=[8.0, 24.0],
        )
    )
    bucket = dict(
        observations=2,
        count=2,
        median_usd=20.0,
        mean_usd=20.0,
        p10_usd=12.0,
        p25_usd=15.0,
        p75_usd=25.0,
        p90_usd=28.0,
        zero_adv20_observations=0,
        zero_adv20_share=0.0,
        median20_median_usd=16.0,
        median20_mean_usd=16.0,
        median20_p10_usd=9.6,
        median20_p25_usd=12.0,
        median20_p75_usd=20.0,
        median20_p90_usd=22.4,
    )
    empty = dict(
        bucket,
        observations=0,
        count=0,
        zero_adv20_observations=0,
        zero_adv20_share=None,
        **{k: None for k in bucket if k not in ("observations", "count", "zero_adv20_observations", "zero_adv20_share")},
    )
    base = dict(
        eligible_observations=2,
        unique_stocks=2,
        below_100m_observations=0,
        buckets=[empty, empty, bucket, empty, empty],
    )
    return frame, base


def test_absolute_statistics_bind_relative_inputs_to_original_release():
    frame, base = sample()
    assert verify_absolute_frame(frame, base) == 80
    doubled = frame.copy()
    doubled[["adv20_usd", "median20_usd"]] *= 2
    with pytest.raises(ValueError, match="absolute"):
        verify_absolute_frame(doubled, base)
    moved = frame.copy()
    moved["market_cap_usd"] = 2e9
    with pytest.raises(ValueError, match="absolute"):
        verify_absolute_frame(moved, base)


def test_zero_adv20_aggregates_are_independently_reconciled():
    frame, base = sample()
    frame.loc[0, "adv20_usd"] = 0
    bucket = base["buckets"][2]
    bucket["median_usd"] = 15.0
    bucket["mean_usd"] = 15.0
    bucket["p10_usd"] = 3.0
    bucket["p25_usd"] = 7.5
    bucket["p75_usd"] = 22.5
    bucket["p90_usd"] = 27.0
    bucket["zero_adv20_observations"] = 1
    bucket["zero_adv20_share"] = 0.5
    bucket["median20_p10_usd"] = 9.6
    bucket["median20_p25_usd"] = 12.0
    bucket["median20_median_usd"] = 16.0
    bucket["median20_p75_usd"] = 20.0
    bucket["median20_p90_usd"] = 22.4
    bucket["zero_adv20_observations"] = 0
    with pytest.raises(ValueError, match="zero-ADV20"):
        verify_absolute_frame(frame, base)
    bucket["zero_adv20_observations"] = 1
    with pytest.raises(ValueError, match="zero-ADV20 share mismatch"):
        verify_absolute_frame(frame, {**base, "buckets": [base["buckets"][0], base["buckets"][1], {**bucket, "zero_adv20_share": 0.4}, *base["buckets"][3:]]})
