"""The public projection never forwards private source fields."""
import copy
import json
from pathlib import Path

import pytest

from scripts.review_microcap_followup import ARMS, METRICS, project


def fixture():
    rows = [{"arm": arm, **dict.fromkeys(METRICS, "0.1"), "private_path": "/private"} for arm in ARMS]
    support = {key: {"formations": 138, "different": 132, "different_2016plus": 122} for key in (
        "support_no_buffer", "support_buffer", "shared_scores_no_buffer", "shared_scores_buffer",
        "coverage_s45_b40", "coverage_s45_b60")}
    support["signal_checks"] = dict(common_rows=514750, raw_max_abs_error=0, identical_input_score_max_abs_error=0)
    target = dict(names=597, stock_months=5400, queried_names=483, unqueried_names=114,
                  unqueried_stock_months=921, implemented_ex_date_field_audit={"stock_positive_missing_listing_date": 1})
    return [rows, support, {"status": "completed", "target_summary": {"45": target, "90": target}, "inputs": ["/private"]},
            {"synthetic_accounting_identity": {"max_daily_abs_difference": 1e-15}},
            {"closed_original_runtime_gap": False, "records": ["/private"]}]


def test_projection_is_allowlisted_and_rejects_changed_scope():
    args = fixture()
    result = project(*args)
    encoded = json.dumps(result)
    assert "/private" not in encoded
    assert "inputs" not in result
    assert len(result["execution"]) == 8
    assert set(result["execution"][0]) == {"id", *METRICS}
    changed = copy.deepcopy(args)
    changed[0][0]["arm"] = "unreviewed"
    with pytest.raises(ValueError, match="approved"):
        project(*changed)
    args[0][0]["net_annual_return"] = "nan"
    with pytest.raises(ValueError, match="nonfinite"):
        project(*args)


def test_published_payload_preserves_limits_and_has_no_private_locators():
    data = json.loads(Path("web/public/data/microcap_followup_review.json").read_text())
    text = json.dumps(data)
    assert "/home/" not in text
    assert "symbol" not in text
    assert data["sample"]["raw_share_readiness"] is False
    assert data["action_coverage"]["90"]["unqueried_names"] == 114
    arms = {row["id"]: row for row in data["execution"]}
    assert arms["prior20_budget"]["fills_over_5pct_realized_amount"] == 688
    assert arms["prior20_budget_realized_guard"]["fills_over_5pct_realized_amount"] == 0
    assert data["history"]["original_runtime_recovered"] is False
