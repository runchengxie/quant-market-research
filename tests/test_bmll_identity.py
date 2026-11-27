import pytest
from market_research.bmll_identity import active_flag, audit_identities


def row(day, listing=1, active='true'):
    return dict(ticker='A', reference_date=day, listing_id=listing, instrument_id=listing,
                isin=f'ID{listing}', mic='@SIP', is_alive=active)


def test_transport_booleans_and_ambiguity():
    assert active_flag('false') is False
    with pytest.raises(ValueError):
        active_flag('False')
    result = audit_identities([row('2025-01-01'), row('2025-01-01', 2)], ['A', 'B'], ['2025-01-01'])
    assert [r['status'] for r in result['observations']] == ['ambiguous_active', 'missing_reference']
    assert result['transitions'] == []


def test_changed_identity_is_not_filled_across_missing_snapshot():
    dates = ['2025-01-01', '2025-01-02', '2025-01-03']
    rows = [row(dates[0]), row(dates[2], 2)]
    assert not audit_identities(rows, ['A'], dates)['transitions']
    assert len(audit_identities(rows, ['A'], [dates[0], dates[2]])['transitions']) == 1
    with pytest.raises(ValueError, match='Duplicate'):
        audit_identities(rows + rows, ['A'], dates)


def test_inactive_records_do_not_become_successors():
    result = audit_identities([row('2025-01-01', active='false')], ['A'], ['2025-01-01'])
    assert result['observations'][0]['identity'] is None
    assert result['observations'][0]['status'] == 'inactive_only'
