import numpy as np
import pandas as pd
import pytest


def inputs():
    dates = pd.date_range("2020-01-01", periods=8, tz="Asia/Shanghai")
    return pd.DataFrame(
        {
            "feature_time": dates,
            "available_at": dates + pd.Timedelta(hours=16),
            "trend": [-1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0],
            "realized_volatility": [1.0, 2.0, 3.0, 4.0, 2.0, 5.0, 1.0, 2.0],
            "dispersion": [1.0, 2.0, 3.0, 4.0, 2.0, 5.0, 1.0, 2.0],
        }
    )


def run(frame=None):
    from market_research.studies.market_regimes import classify_market_states

    return classify_market_states(
        inputs() if frame is None else frame,
        decisions=pd.date_range("2020-01-06", periods=3, tz="Asia/Shanghai"),
        training_end=pd.Timestamp("2020-01-04 20:00", tz="Asia/Shanghai"),
        asset_id="synthetic-price-index",
        return_kind="price",
        min_training=4,
        high_quantile=0.75,
    )


def test_decision_uses_only_strictly_available_features_and_records_calibration():
    result = run()
    labels = result["states"]
    assert labels.iloc[0].feature_time == inputs().feature_time.iloc[4]
    assert labels.iloc[0].state_label == "up__low_vol__low_dispersion"
    assert labels.iloc[1].state_label == "down__high_vol__high_dispersion"
    assert labels.state_probability.isna().all()
    assert result["calibration"]["training_rows"] == 4
    assert result["calibration"]["asset_id"] == "synthetic-price-index"


def test_future_extreme_does_not_change_past_states_or_calibration():
    frame = inputs()
    frame.loc[7, ["trend", "realized_volatility", "dispersion"]] = 1e10
    original, changed = run(), run(frame)
    pd.testing.assert_frame_equal(original["states"], changed["states"])
    assert original["calibration"] == changed["calibration"]


def test_missing_signal_has_no_fallback_or_claim_of_probability():
    frame = inputs()
    frame.loc[4, "trend"] = np.nan
    row = run(frame)["states"].iloc[0]
    assert row.status == "missing_features"
    assert pd.isna(row.state_label)
    assert pd.isna(row.change_event)


@pytest.mark.parametrize("field", ["realized_volatility", "feature_time"])
def test_training_hash_preserves_float_and_submillisecond_identity(field):
    frame = inputs()
    if field == "feature_time":
        frame[field] = frame[field].dt.as_unit("ns")
        frame.loc[1, field] += pd.Timedelta(nanoseconds=1)
    else:
        frame.loc[1, field] += 1e-12
    assert run(frame)["calibration"]["training_sha256"] != run()["calibration"]["training_sha256"]
    renamed = inputs().set_axis(range(10, 18))
    assert run(renamed)["calibration"] == run()["calibration"]


@pytest.mark.parametrize("case", ["naive", "late", "duplicate", "infinite", "few"])
def test_invalid_or_unusable_training_inputs_fail(case):
    frame = inputs()
    if case == "naive":
        frame["available_at"] = frame.available_at.dt.tz_localize(None)
    elif case == "late":
        frame["available_at"] = frame.available_at - pd.Timedelta(days=2)
    elif case == "duplicate":
        frame = pd.concat([frame, frame.iloc[[0]]])
    elif case == "infinite":
        frame.loc[0, "trend"] = np.inf
    else:
        frame = frame.iloc[2:]
    with pytest.raises(ValueError):
        run(frame)
