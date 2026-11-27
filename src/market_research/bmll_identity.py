"""Describe dated reference identities without inferring corporate-action returns."""
from collections import defaultdict


def active_flag(value):
    """Statement API BOOLEAN values may arrive as strings."""
    if value is True or value == 'true':
        return True
    if value is False or value == 'false':
        return False
    raise ValueError('Unrecognised reference activity flag')


def audit_identities(rows, symbols, dates):
    if not symbols or not dates or len(set(symbols)) != len(symbols) or len(set(dates)) != len(dates):
        raise ValueError('Require unique, nonempty symbols and dates')
    grouped = defaultdict(list)
    seen = set()
    for row in rows:
        key = (row['ticker'], row['reference_date'])
        if key[0] not in symbols or key[1] not in dates or row['mic'] != '@SIP':
            raise ValueError('Unexpected reference scope')
        identity = (*key, row['listing_id'])
        if identity in seen:
            raise ValueError('Duplicate listing within symbol/date')
        seen.add(identity)
        active_flag(row['is_alive'])
        grouped[key].append(row)
    observations, transitions = [], []
    for symbol in sorted(symbols):
        previous = None
        for day in sorted(dates):
            records = grouped[symbol, day]
            alive = [r for r in records if active_flag(r['is_alive'])]
            status = ('missing_reference' if not records else 'inactive_only' if not alive
                      else 'ambiguous_active' if len(alive) > 1 else 'unique_active')
            current = alive[0] if len(alive) == 1 else None
            identity = {k: current[k] for k in ['listing_id', 'instrument_id', 'isin']} if current else None
            observations.append(dict(ticker=symbol, date=day, status=status,
                                     reference_records=len(records), identity=identity))
            # Only adjacent sampled dates. No forward-fill across a failed match.
            if previous and current:
                changed = [k for k in identity if identity[k] != previous['identity'][k]]
                if changed:
                    transitions.append(dict(ticker=symbol, start=previous['date'], end=day,
                                            changed_fields=changed, status='requires_event_reconciliation'))
            previous = dict(date=day, identity=identity) if current else None
    return dict(observations=observations, transitions=transitions,
                scope='Sampled snapshots only; changes are not effective dates, successor mappings, split factors or realised returns.')
