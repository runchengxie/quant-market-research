import pytest
from market_research.bmll_coverage import coverage_sql, audit_coverage


def test_query_bounds_and_historical_identity_are_explicit():
    sql = coverage_sql(['A', 'B'], ['2025-03-18'])
    assert 'LEFT JOIN ref' in sql and 'r.alive_records=1' in sql
    assert 'America/New_York' in sql
    for symbols, dates in [(['A', 'A'], ['2025-03-18']), (["A'"], ['2025-03-18']),
                           (['A'], ['invalid']), (['A'], []),
                           ([f'A{i}' for i in range(501)], ['2025-03-18'])]:
        with pytest.raises(ValueError):
            coverage_sql(symbols, dates)


def test_nonmatches_and_ambiguity_remain_in_denominator():
    rows = [dict(ticker=s, reference_date='2025-03-18', reference_records=r,
                 alive_records=a, quote_events=q, valid_price_events=q)
            for s, r, a, q in [('A', 0, 0, 0), ('B', 1, 0, 0), ('C', 2, 2, 0),
                               ('D', 1, 1, 0), ('E', 1, 1, 3)]]
    result = audit_coverage(rows, list('ABCDE'), ['2025-03-18'])
    assert len(result['by_date']['2025-03-18']) == 5
    assert sum(result['by_date']['2025-03-18'].values()) == 5
    with pytest.raises(ValueError, match='grid'):
        audit_coverage(rows[:-1], list('ABCDE'), ['2025-03-18'])
    rows[0]['quote_events'] = rows[0]['valid_price_events'] = 1
    with pytest.raises(ValueError, match='unresolved'):
        audit_coverage(rows, list('ABCDE'), ['2025-03-18'])
