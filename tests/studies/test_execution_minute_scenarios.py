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


def comparison(role='baseline'):
    return {'risk_comparison': {'role': role, 'source_packet_path': '/external/packet.json',
                               'source_packet_sha256': 'a' * 64,
                               'authorized_scenarios': ['fees_1m', 'fees_10m']}}


@pytest.mark.parametrize('names', [None, [], ['weekly_10m'], ['buffer_10m'],
                                  ['gross_1m'], ['fees_1m', 'fees_100m']])
def test_risk_comparison_requires_explicit_authorized_matrix(names):
    with pytest.raises(ValueError, match='risk comparison'):
        runner.select_prepared_scenarios(comparison(), names)


def test_risk_comparison_selects_only_explicit_pilots_and_keeps_default():
    assert len(runner.select_prepared_scenarios({}, None)) == 9
    assert [row[0] for row in runner.select_prepared_scenarios(comparison(), ['fees_10m'])] == [
        'fees_10m']
    proposal = runner.build_proposal(comparison(), [
        {'scenario': 'fees_1m'}, {'scenario': 'fees_10m'}], {})
    assert proposal['complete'] is False
    assert proposal['expected_scenarios'] == 9
    assert proposal['published'] is False
    assert proposal['requested_pilots_complete'] is True
    assert proposal['authorized_pilot_count'] == 2
    with pytest.raises(ValueError, match='risk comparison'):
        runner.build_proposal(comparison(), [{'scenario': 'weekly_10m'}], {})


@pytest.mark.parametrize('change', [{'role': 'other'}, {'authorized_scenarios': ['weekly_10m']},
                                  {'source_packet_sha256': None}, {'source_packet_path': ''}])
def test_risk_comparison_rejects_invalid_receipt(change):
    inputs = comparison()
    inputs['risk_comparison'].update(change)
    with pytest.raises(ValueError, match='risk comparison'):
        runner.select_prepared_scenarios(inputs, ['fees_1m'])


def risk_packet(tmp_path):
    import hashlib
    import json

    from market_research.studies.ashare_execution_costs.risk_sources import RULE
    from market_research.studies.ashare_execution_costs.risk_sources import load_risk_events
    from market_research.studies.ashare_execution_costs.risk_guards import build_risk_targets
    import inspect

    primary = tmp_path / 'notice.pdf'
    primary.write_bytes(b'bound issuer PDF fixture')
    symbols = ['600321.SH', '002621.SZ', '000982.SZ', '600836.SH']
    events = [dict(symbol=symbol, event_id=f'confirmed:{symbol}',
                   event_type='confirmed_termination', available_time='2024-07-08T09:00:00+08:00',
                   source_refs=['primary']) for symbol in symbols]
    facts = tmp_path / 'facts.json'
    facts.write_text(json.dumps({'schema': 'execution-risk-event-facts.v1', 'events': [
        dict(event, primary_publication_date='2024-07-05', primary_file_ref='primary',
             publication_intraday_timestamp=None, availability_rule=RULE) for event in events]}))
    refs = [dict(name=name, path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            for name, path in [('primary', primary), ('facts', facts)]]
    packet = tmp_path / 'packet.json'
    packet.write_text(json.dumps(dict(schema='execution-risk-events-source.v1', source_refs=refs,
                                     facts_ref=refs[1], events=events, source_flags=['subset_only'],
                                     coverage=dict(scope='selected_baseline_109_2024_delisted',
                                                   complete_for_scope=True,
                                                   all_market_announcement_coverage=False,
                                                   symbols=symbols))))
    inputs = comparison()
    inputs.update(start='20240705', end='20240709', sessions=3)
    inputs['risk_comparison'].update(source_packet_path=str(packet),
                                    source_packet_sha256=runner.sha(packet))
    inputs['risk_comparison']['lineage'] = {'implementation_sha256': {
        name: runner.sha(Path(inspect.getfile(function))) for name, function in [
            ('risk_sources', load_risk_events), ('risk_targets', build_risk_targets),
            ('baseline_targets', runner.build_targets)]}}
    import pandas as pd
    bars = pd.DataFrame({'time': pd.to_datetime(['2024-07-05 09:32', '2024-07-08 09:32',
                                                '2024-07-09 09:32']).tz_localize('Asia/Shanghai')})
    return inputs, bars, primary


def test_risk_comparison_both_arms_use_same_four_source_bound_nontrading_events(tmp_path):
    inputs, bars, _ = risk_packet(tmp_path)
    baseline_rows, baseline_policy = runner.build_risk_comparison_valuation(inputs, bars)
    inputs['risk_comparison']['role'] = 'risk'
    risk_rows, risk_policy = runner.build_risk_comparison_valuation(inputs, bars)
    assert risk_rows == baseline_rows
    assert risk_policy == baseline_policy
    assert len(risk_rows) == 4
    assert {row['value_per_share'] for row in risk_rows} == {0.}
    assert next(row for row in risk_rows if row['symbol'] == '600836.SH')[
        'effective_time'] == '2024-07-08T09:00:00+08:00'
    assert risk_policy['mode'] == 'termination_decision_full_impairment'
    assert risk_policy['shares_retained'] is True
    assert risk_policy['cash_disposal'] is False
    assert risk_policy['hypothesis'] is True


def test_risk_comparison_revalidates_primary_packet_and_sessions(tmp_path):
    inputs, bars, primary = risk_packet(tmp_path)
    with pytest.raises(ValueError, match='prepared sessions'):
        runner.build_risk_comparison_valuation(inputs, bars.iloc[:2])
    primary.write_bytes(b'tampered')
    with pytest.raises(ValueError, match='source hash mismatch'):
        runner.build_risk_comparison_valuation(inputs, bars)
    inputs['risk_comparison']['source_packet_sha256'] = 'b' * 64
    with pytest.raises(ValueError, match='packet hash mismatch'):
        runner.build_risk_comparison_valuation(inputs, bars)


def test_risk_comparison_binds_target_preparation_implementation(tmp_path):
    inputs, bars, _ = risk_packet(tmp_path)
    inputs['risk_comparison']['lineage']['implementation_sha256']['risk_targets'] = '0' * 64
    with pytest.raises(ValueError, match='preparation implementation differs'):
        runner.build_risk_comparison_valuation(inputs, bars)
