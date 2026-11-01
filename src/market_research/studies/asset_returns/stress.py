"""Contemporaneous stress descriptions, never formation-time policy signals."""

from __future__ import annotations


from .analysis import validate_levels

PAIRS = [
    ("equity_bond", "total", "bond"),
    ("equity_gold", "total", "gold"),
    ("bond_gold", "bond", "gold"),
]


def conditional_stress(frame) -> list[dict]:
    data = validate_levels(frame, ["total", "bond", "gold", "cpi"])
    r = data[["total", "bond", "gold"]].pct_change(fill_method=None)
    inflation = data.cpi / data.cpi.shift(12) - 1
    masks = {
        "all": r.total.notna(),
        "equity_down_5pct": r.total <= -0.05,
        "bond_down_1pct": r.bond <= -0.01,
        "inflation_3pct": inflation >= 0.03,
    }
    rows = []
    for ident, mask in masks.items():
        selected = r.loc[mask]
        corr, joint = {}, {}
        for key, a, b in PAIRS:
            valid = len(selected) >= 12 and min(selected[a].std(), selected[b].std()) > 1e-12
            corr[key] = float(selected[a].corr(selected[b])) if valid else None
            joint[key] = (
                float(((selected[a] < 0) & (selected[b] < 0)).mean()) if len(selected) else None
            )
        rows.append(
            {
                "id": ident,
                "months": len(selected),
                "correlations": corr,
                "joint_negative_fraction": joint,
                "mean_monthly_returns": {
                    name: float(selected[name].mean()) if len(selected) else None
                    for name in selected
                },
                "minimum_monthly_returns": {
                    name: float(selected[name].min()) if len(selected) else None
                    for name in selected
                },
                "inflation_eligible_months": int(inflation.notna().sum()),
            }
        )
    return rows


def event_recovery(frame, events) -> list[dict]:
    data = validate_levels(frame, ["total", "bond", "gold"])
    rows = []
    for ident, start, end in events:
        event = data.loc[data.date.between(start, end)]
        if (
            len(event) < 2
            or event.date.iloc[0].date().isoformat() != start
            or event.date.iloc[-1].date().isoformat() != end
        ):
            rows.append({"id": ident, "status": "unavailable_event_coverage"})
            continue
        row = {"id": ident, "start": start, "end": end}
        for label, col in [("equity", "total"), ("bond", "bond"), ("gold", "gold")]:
            # Recover from this event's maximum-drawdown peak, not a cherry-picked low.
            dd = event[col] / event[col].cummax() - 1
            trough = int(dd.idxmin())
            peak = int(data.loc[event.index[0] : trough, col].idxmax())
            if float(dd.min()) >= -1e-12:
                peak = trough = int(event.index[0])
            later = data.loc[trough:]
            recovered = later[later[col] >= data.loc[peak, col] - 1e-12]
            recovery_date = recovered.date.iloc[0] if len(recovered) else None
            observed = recovery_date if recovery_date is not None else data.date.iloc[-1]
            row[label] = {
                "maximum_drawdown": float(dd.min()),
                "peak_date": data.date.iloc[peak].date().isoformat(),
                "trough_date": data.date.iloc[trough].date().isoformat(),
                "recovered_at": recovery_date.date().isoformat()
                if recovery_date is not None
                else None,
                "censored": recovery_date is None,
                "underwater_observed_months": int(
                    observed.to_period("M").ordinal - data.date.iloc[peak].to_period("M").ordinal
                ),
            }
        rows.append(row)
    return rows
