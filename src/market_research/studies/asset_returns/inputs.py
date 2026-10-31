"""Study-local readers for frozen data-owner exports and monthly endpoints."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def read_frozen_response(path: Path, expected_sha256: str) -> pd.DataFrame:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('frozen response hash mismatch')
    payload = json.loads(raw)
    if payload.get('code') != 0 or not payload.get('data'):
        raise ValueError('response did not succeed with data')
    data = payload['data']
    frame = pd.DataFrame(data['items'], columns=data['fields'])
    if frame.empty:
        raise ValueError('empty data is not verified coverage')
    return frame


def month_end_levels(frame: pd.DataFrame, calendar: pd.DatetimeIndex) -> pd.DataFrame:
    """Require exact final-session marks; no stale quote or forward fill.

Calendar must include complete months and be verified independently. Input
may include additional days; only the calendar's monthly endpoints are used.
This verifies endpoints, not all intervening daily marks.
    """
    dates = pd.DatetimeIndex(calendar)
    if dates.empty or dates.hasnans or dates.duplicated().any():
        raise ValueError('calendar must contain unique nonmissing sessions')
    endpoints = pd.Series(dates, index=dates.to_period('M')).groupby(level=0).max()
    if not np.all(np.diff(endpoints.index.astype('int64')) == 1):
        raise ValueError('calendar has missing months')
    data = frame[['date', 'close']].copy()
    data['date'] = pd.to_datetime(data.date, errors='raise')
    data['close'] = pd.to_numeric(data.close, errors='raise')
    if data.date.duplicated().any() or data.date.isna().any():
        raise ValueError('duplicate or missing quote dates')
    selected = data.set_index('date').reindex(pd.DatetimeIndex(endpoints.to_numpy()))
    if not np.isfinite(selected.close).all() or (selected.close <= 0).any():
        raise ValueError('missing or invalid last-session quote')
    return pd.DataFrame({'date': endpoints.index.to_timestamp('M'),
                         'close': selected.close.to_numpy()})
