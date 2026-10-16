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
        p90_usd=28.0,
        median20_median_usd=16.0,
        median20_mean_usd=16.0,
        median20_p90_usd=22.4,
    )
    empty = dict(
        bucket,
        observations=0,
        count=0,
        **{k: None for k in bucket if k not in ("observations", "count")},
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
    assert verify_absolute_frame(frame, base) == 40
    doubled = frame.copy()
    doubled[["adv20_usd", "median20_usd"]] *= 2
    with pytest.raises(ValueError, match="absolute"):
        verify_absolute_frame(doubled, base)
    moved = frame.copy()
    moved["market_cap_usd"] = 2e9
    with pytest.raises(ValueError, match="absolute"):
        verify_absolute_frame(moved, base)
