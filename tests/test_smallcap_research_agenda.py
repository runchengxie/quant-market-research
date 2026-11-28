import copy
import json
from pathlib import Path

import pytest

from market_research.research_agenda import validate_agenda

ROOT = Path(__file__).parents[1]


def agenda():
    return json.loads((ROOT / 'studies/smallcap_investability/task-registry.json').read_text())


def test_all_thirty_tasks_are_owned_bilingual_and_dependency_checked():
    data = agenda()
    assert validate_agenda(data) is True
    assert len(data['tasks']) == 30
    assert {t['priority'] for t in data['tasks']} == {'P0', 'P1', 'P2', 'P3'}
    assert {t['workstream'] for t in data['tasks']} == {
        'data', 'account', 'factors', 'portfolio', 'execution', 'validation', 'publication'}


def test_duplicate_and_missing_dependencies_fail():
    data = agenda()
    data['tasks'].append(copy.deepcopy(data['tasks'][0]))
    with pytest.raises(ValueError, match='duplicate'):
        validate_agenda(data)
    data = agenda()
    data['tasks'][0]['dependsOn'] = ['SC-999']
    with pytest.raises(ValueError, match='missing dependency'):
        validate_agenda(data)


def test_cycles_and_unsupported_completion_fail():
    data = agenda()
    data['tasks'][0]['dependsOn'] = ['SC-002']
    with pytest.raises(ValueError, match='cycle'):
        validate_agenda(data)
    data = agenda()
    data['tasks'][1]['status'] = 'done'
    data['tasks'][1]['evidence'] = []
    with pytest.raises(ValueError, match='evidence'):
        validate_agenda(data)
    data = agenda()
    data['tasks'][8]['status'] = 'ready'
    data['tasks'][8]['gap'] = None
    with pytest.raises(ValueError, match='unfinished prerequisite'):
        validate_agenda(data)


def test_waiting_gate_and_localization_cannot_disappear():
    data = agenda()
    data['tasks'][2]['gap'] = None
    with pytest.raises(ValueError, match='gap'):
        validate_agenda(data)
    data = agenda()
    data['tasks'][0]['acceptance']['zh'] = ''
    with pytest.raises(ValueError, match='bilingual'):
        validate_agenda(data)


def test_evidence_links_have_retained_public_source_files():
    prefix = 'https://github.com/runchengxie/quant-market-research/blob/main/'
    for task in agenda()['tasks']:
        for url in task['evidence']:
            if url.startswith(prefix):
                assert (ROOT / url.removeprefix(prefix)).is_file(), url


def test_reviewed_progress_is_target_only_and_retains_transition_denominators():
    review = json.loads((ROOT / 'studies/smallcap_investability/target-support-reviewed.json').read_text())
    assert review['returns_computed'] is False
    assert review['execution_simulated'] is False
    assert review['pit_certified'] is False
    assert review['formations']['supported'] + review['formations']['unsupported'] == review['formations']['input']
    assert len(review['rows']) == 6
    for row in review['rows']:
        assert row['target_change_half_l1_valid_dates'] == 136
        assert row['selected_count_valid_dates'] == 137
    for lang in ['', '.zh-CN']:
        text = (ROOT / f'studies/smallcap_investability/README{lang}.md').read_text()
        for task in agenda()['tasks']:
            assert task['id'] in text
            assert task['acceptance']['zh' if lang else 'en'] in text
