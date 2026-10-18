import numpy as np
import pytest


def test_missing_days_remain_unresolved_and_do_not_disappear_from_denominator():
    from market_research.liquidity_exit import evaluate_budget

    r = evaluate_budget(
        np.array([[100.0, 100.0], [100.0, np.nan], [0.0, 0.0], [np.nan, 500.0]]), 150, 1
    )
    assert r["covered"].tolist() == [True, False, False, True]
    assert r["unresolved"].tolist() == [False, True, False, False]
    assert r["not_covered"].tolist() == [False, False, True, False]
    assert r["first_day"][[0, 3]].tolist() == [2, 2]
    assert r["uncredited_fraction"].tolist() == pytest.approx([0, 1 / 3, 1, 0])


def test_lower_limit_touch_blocks_sells_but_upper_limit_does_not():
    from market_research.liquidity_exit import sell_credit

    assert sell_credit(100, 9, 11, 9, False) == (100, 0, "lower_touch")
    assert sell_credit(100, 10, 11, 9, False) == (100, 100, "credited")
    assert sell_credit(100, 11, 11, 9, False) == (100, 100, "credited")
    raw, guarded, state = sell_credit(100, 10, 11, None, False)
    assert raw == 100 and np.isnan(guarded) and state == "unknown_limit"
    assert sell_credit(None, None, None, None, True) == (0, 0, "full_suspension")
    raw, guarded, state = sell_credit(None, None, None, None, False)
    assert np.isnan(raw) and np.isnan(guarded) and state == "missing_daily"


def test_budget_rejects_invalid_inputs_and_keeps_genuine_zero():
    from market_research.liquidity_exit import evaluate_budget

    for values, q, p in [
        (np.array([[-1.0]]), 100, 0.03),
        (np.array([[np.inf]]), 100, 0.03),
        (np.zeros((1, 2)), 0, 0.03),
        (np.zeros((1, 2)), 100, 2),
    ]:
        with pytest.raises(ValueError):
            evaluate_budget(values, q, p)
    assert evaluate_budget(np.zeros((2, 2)), 100, 0.03)["not_covered"].all()


def test_frozen_path_keeps_missing_future_names_and_uses_only_future_dates():
    import duckdb
    from market_research.liquidity_exit import frozen_paths

    c = duckdb.connect()
    c.execute(
        "CREATE TABLE f(symbol VARCHAR,date DATE,eligible BOOLEAN,market_cap_usd DOUBLE,adv20_usd DOUBLE,usd_per_native DOUBLE)"
    )
    c.execute(
        "INSERT INTO f VALUES ('x','2024-01-31',true,2e8,100,1),('y','2024-01-31',true,2e8,100,1),('x','2024-02-01',true,2e9,100,1),('x','2024-02-02',true,2e9,100,1)"
    )
    c.execute("CREATE TABLE d(symbol VARCHAR,date DATE,amount DOUBLE,low DOUBLE,high DOUBLE)")
    c.execute(
        "INSERT INTO d VALUES ('x','2024-01-31',999,10,11),('x','2024-02-01',1,10,11),('x','2024-02-02',2,10,11)"
    )
    c.execute("CREATE TABLE l(symbol VARCHAR,date DATE,down_limit DOUBLE)")
    c.execute("CREATE TABLE s(symbol VARCHAR,date DATE,full_suspension BOOLEAN)")
    r = frozen_paths(c, 2024, 2024, horizon=2)
    assert len(r) == 4 and r.h.tolist() == [1, 2, 1, 2]
    assert r.bucket.tolist() == [2] * 4
    assert r.loc[r.symbol == "x", "amount"].tolist() == [1, 2]
    assert r.loc[r.symbol == "y", "amount"].isna().all()


def test_tail_summary_does_not_report_a_complete_exit_maximum_when_some_names_are_censored():
    from market_research.liquidity_exit import summarize_budget

    r = summarize_budget(np.array([[100.0, 100.0], [0.0, 0.0], [np.nan, 0.0]]), 150, 1)
    assert r["stocks"] == 3 and r["covered"] == 1 and r["not_covered"] == 1 and r["unresolved"] == 1
    assert r["covered_day_p50"] == 2 and r["all_names_day_max"] is None
    assert r["uncredited_fraction"] == pytest.approx(2 / 3)
    assert r["top_decile_uncredited_share"] == pytest.approx(0.5)
