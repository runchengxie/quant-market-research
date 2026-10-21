import importlib.util
from pathlib import Path

import pandas as pd


spec = importlib.util.spec_from_file_location(
    "followups", Path(__file__).parents[1] / "scripts/extend_grouped_valuation_diagnostics.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def panel():
    return pd.DataFrame(
        [
            dict(ts_code=s, formation_date=f"{d:02}", status="non_st", pb_parent=float(i + 1))
            for d in range(14)
            for i, s in enumerate("ABCDE")
        ]
    )


def test_persistence_uses_prior_twelve_scheduled_snapshots():
    p = panel()
    r = module.historical_labels(p, "pb_parent")
    assert r.loc[r.formation_date.eq("11"), "condition"].item() == "history_insufficient"
    assert r.loc[r.formation_date.eq("12"), "condition"].item() == "persistent_cheap"
    assert r.loc[r.formation_date.eq("12"), "prior_cheap_12"].item() == 12


def test_one_off_and_missing_history_not_compressed():
    p = panel()
    p.loc[p.ts_code.eq("B") & p.formation_date.eq("13"), "pb_parent"] = 0.5
    r = module.historical_labels(p, "pb_parent")
    b = r.loc[r.formation_date.eq("13")]
    assert b.condition.item() == "one_off_cheap"
    assert b.prior_cheap_12.item() == 0
    p = p.loc[~(p.ts_code.eq("B") & p.formation_date.isin(["02", "03", "04"]))]
    r = module.historical_labels(p, "pb_parent")
    assert r.loc[r.formation_date.eq("13"), "condition"].item() == "history_insufficient"


def test_future_values_do_not_change_history_labels():
    p = panel()
    before = module.historical_labels(p, "pb_parent")
    p.loc[p.formation_date.eq("13"), "pb_parent"] = 100
    after = module.historical_labels(p, "pb_parent")
    pd.testing.assert_frame_equal(
        before.loc[before.formation_date.lt("13")], after.loc[after.formation_date.lt("13")]
    )
