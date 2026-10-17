import pytest
from scripts.review_microcap_action_backfill import project


def test_backfill_projection_drops_private_events_and_preserves_blockers():
    coverage = dict(names=597, stock_months=5400, queried_names=597, unqueried_names=0, unqueried_stock_months=0, private_path='/private')
    events = dict(implemented_rows=5, ready_events=2, equivalent_versions_collapsed=1, missing_ex_date_rows=1, blocked_event_count=1, conflict_fields={'record_date': 1}, missing_fields={}, blocked_events=[{'ts_code': 'PRIVATE'}])
    summary = dict(status='completed', coverage={key: coverage for key in ('45','90')}, event_resolution={key: events for key in ('45','90')})
    payload = project(summary)
    assert '/private' not in str(payload)
    assert 'PRIVATE' not in str(payload)
    assert payload['plans']['90']['events']['blocked_event_count'] == 1
    assert payload['raw_share_ready'] is False
    coverage['unqueried_names'] = 1
    with pytest.raises(ValueError, match='incomplete'):
        project(summary)
