"""Accounting and missing-data contracts for the grouped valuation study."""

import importlib
import importlib.util

import numpy as np
import pandas as pd
import pytest


def api(name):
    assert importlib.util.find_spec("market_research.valuation_groups") is not None, (
        "grouped valuation study is not implemented"
    )
    module = importlib.import_module("market_research.valuation_groups")
    fn = getattr(module, name, None)
    assert callable(fn), f"missing grouped valuation behavior: {name}"
    return fn


def test_non_st_requires_dated_known_name_and_positive_absence_is_not_enough():
    rows = pd.DataFrame({"ts_code": list("ABCDEFG"), "formation_date": ["20240131"] * 7,
                         "list_date": ["20200101"] * 6 + ["20240201"],
                         "delist_date": [None] * 7})
    names = pd.DataFrame([
        {"ts_code": c, "name": name, "start_date": "20200101", "end_date": None,
         "ann_date": ann, "change_reason": "other"}
        for c, name, ann in [("A", "Normal", "20200101"), ("B", "ST Beta", "20200101"),
                              ("C", "*ST Gamma", "20200101"), ("E", "Normal", "20240131"),
                              ("F", "Normal", "20200101"), ("G", "Normal", "20200101")]
    ])
    positive = pd.DataFrame({"ts_code": ["B", "C", "F"], "trade_date": ["20240131"] * 3,
                             "name": ["ST Beta", "*ST Gamma", "ST F"],
                             "available_from": ["20200101"] * 3})
    result = api("classify_groups")(rows, names, positive).set_index("ts_code")
    assert result.status.to_dict() == {"A": "non_st", "B": "st", "C": "star_st",
                                       "D": "unknown", "E": "unknown", "F": "unknown", "G": "unknown"}


def test_ambiguous_name_and_unavailable_positive_state_remain_unknown():
    rows = pd.DataFrame({"ts_code": ["A", "B"], "formation_date": ["20240131"] * 2,
                         "list_date": ["20200101"] * 2, "delist_date": [None] * 2})
    names = pd.DataFrame({"ts_code": ["A", "A", "B"], "name": ["Normal", "ST A", "*ST B"],
                          "start_date": ["20200101"] * 3, "end_date": [None] * 3,
                          "ann_date": ["20200101"] * 3, "change_reason": ["other"] * 3})
    positive = pd.DataFrame({"ts_code": ["A", "B"], "trade_date": ["20240131"] * 2,
                             "name": ["ST A", "*ST B"], "available_from": ["20200101", "20240201"]})
    assert api("classify_groups")(rows, names, positive).status.tolist() == ["unknown", "unknown"]


def test_grouped_statistics_separate_arithmetic_mean_from_ratio_of_totals():
    frame = pd.DataFrame({"ts_code": list("ABCD"), "status": ["st"] * 4,
                          "market_value": [100., 900., 20., 50.],
                          "denominator": [10., 30., -5., 0.], "multiple": [10., 30., np.nan, np.nan]})
    result = api("describe_metric")(frame, "multiple", "denominator", tail_count=2)
    assert result["valid_n"] == 2 and result["nonpositive_denominator_n"] == 2
    assert result["equal_weight_mean"] == 20.
    assert result["ratio_of_totals"] == 25.
    assert result["median"] == 20. and result["minimum"] == 10.
    assert result["minimum_records"][0]["ts_code"] == "A"
    assert result["minimum_records"][0]["denominator"] == 10.
    assert [x["ts_code"] for x in result["tail_records"]] == ["A", "B"]


def test_minimum_keeps_ties_and_invalid_amounts_never_become_cheap():
    frame = pd.DataFrame({"ts_code": list("ABCD"), "market_value": [100., 200., 300., 50.],
                          "denominator": [10., 20., np.inf, np.nan],
                          "multiple": [10., 10., 0., np.nan]})
    result = api("describe_metric")(frame, "multiple", "denominator", tail_count=1)
    assert result["valid_n"] == 2
    assert {x["ts_code"] for x in result["minimum_records"]} == {"A", "B"}
    assert len(result["tail_records"]) == 2
    empty = api("describe_metric")(frame.iloc[:0], "multiple", "denominator")
    assert empty["minimum"] is None and empty["ratio_of_totals"] is None


def test_public_projection_never_contains_security_rows_or_provider_amounts():
    private = {"valid_n": 2, "minimum": .4, "equal_weight_mean": 1.2,
               "ratio_of_totals": 1.1, "minimum_records": [{"ts_code": "A", "denominator": 10.}],
               "tail_records": [{"market_value": 100.}]}
    public = api("public_statistics")(private)
    assert public == {"valid_n": 2, "minimum": .4, "equal_weight_mean": 1.2, "ratio_of_totals": 1.1}


def test_legacy_comparison_accepts_concat_dtype_widening_but_requires_exact_values():
    fn = api("verify_legacy_values")
    monthly = pd.DataFrame({"age": [1, 2], "value": [1., 2.], "private_extra": [10., 20.]})
    concatenated = pd.DataFrame({"age": [1., 2.], "value": [1., 2.]})
    fn(monthly, concatenated)
    changed = monthly.copy()
    changed.loc[0, "value"] += 1e-9
    with pytest.raises(AssertionError):
        fn(changed, concatenated)


def price_rows(codes, day, values):
    return pd.DataFrame({"ts_code": codes, "trade_date": [day] * len(codes), "adj_close": values,
                         "amount": [100.] * len(codes), "is_suspended": [False] * len(codes),
                         "is_limit_up": [False] * len(codes), "is_limit_down": [False] * len(codes)})


def test_factor_period_ranks_cheap_first_and_missing_member_invalidates_its_basket():
    names = [f"S{i:02}" for i in range(25)]
    signal = pd.DataFrame({"ts_code": names, "multiple": range(1, 26), "delist_date": [None] * 25})
    entry = price_rows(names, "20240201", [100.] * 25)
    end = price_rows(names, "20240301", [125. - i for i in range(25)])
    end.loc[0, "adj_close"] = np.nan
    result, members = api("factor_period")(signal, entry, end, metric="multiple", minimum_names=25)
    assert result["signal_n"] == 25 and result["return_n"] == 24
    assert result["rank_ic"] == pytest.approx(1.)
    assert result["quintiles"][0]["selected_n"] == 5
    assert result["quintiles"][0]["complete"] is False
    assert result["quintiles"][0]["gross_return"] is None
    assert result["cheap_minus_expensive"] is None
    assert members.loc[members.ts_code.eq("S00"), "quintile"].iloc[0] == 1


@pytest.mark.filterwarnings("error:invalid value encountered:RuntimeWarning")
def test_factor_endpoint_constraints_and_delisting_do_not_zero_fill_returns():
    names = [f"S{i:02}" for i in range(25)]
    signal = pd.DataFrame({"ts_code": names, "multiple": range(1, 26), "delist_date": [None] * 25})
    signal.loc[2, "delist_date"] = "20240220"
    entry = price_rows(names, "20240201", [100.] * 25)
    end = price_rows(names, "20240301", [110.] * 25)
    entry.loc[0, "is_limit_up"] = True
    end.loc[1, "is_suspended"] = True
    result, members = api("factor_period")(signal, entry, end, metric="multiple", minimum_names=25)
    assert result["return_n"] == 22
    assert result["rank_ic"] is None  # constant returns have no defined rank correlation
    assert result["quintiles"][0]["gross_return"] is None
    assert members.forward_return.isna().sum() == 3


def test_factor_endpoint_cannot_precede_entry():
    names = [f"S{i:02}" for i in range(25)]
    signal = pd.DataFrame({"ts_code": names, "multiple": range(1, 26), "delist_date": [None] * 25})
    entry = price_rows(names, "20240301", [100.] * 25)
    end = price_rows(names, "20240201", [110.] * 25)
    with pytest.raises(ValueError, match="after entry"):
        api("factor_period")(signal, entry, end, metric="multiple")


def test_turnover_uses_drifted_previous_weights_and_cost_is_labelled_sensitivity():
    fn = api("cost_sensitivity")
    # After the previous month A and B carry 60/40; new target A/C is 50/50.
    result = fn({"A": .5, "C": .5}, {"A": .6, "B": .4}, .10, cost_bps=(0, 10, 30), liquidate=True)
    assert result["traded_notional"] == pytest.approx(2.)  # 1.0 rebalance + 1.0 terminal liquidation
    assert result["net_sensitivity"]["10"] == pytest.approx(.098)
    assert result["net_sensitivity"]["30"] == pytest.approx(.094)


def test_private_denominators_preserve_old_panel_and_allow_ratio_aggregation():
    # This exercises the established TTM/positive-denominator pipeline, not a second formula.
    from market_research.valuation_panel import make_panel

    periods = ["20240630", "20231231", "20230630"]
    source = {"ts_code": ["A"] * 3, "end_date": periods,
              "ann_date": ["20240801", "20240401", "20230801"],
              "_source_retrieved_at": ["2026-10-18T00:00:00Z"] * 3}
    statements = {"income": pd.DataFrame({**source, "n_income_attr_p": [60., 100., 40.], "comp_type": ["1"] * 3}),
                  "fina_indicator": pd.DataFrame({**source, "profit_dedt": [50., 90., 30.], "roe": [10.] * 3}),
                  "balancesheet": pd.DataFrame({**source, "total_hldr_eqy_exc_min_int": [500.] * 3,
                                                 "goodwill": [20.] * 3, "intan_assets": [30.] * 3,
                                                 "minority_int": [10.] * 3, "oth_eqt_tools_p_shr": [0.] * 3})}
    prices = pd.DataFrame({"ts_code": ["A"], "trade_date": ["20240830"], "total_mv": [.1]})
    legacy = make_panel(statements, prices, "20240830", require_observed=False)
    assert "market_value" not in legacy
    try:
        detail = make_panel(statements, prices, "20240830", require_observed=False, private_denominators=True)
    except TypeError:
        pytest.fail("private denominator audit is not implemented")
    assert detail.market_value.iloc[0] == 1000.
    assert detail.denominator_pe_deducted_proxy.iloc[0] == 110.
    assert detail.denominator_pb_ex_intangibles_proxy.iloc[0] == 450.
    pd.testing.assert_frame_equal(detail[legacy.columns], legacy)
