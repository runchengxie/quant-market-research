"""Exploratory quote diagnostics and target membership, with no execution claims."""
from collections import defaultdict
from math import isfinite
from statistics import mean


def quote_diagnostics(rows, baseline, comparison):
    """Equal-window daily means; retain valid-time coverage alongside each estimate."""
    days = defaultdict(list)
    seen = set()
    for row in rows:
        key = (row['ticker'], row['trade_date'], row['label'])
        if key in seen:
            raise ValueError('Duplicate quote window')
        seen.add(key)
        if (abs(row['covered_seconds'] - 1800) > .001
                or not 0 < row['valid_seconds'] <= row['covered_seconds']
                or abs(row['bid_size_seconds'] - row['valid_seconds']) > .001
                or not 0 <= row['fresh60_seconds'] <= row['valid_seconds']):
            raise ValueError('Incomplete quote or quantity coverage')
        days[key[:2]].append(row)
    daily = []
    metrics = ['tw_spread_bps', 'fresh60_tw_spread_bps', 'tw_best_bid_dollars',
               'bid_covers_1000_fraction', 'bid_covers_10000_fraction']
    for (symbol, day), observations in sorted(days.items()):
        if {r['label'] for r in observations} != {'open', 'midday', 'close'}:
            raise ValueError('Missing intraday window')
        record = {'symbol': symbol, 'date': day}
        for metric in metrics:
            values = [r[metric] for r in observations]
            record[metric] = (mean(values) if all(v is not None and isfinite(v) for v in values)
                              else None)
        record['valid_fraction'] = sum(r['valid_seconds'] for r in observations) / 5400
        record['fresh_fraction'] = (sum(r['fresh60_seconds'] for r in observations)
                                    / sum(r['valid_seconds'] for r in observations))
        daily.append(record)
    comparisons = []
    for symbol in sorted({r['symbol'] for r in daily}):
        a = [r for r in daily if r['symbol'] == symbol and r['date'] in baseline]
        b = [r for r in daily if r['symbol'] == symbol and r['date'] in comparison]
        if len(a) != len(baseline) or len(b) != len(comparison):
            raise ValueError('Incomplete paired dates')
        out = {'symbol': symbol}
        for metric in metrics + ['fresh_fraction']:
            av = [r[metric] for r in a]
            bv = [r[metric] for r in b]
            out[metric] = {'baseline': mean(av) if None not in av else None,
                           'comparison': mean(bv) if None not in bv else None}
        comparisons.append(out)
    return {'daily': daily, 'paired': comparisons}


def select_buffered(ranked, previous, count, exit_rank):
    """Keep eligible previous names within exit rank, then fill by ascending size rank."""
    if len(ranked) != len(set(ranked)) or count <= 0 or exit_rank < count:
        raise ValueError('Invalid ranked universe or buffer')
    if len(ranked) < count:
        raise ValueError('Insufficient eligible names')
    retained = [s for s in ranked[:exit_rank] if s in previous][:count]
    return retained + [s for s in ranked if s not in retained][:count - len(retained)]


def replacement_fraction(previous, current):
    """Equal-weight target membership replacement; excludes price drift and executions."""
    if not current or len(set(current)) != len(current):
        raise ValueError('Empty or duplicate target')
    if not previous:
        return None  # Initial funding is not a rebalance observation.
    if len(previous) != len(current) or len(set(previous)) != len(previous):
        raise ValueError('Target size changed')
    return len(set(current) - set(previous)) / len(current)
