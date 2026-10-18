import numpy as np
import pandas as pd
import pytest

from market_research.valuation_panel import admitted, make_panel, trailing_values


def test_observed_timestamp_and_prior_day_disclosure_are_separate_gates():
    frame = pd.DataFrame([
        {"ts_code": "A", "end_date": "20260630", "ann_date": "20260820", "_source_retrieved_at": "2026-08-21T00:00:00Z", "value": 1},
        {"ts_code": "A", "end_date": "20260630", "ann_date": "20260825", "_source_retrieved_at": "2026-10-17T00:00:00Z", "value": 2},
        {"ts_code": "B", "end_date": "20260630", "ann_date": "20260831", "_source_retrieved_at": "2026-08-31T00:00:00Z", "value": 3},
    ])
    assert admitted(frame, "20260831", True).value.tolist() == [1]
    assert admitted(frame, "20260831", False).value.tolist() == [2]


def test_trailing_requires_all_matching_legs_and_annual_is_not_doubled():
    source = pd.DataFrame({"ts_code": ["A"] * 3, "end_date": ["20260630", "20251231", "20250630"], "x": [60., 100., 40.]})
    assert trailing_values(source.iloc[:2], source, "x").tolist() == [120., 100.]
    assert np.isnan(trailing_values(source.iloc[:1], source.iloc[:2], "x").iloc[0])


def statements():
    common = {"ts_code": ["A", "B"], "end_date": ["20251231"] * 2, "ann_date": ["20260401"] * 2, "_source_retrieved_at": ["2026-04-02T00:00:00Z"] * 2}
    return {
        "income": pd.DataFrame({**common, "report_type": ["1"] * 2, "n_income_attr_p": [10., -1.], "comp_type": ["1", "2"]}),
        "fina_indicator": pd.DataFrame({**common, "profit_dedt": [8., -2.], "roe": [10., -1.]}),
        "balancesheet": pd.DataFrame({**common, "report_type": ["1"] * 2, "total_hldr_eqy_exc_min_int": [50., 20.], "goodwill": [np.nan, 2.], "intan_assets": [1., 1.], "minority_int": [0., 1.], "oth_eqt_tools_p_shr": [np.nan, 0.]}),
    }


def test_missing_deduction_is_not_zero_and_loss_is_not_cheap():
    price = pd.DataFrame({"ts_code": ["A", "B"], "trade_date": ["20261016"] * 2, "total_mv": [1., 1.]})
    p = make_panel(statements(), price, "20261016", require_observed=True).set_index("ts_code")
    assert p.loc["A", "pb_parent"] == 200
    assert np.isnan(p.loc["A", "pb_ex_goodwill_proxy"])
    assert np.isnan(p.loc["B", "pe_ttm"])
    assert p.loc["B", "pe_ttm_nonpositive"]
    assert not p.common_five.any()


def test_duplicate_quote_keys_fail():
    price = pd.DataFrame({"ts_code": ["A", "A"], "trade_date": ["20261016"] * 2, "total_mv": [1., 1.]})
    with pytest.raises(ValueError, match="duplicate"):
        make_panel(statements(), price, "20261016", require_observed=True)


def test_missing_indicator_does_not_erase_independent_pe_and_pb():
    data = statements()
    data["fina_indicator"] = data["fina_indicator"].iloc[1:]
    price = pd.DataFrame({"ts_code": ["A", "B"], "trade_date": ["20261016"] * 2, "total_mv": [1., 1.]})
    p = make_panel(data, price, "20261016", require_observed=True).set_index("ts_code")
    assert p.loc["A", "pe_ttm"] == 1000
    assert p.loc["A", "pb_parent"] == 200
    assert np.isnan(p.loc["A", "pe_deducted_proxy"])
    assert not p.loc["A", "same_report_period"]


def test_age_guard_and_standard_report_filter():
    data = statements()
    data['income'].loc[0, 'report_type'] = '4'
    data['balancesheet'].loc[0, 'end_date'] = '20241231'
    price = pd.DataFrame({'ts_code': ['A', 'B'], 'trade_date': ['20261016'] * 2, 'total_mv': [1., 1.]})
    p = make_panel(data, price, '20261016', require_observed=True).set_index('ts_code')
    assert np.isnan(p.loc['A', 'pe_ttm'])
    assert np.isnan(p.loc['A', 'pb_parent'])
    assert p.loc['A', 'stale_statement']
    assert p.loc['A', 'pe_deducted_proxy'] == 1250


def test_different_report_periods_preserve_metrics_but_leave_common_sample():
    data = statements()
    data['balancesheet'].loc[0, 'end_date'] = '20250630'
    data['balancesheet'].loc[0, 'goodwill'] = 0.
    price = pd.DataFrame({'ts_code': ['A', 'B'], 'trade_date': ['20261016'] * 2, 'total_mv': [1., 1.]})
    p = make_panel(data, price, '20261016', require_observed=True).set_index('ts_code')
    assert p.loc['A', 'all_metrics_available']
    assert not p.loc['A', 'common_five']


def test_rank_overlap_is_jaccard_and_keeps_boundary_ties():
    from market_research.valuation_panel import rank_comparison
    frame = pd.DataFrame({'ts_code': list('ABCDE'), 'common_five': [True] * 5,
                          'a': [1., 1., 3., 4., 5.], 'b': [1., 3., 1., 4., 5.]})
    result = rank_comparison(frame, 'a', 'b')
    assert result['first_selected'] == result['second_selected'] == 2
    assert result['bottom_quintile_jaccard'] == pytest.approx(1 / 3)


def test_snapshot_loader_rejects_changed_manifest_without_resealing(tmp_path):
    import hashlib
    import json
    from scripts.analyze_valuation_panel import load_snapshot
    original = b'status: completed\nimmutable_snapshot: true\n'
    (tmp_path / 'manifest.yml').write_bytes(original + b'# migrated path\n')
    (tmp_path / 'SEALED.json').write_text(json.dumps({'manifest_sha256': hashlib.sha256(original).hexdigest()}))
    with pytest.raises(ValueError, match='vintage manifest seal mismatch'):
        load_snapshot(tmp_path, {})
