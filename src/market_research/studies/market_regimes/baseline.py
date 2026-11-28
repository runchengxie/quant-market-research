"""Causal feature selection; caller retains responsibility for historical vintages."""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

FEATURES = ["trend", "realized_volatility", "dispersion"]


def _aware(values, name):
    result = pd.DatetimeIndex(values)
    if result.tz is None or result.hasnans:
        raise ValueError(f"{name} must contain timezone-aware nonmissing timestamps")
    return result.tz_convert("UTC")


def classify_market_states(
    features: pd.DataFrame,
    *,
    decisions: pd.DatetimeIndex,
    training_end: pd.Timestamp,
    asset_id: str,
    return_kind: str,
    min_training: int,
    high_quantile: float,
) -> dict:
    """Fit two quantiles once; select the latest strictly visible observation.

    Trend is positive only above zero. Volatility/dispersion are high strictly
    above their training quantile. No model probability or change-point test is
    implied by these labels. Inputs must already embody verified universe,
    corporate-action, feature-definition and vintage policies.
    """
    if (
        not isinstance(asset_id, str)
        or not asset_id.strip()
        or return_kind not in {"price", "total_return"}
    ):
        raise ValueError("explicit asset identity and price/total_return kind required")
    if type(min_training) is not int or min_training < 3:
        raise ValueError("min_training must be an integer at least three")
    if (
        isinstance(high_quantile, bool)
        or not np.isfinite(high_quantile)
        or not 0 < high_quantile < 1
    ):
        raise ValueError("high_quantile must lie in (0, 1)")
    if not set(["feature_time", "available_at", *FEATURES]) <= set(features):
        raise ValueError("feature_time, available_at and all baseline features required")
    frame = features[["feature_time", "available_at", *FEATURES]].copy()
    frame["feature_time"] = _aware(frame.feature_time, "feature_time")
    frame["available_at"] = _aware(frame.available_at, "available_at")
    end = _aware([training_end], "training_end")[0]
    decisions = _aware(decisions, "decisions")
    if (
        decisions.empty
        or not decisions.is_monotonic_increasing
        or decisions.has_duplicates
        or (decisions <= end).any()
    ):
        raise ValueError("unique increasing decisions strictly after training_end required")
    if frame.feature_time.duplicated().any() or (frame.available_at < frame.feature_time).any():
        raise ValueError("unique feature times and non-anticipating availability required")
    frame[FEATURES] = frame[FEATURES].apply(pd.to_numeric, errors="raise").astype(float)
    if np.isinf(frame[FEATURES].to_numpy()).any():
        raise ValueError("infinite features are invalid")
    if (frame[["realized_volatility", "dispersion"]] < 0).any().any():
        raise ValueError("volatility and dispersion must be nonnegative")
    frame = frame.sort_values("feature_time")
    train = frame.loc[(frame.feature_time <= end) & (frame.available_at <= end)].dropna()
    if len(train) < min_training:
        raise ValueError("insufficient training observations")
    thresholds = train[["realized_volatility", "dispersion"]].quantile(high_quantile)
    calibration = dict(
        schema_version="market-research.state-calibration.v1",
        asset_id=asset_id,
        return_kind=return_kind,
        training_end=end.isoformat(),
        training_rows=len(train),
        high_quantile=high_quantile,
        thresholds=thresholds.to_dict(),
        training_sha256=_training_digest(train),
        training_serialization="utc-ns-float-hex.v1",
        historical_vintage_verified=False,
    )
    rows, previous = [], None
    for decision in decisions:
        known = frame.loc[(frame.feature_time < decision) & (frame.available_at < decision)]
        row = dict(
            decision_time=decision,
            feature_time=pd.NaT,
            available_at=pd.NaT,
            state_label=None,
            state_probability=np.nan,
            change_event=None,
            status="no_visible_features",
            fitted_through=end,
        )
        if not known.empty:
            observation = known.iloc[-1]
            row.update(feature_time=observation.feature_time, available_at=observation.available_at)
            if observation[FEATURES].isna().any():
                row["status"] = "missing_features"
            else:
                label = "up" if observation.trend > 0 else "nonpositive"
                if observation.trend < 0:
                    label = "down"
                label += (
                    "__high_vol"
                    if observation.realized_volatility > thresholds.realized_volatility
                    else "__low_vol"
                )
                label += (
                    "__high_dispersion"
                    if observation.dispersion > thresholds.dispersion
                    else "__low_dispersion"
                )
                row.update(
                    state_label=label,
                    status="descriptive",
                    change_event=(label != previous) if previous is not None else None,
                )
        previous = row["state_label"]
        rows.append(row)
    return {"states": pd.DataFrame(rows), "calibration": calibration}


def _training_digest(train):
    rows = [
        [
            row.feature_time.value,
            row.available_at.value,
            *[float(getattr(row, column)).hex() for column in FEATURES],
        ]
        for row in train.itertuples(index=False)
    ]
    payload = ["utc-ns-float-hex.v1", ["feature_time", "available_at", *FEATURES], rows]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()
