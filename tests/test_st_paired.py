import pandas as pd
import pytest

from market_research.st_paired import classify_status, pair_period


def sample():
    return pd.DataFrame([
        dict(ts_code=s, trade_date='20240131', total_mv=i+1, amount=100.,
             adj_close=10., is_suspended=False, is_st=st, st_available_from='20200101',
             list_date='20000101', delist_date=None, status='st' if st else 'non_st',
             delisting_period=False)
        for i, (s, st) in enumerate([('A', True), ('B', False), ('C', False)])])


def prices():
    return pd.DataFrame([
        dict(ts_code=s, trade_date=day, adj_close=p, amount=100., is_suspended=False)
        for s, end in [('A', 12.), ('B', 11.), ('C', 9.)]
        for day, p in [('20240201', 10.), ('20240301', end)]])


def test_only_st_eligibility_changes_and_weights_stay_fixed():
    record, audit = pair_period(sample(), prices(), n=2, execution='20240201', endpoint='20240301')
    assert record['complete_pair']
    assert record['common_names'] == 1
    assert record['include_st_count'] == 1
    assert record['difference'] == pytest.approx(.15)
    assert audit.weight.eq(.5).all()


def test_missing_endpoint_invalidates_both_without_replacement():
    p = prices().loc[lambda r: ~(r.ts_code.eq('A') & r.trade_date.eq('20240301'))]
    record, audit = pair_period(sample(), p, n=2, execution='20240201', endpoint='20240301')
    assert not record['complete_pair']
    assert record['include_st_return'] is record['exclude_st_return'] is None
    assert set(audit.loc[audit.arm.eq('include_st'), 'ts_code']) == {'A', 'B'}
    assert audit.loc[audit.ts_code.eq('A'), 'forward_return'].isna().all()


def test_eventual_delisting_preserved_and_in_window_terminal_unresolved():
    f = sample()
    f.loc[f.ts_code.eq('A'), 'delist_date'] = '20240215'
    record, audit = pair_period(f, prices(), n=2, execution='20240201', endpoint='20240301')
    assert 'A' in set(audit.ts_code)
    assert record['terminal_selected_rows'] == 1
    assert not record['complete_pair']


def test_unknown_excluded_symmetrically():
    f = sample()
    f.loc[f.ts_code.eq('A'), 'status'] = 'unknown'
    record, audit = pair_period(f, prices(), n=2, execution='20240201', endpoint='20240301')
    assert record['difference'] == 0
    assert 'A' not in set(audit.ts_code)


def test_name_announcement_and_positive_availability_boundaries():
    f = sample()
    names = pd.DataFrame([
        dict(ts_code=s, name=name, start_date='20200101', end_date=None,
             ann_date=ann, change_reason='other')
        for s, name, ann in [('A', '*ST A', '20200101'), ('B', 'B', '20240131'), ('C', 'ST C', '20200101')]])
    f.loc[f.ts_code.eq('A'), 'st_available_from'] = '20240201'
    out = classify_status(f, names).set_index('ts_code')
    assert out.loc['A', 'status'] == 'unknown'  # announcement valid, availability late
    assert out.loc['B', 'status'] == 'unknown'  # same-day announcement
    assert out.loc['C', 'status'] == 'unknown'  # daily state/name conflict
    f.loc[f.ts_code.eq('A'), 'st_available_from'] = '20240131'
    assert classify_status(f, names).set_index('ts_code').loc['A', 'status'] == 'st'


def test_insufficient_known_names_never_renormalized():
    f = sample().iloc[:1]
    record, audit = pair_period(f, prices(), n=2, execution='20240201', endpoint='20240301')
    assert not record['complete_pair']
    assert record['difference'] is None
    assert audit.weight.eq(.5).all()


def test_absent_or_ambiguous_name_is_unknown():
    f = sample()
    names = pd.DataFrame([
        dict(ts_code='A', name=name, start_date='20200101', end_date=None,
             ann_date='20191231', change_reason='other') for name in ['ST A', 'A']])
    out = classify_status(f, names)
    assert out.status.eq('unknown').all()
