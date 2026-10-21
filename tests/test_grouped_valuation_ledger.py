from market_research.studies.grouped_valuation_ledger import run_ledger, verify_ledger
import pytest


def quote(price=10.0, **updates):
    row = dict(
        adj_close=price,
        close=price,
        high=price,
        low=price,
        up_limit=20.0,
        down_limit=1.0,
        amount=100.0,
        is_suspended=False,
        is_limit_up=False,
        is_limit_down=False,
    )
    row.update(updates)
    return row


def run(prices, cohorts, **kwargs):
    days = sorted(prices)
    return run_ledger(days, lambda d: prices[d], cohorts, initial_cash=100.0, **kwargs)


def test_blocked_entry_cash_not_redistributed():
    p = {"01": {"A": quote(), "B": quote(is_limit_up=True)}}
    r = run(p, {"01": ["A", "B"]}, fill_policy="close_flag", fee_bps=0)
    assert r["daily"][0]["cash"] == 50
    assert r["holdings"][0]["units"] == 5
    assert len(r["orders"]) == 2
    assert r["orders"][1]["reason"] == "upper_limit"
    verify_ledger(r, 100.0)


def test_delayed_exit_crosses_rebalance_and_is_not_free_cash():
    p = {d: {"A": quote(), "B": quote(), "C": quote()} for d in ["01", "02", "03", "04"]}
    p["02"]["A"]["is_limit_down"] = True
    p["03"]["A"]["is_limit_down"] = True
    r = run(p, {"01": ["A"], "02": ["B"], "03": ["C"]}, fill_policy="close_flag", fee_bps=0)
    assert [d["cash"] for d in r["daily"]] == [0, 0, 0, 100]
    sells = [o for o in r["orders"] if o["side"] == "sell"]
    assert [o["status"] for o in sells] == ["pending", "pending", "filled"]
    assert {o["requested_date"] for o in sells} == {"02"}
    verify_ledger(r, 100.0)


def test_missing_mark_stays_unknown_then_recovers_without_future_fill():
    r = run({"01": {"A": quote()}, "02": {}, "03": {"A": quote(12)}}, {"01": ["A"]}, fee_bps=0)
    assert r["daily"][1]["strict_nav"] is None
    assert r["daily"][1]["zero_unresolved_nav"] == 0
    assert r["holdings"][1]["last_observed_date"] == "01"
    assert r["holdings"][1]["units"] == 10
    assert r["daily"][2]["strict_nav"] == 120
    verify_ledger(r, 100.0)


def test_terminal_zero_is_valuation_not_cash_or_sale():
    r = run(
        {"01": {"A": quote()}, "02": {"A": quote(20)}, "03": {"A": quote(30)}},
        {"01": ["A"]},
        delist_dates={"A": "02"},
        liquidation_date="02",
        fee_bps=0,
    )
    assert r["daily"][-1]["cash"] == 0
    assert r["daily"][-1]["strict_nav"] is None
    assert r["holdings"][-1]["units"] == 10
    assert r["holdings"][-1]["mark_source"] == "unresolved_terminal"
    assert all(o["status"] == "pending" for o in r["orders"] if o["side"] == "sell")
    verify_ledger(r, 100.0)


def test_fee_cash_identity_and_one_time_fee_on_retry():
    p = {d: {"A": quote()} for d in ["01", "02", "03"]}
    p["02"]["A"]["is_limit_down"] = True
    r = run(p, {"01": ["A"]}, fill_policy="close_flag", liquidation_date="02", fee_bps=100)
    assert r["daily"][-1]["cash"] == pytest.approx(100 / 1.01 * 0.99)
    assert sum(o["fee"] for o in r["orders"]) == pytest.approx(100 - 100 / 1.01 * 0.99)
    verify_ledger(r, 100.0)
    r["daily"][-1]["cash"] += 1
    with pytest.raises(AssertionError):
        verify_ledger(r, 100.0)


def test_touch_is_more_conservative_than_close_flag():
    p = {"01": {"A": quote()}}
    p["01"]["A"]["high"] = 20
    assert run(p, {"01": ["A"]}, fee_bps=0)["daily"][0]["cash"] == 100
    assert run(p, {"01": ["A"]}, fee_bps=0, fill_policy="close_flag")["daily"][0]["cash"] == 0


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("amount", 0, "no_positive_amount"),
        ("is_suspended", True, "suspended"),
        ("is_limit_up", None, "unknown_flags"),
        ("up_limit", None, "unknown_limit_price"),
        ("adj_close", float("nan"), "missing_price"),
    ],
)
def test_invalid_daily_data_blocks_entry(field, value, reason):
    q = quote()
    q[field] = value
    r = run({"01": {"A": q}}, {"01": ["A"]}, fee_bps=0)
    assert r["orders"][0]["reason"] == reason
    assert r["daily"][0]["cash"] == 100


def test_no_reentry_while_old_exit_is_pending():
    p = {d: {"A": quote()} for d in ["01", "02"]}
    p["02"]["A"]["is_limit_down"] = True
    r = run(p, {"01": ["A"], "02": ["A"]}, fill_policy="close_flag", fee_bps=0)
    assert r["orders"][-1]["reason"] == "pending_old_exit"
    assert r["holdings"][-1]["units"] == 10


def test_raw_mode_and_separate_actions_fail_closed():
    for options in [{"unit_mode": "raw_shares"}, {"corporate_actions": [{"cash_div": 1}]}]:
        with pytest.raises(ValueError):
            run({"01": {"A": quote()}}, {"01": ["A"]}, **options)


def test_duplicate_members_bad_calendar_and_costs_rejected():
    with pytest.raises(ValueError):
        run({"01": {"A": quote()}}, {"01": ["A", "A"]})
    with pytest.raises(ValueError):
        run({"01": {"A": quote()}}, {"02": ["A"]})
    with pytest.raises(ValueError):
        run({"01": {"A": quote()}}, {"01": ["A"]}, fee_bps=-1)


def test_future_quotes_do_not_change_past_ledger():
    p = {"01": {"A": quote()}, "02": {}, "03": {"A": quote(12)}}
    a = run(p, {"01": ["A"]}, fee_bps=0)
    p["03"]["A"] = quote(900)
    b = run(p, {"01": ["A"]}, fee_bps=0)
    assert a["daily"][:2] == b["daily"][:2]
    assert a["holdings"][:2] == b["holdings"][:2]
