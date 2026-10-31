"""Fail closed on changed history or incompatible monthly asset-study contracts.

A passing gate is a compatibility check, not publication authorization or a
certification of source correctness. Historical revisions require a new study.
"""

from __future__ import annotations

import pandas as pd

from .closure import monthly_frame

CONTRACT_KEYS = ("currency", "return_basis", "cost_basis")


def validate_update(
    previous: pd.DataFrame,
    candidate: pd.DataFrame,
    previous_contract: dict,
    candidate_contract: dict,
) -> dict:
    for key in CONTRACT_KEYS:
        if not previous_contract.get(key) or previous_contract[key] != candidate_contract.get(key):
            raise ValueError(f"incompatible or missing {key}")
    if candidate_contract["cost_basis"] not in {
        "per_traded_notional",
        "annual_wealth_drag",
        "none",
    }:
        raise ValueError("unknown cost_basis")
    old, new = monthly_frame(previous), monthly_frame(candidate)
    if list(old.columns) != list(new.columns):
        raise ValueError("monthly schema changed")
    if len(new) < len(old) or not old.equals(new.iloc[: len(old)].reset_index(drop=True)):
        raise ValueError("history changed; preserve old release and review a revision separately")
    return {
        "status": "compatible_history",
        "previous_months": len(old),
        "candidate_months": len(new),
        "appended_months": len(new) - len(old),
        "published": False,
    }
