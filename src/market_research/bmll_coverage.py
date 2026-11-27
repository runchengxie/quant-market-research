"""Reference/quote availability checks for a fixed candidate cohort, not universe certification."""
from collections import Counter
from datetime import date
import re


def coverage_sql(symbols: list[str], dates: list[str]) -> str:
    if not symbols or len(symbols) != len(set(symbols)) or len(dates) != len(set(dates)) or not dates:
        raise ValueError('Use nonempty unique symbols and dates')
    if len(symbols) * len(dates) > 500:
        raise ValueError('Cohort exceeds the retained single-chunk row limit')
    if any(not re.fullmatch(r'[A-Za-z0-9.\-]+', s) for s in symbols):
        raise ValueError('Invalid symbol')
    for d in dates:
        date.fromisoformat(d)
    names = ','.join(f"('{s}')" for s in symbols)
    days = ','.join(f"(DATE '{d}')" for d in dates)
    return f"""WITH candidates(ticker) AS (VALUES {names}), days(reference_date) AS (VALUES {days}),
expected AS (SELECT * FROM candidates CROSS JOIN days),
ref AS (
 SELECT r.reference_date,r.ticker,count(*) reference_records,
 count_if(r.is_alive) alive_records,
 max(CASE WHEN r.is_alive THEN r.listing_id END) listing_id
 FROM bmll_data_feed.market_data.reference_prod r JOIN expected e
 ON r.reference_date=e.reference_date AND r.ticker=e.ticker WHERE r.mic='@SIP'
 GROUP BY r.reference_date,r.ticker
), observed AS (
 SELECT r.ticker,q.trade_date,count(*) quote_events,
 count_if(q.bid_price>0 AND q.ask_price>=q.bid_price) valid_price_events,
 min(from_utc_timestamp(q.event_timestamp,'America/New_York')) first_quote,
 max(from_utc_timestamp(q.event_timestamp,'America/New_York')) last_quote
 FROM bmll_data_feed.market_data.nbbo_prod q JOIN ref r
 ON r.reference_date=q.trade_date AND r.listing_id=q.bmll_object_id AND r.alive_records=1
 WHERE q.mic='@SIP'
 AND date_format(from_utc_timestamp(q.event_timestamp,'America/New_York'),'HH:mm:ss')>='09:30:00'
 AND date_format(from_utc_timestamp(q.event_timestamp,'America/New_York'),'HH:mm:ss')<'16:00:00'
 GROUP BY r.ticker,q.trade_date
)
SELECT e.ticker,e.reference_date,coalesce(r.reference_records,0) reference_records,
coalesce(r.alive_records,0) alive_records,r.listing_id,coalesce(o.quote_events,0) quote_events,
coalesce(o.valid_price_events,0) valid_price_events,o.first_quote,o.last_quote
FROM expected e LEFT JOIN ref r ON e.ticker=r.ticker AND e.reference_date=r.reference_date
LEFT JOIN observed o ON e.ticker=o.ticker AND e.reference_date=o.trade_date
ORDER BY e.reference_date,e.ticker
"""


def audit_coverage(rows, symbols, dates):
    """Preserve missing and ambiguous joins. An observed quote is not complete session coverage."""
    expected = {(s, d) for s in symbols for d in dates}
    keys = [(r['ticker'], r['reference_date']) for r in rows]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError('Coverage output differs from the expected cohort grid')
    observations = []
    for row in rows:
        ref, alive, quotes, valid = (row[k] for k in
                                    ['reference_records', 'alive_records', 'quote_events', 'valid_price_events'])
        if not 0 <= alive <= ref or not 0 <= valid <= quotes:
            raise ValueError('Inconsistent availability counts')
        if alive != 1 and quotes:
            raise ValueError('Quotes joined to an unresolved identity')
        status = ('no_reference' if ref == 0 else 'inactive_only' if alive == 0
                  else 'ambiguous_active_reference' if alive > 1 else 'no_session_quotes'
                  if quotes == 0 else 'quotes_observed')
        observations.append(dict(row, status=status))
    return {'observations': observations,
            'by_date': {day: dict(Counter(r['status'] for r in observations if r['reference_date'] == day))
                        for day in dates},
            'scope': 'Fixed retrospective cohort. Quote counts do not certify uninterrupted coverage, tradability, common-share eligibility or corporate-action continuity.'}
