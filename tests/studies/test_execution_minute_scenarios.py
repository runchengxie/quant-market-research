import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "minute_runner", Path(__file__).parents[2] / "scripts/run_execution_cost_minute.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_selected_pilots_preserve_full_matrix_completion_gate():
    selected = runner.scenarios(["fees_1m", "fees_10m"])
    assert [row[0] for row in selected] == ["fees_1m", "fees_10m"]
    proposal = runner.build_proposal({}, [{"scenario": row[0]} for row in selected], {})
    assert proposal["complete"] is False
    assert proposal["expected_scenarios"] == 9
    assert runner.build_proposal({}, [{"scenario": row[0]} for row in runner.scenarios()], {})[
        "complete"
    ]


@pytest.mark.parametrize("names", [["unknown"], ["fees_1m", "fees_1m"], []])
def test_unknown_duplicate_or_empty_scenario_selection_rejects(names):
    with pytest.raises(ValueError):
        runner.scenarios(names)


def test_valuation_pilots_keep_hypothesis_visible_and_matrix_incomplete():
    policy = {"mode": "full_impairment", "hypothesis": True, "quote_verified": False}
    proposal = runner.build_proposal({}, [{"scenario": "fees_1m"}], {}, policy)
    assert proposal["valuation_policy"] == policy
    assert proposal["complete"] is False
    assert proposal["published"] is False
    assert "declared_nontrading_valuation_not_cash_disposal" in proposal["limits"]
