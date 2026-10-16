"""Independent pandas/NumPy reconciliation against the original absolute release."""

from __future__ import annotations

import numpy as np


def verify_absolute_frame(frame, base: dict) -> int:
    """Reject changed inputs even if dates and denominators are unchanged."""
    if (len(frame), frame.symbol.nunique(), int(frame.market_cap_usd.lt(1e8).sum())) != (
        base["eligible_observations"],
        base["unique_stocks"],
        base["below_100m_observations"],
    ):
        raise ValueError("absolute universe mismatch")
    codes = np.searchsorted([1e7, 1e8, 1e9, 1e10], frame.market_cap_usd.to_numpy(), side="right")
    cells = 0
    for index, b in enumerate(base["buckets"]):
        rows = frame.loc[codes == index]
        if (len(rows), rows.symbol.nunique()) != (b["observations"], b["count"]):
            raise ValueError("absolute bucket membership mismatch")
        cells += 2
        for col, prefix in [("adv20_usd", ""), ("median20_usd", "median20_")]:
            values = rows[col].to_numpy()
            for key, fn in [
                ("median_usd", np.median),
                ("mean_usd", np.mean),
                ("p90_usd", lambda a: np.quantile(a, 0.9)),
            ]:
                actual = b[prefix + key]
                matches = (
                    actual is None
                    if not len(values)
                    else actual is not None
                    and np.isclose(actual, fn(values), rtol=1e-10, atol=1e-6)
                )
                if not matches:
                    raise ValueError("absolute turnover statistics mismatch")
                cells += 1
    return cells
