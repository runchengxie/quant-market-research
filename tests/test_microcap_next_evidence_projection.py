import copy
import json
from pathlib import Path

import pytest

from scripts.review_microcap_next_evidence import project_readiness


def readiness():
    return copy.deepcopy(json.loads(Path('web/public/data/microcap_next_evidence_review.json').read_text())['readiness'])


def test_readiness_projection_preserves_pending_state_and_drops_private_fields():
    source = readiness()
    source.update(private_path='/private/source', signal={'ticker': 'PRIVATE'}, limitation='/private')
    result = project_readiness(source)
    assert result['admitted'] is False
    assert result['issue_count'] == 7
    assert result['new_cohort_completed_windows'] == 0
    assert '/private' not in str(result)
    assert 'PRIVATE' not in str(result)


@pytest.mark.parametrize('field,value', [
    ('status', 'ready'), ('admitted', True), ('new_cohort_completed_windows', 1),
    ('formation', '2026-11-30'), ('issue_categories', ['PRIVATE']),
])
def test_changed_prospective_state_requires_new_review(field, value):
    source = readiness()
    source[field] = value
    with pytest.raises(ValueError, match='review required'):
        project_readiness(source)


def events():
    return copy.deepcopy(json.loads(Path('web/public/data/microcap_next_evidence_review.json').read_text())['events'])


def test_event_projection_excludes_rows_and_preserves_unchanged_owner_blockers():
    from scripts.review_microcap_next_evidence import project_events
    source = events()
    source['schema_version'] = 'microcap-event-adjudication.v1'
    source.update(private_path='/private/source', cases=[{'ticker': 'PRIVATE'}])
    result = project_events(source)
    assert result['plan_blockers'] == {'45': 83, '90': 82}
    assert result['owner_resolver_recomputed'] is False
    assert result['raw_share_ready'] is False
    assert '/private' not in str(result)
    assert 'PRIVATE' not in str(result)
    source['dated_unresolved'] -= 1
    with pytest.raises(ValueError, match='reconcile'):
        project_events(source)


def test_case_projection_drops_unreviewed_fields_and_keeps_primary_evidence_binding():
    from scripts.review_microcap_next_evidence import project_cases
    public = json.loads(Path('web/public/data/microcap_next_evidence_review.json').read_text())['cases']
    cases, primary = [], []
    for row in copy.deepcopy(public):
        evidence = {key: row[key] for key in ('source_url', 'source_pdf_sha256', 'stock_per_share')}
        evidence.update({key: value.replace('-', '') if value else None for key, value in row['dates'].items()})
        for key in ('cash_per_share', 'holder_rates', 'reference_price_deduction'):
            if key in row:
                evidence[key] = row[key]
        evidence.update(symbol='PRIVATE', source_pdf_path='/private/source', explanation='PRIVATE')
        primary.append(evidence)
        raw = {key: row[key] for key in ('case', 'assumed_record_shares', 'opening_cash')}
        raw['evidence'] = evidence
        for key in ('snapshots', 'snapshots_by_assumed_holder_class', 'exdate_pre_settlement'):
            if key in row:
                raw[key] = row[key]
        snapshots = raw.get('snapshots', [])
        for points in raw.get('snapshots_by_assumed_holder_class', {}).values():
            snapshots += points
        for point in snapshots:
            point['date'] = point['date'].replace('-', '')
            point['ticker'] = 'PRIVATE'
        raw['private_path'] = '/private'
        cases.append(raw)
    result = project_cases(cases, primary)
    assert len(result) == 4
    encoded = json.dumps(result)
    assert 'PRIVATE' not in encoded
    assert '/private' not in encoded
    assert 'symbol' not in encoded
    assert 'source_pdf_path' not in encoded
    cases[0]['snapshots'][0]['executable_sellable_shares'] = 1000
    with pytest.raises(ValueError, match='review required'):
        project_cases(cases, primary)


@pytest.mark.parametrize('value', [1.23, True, 'NaN', '1e3', '-1', '/private'])
def test_case_numbers_reject_lossy_or_non_decimal_inputs(value):
    from scripts.review_microcap_next_evidence import public_number
    with pytest.raises(ValueError, match='invalid case number'):
        public_number(value)


@pytest.mark.parametrize('value', ['20241301', '20240230', '202411', '2024-01-01', True])
def test_case_dates_require_eight_digits_and_a_real_calendar_date(value):
    from scripts.review_microcap_next_evidence import public_date
    with pytest.raises(ValueError):
        public_date(value)


def test_calendar_projection_drops_private_paths_and_requires_reviewed_schedule():
    from scripts.review_microcap_next_evidence import project_calendar
    public = json.loads(Path('web/public/data/microcap_next_evidence_review.json').read_text())
    source = copy.deepcopy(public['calendar'])
    source['private_path'] = '/private'
    for item in source['sources']:
        item['path'] = '/private/source'
    result = project_calendar(source)
    assert result['civil_days'] == 61
    assert result['vendor_calendar_mismatches'] == 0
    assert '/private' not in json.dumps(result)
    assert public['initial_readiness']['issue_count'] == 8
    assert public['readiness']['issue_count'] == 7
    assert project_readiness(public['initial_readiness'], initial=True)['issue_count'] == 8
    source['november_open_sessions'] = 22
    with pytest.raises(ValueError, match='review required'):
        project_calendar(source)
