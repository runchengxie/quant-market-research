"""Run private follow-up diagnostics from retained inputs. No new data service required."""
import argparse
import hashlib
import json
from pathlib import Path

import duckdb

from market_research.bmll_pilot import decode_statement, cap_bucket
from market_research.smallcap_followup import quote_diagnostics, select_buffered, replacement_fraction

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--pilot', type=Path, required=True)
p.add_argument('--features', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
if a.output.resolve().is_relative_to(repo) or a.output.exists():
    raise ValueError('Use a new output directory outside the repository')
config = json.loads((repo / 'configs/bmll/pilot.json').read_text())
quotes = decode_statement(json.loads((a.pilot / 'quotes.json').read_text()))
trades = decode_statement(json.loads((a.pilot / 'trades.json').read_text()))
result = quote_diagnostics(quotes, set(config['baseline_dates']), set(config['comparison_dates']))
result['direction_coverage'] = []
for symbol in config['symbols']:
    rows = [r for r in trades if r['ticker'] == symbol]
    denominator = sum(r['valid_quote_events'] for r in rows)
    result['direction_coverage'].append(dict(symbol=symbol, valid_events=denominator,
        unknown_fraction=sum(r['unknown_direction_events'] for r in rows) / denominator
        if denominator else None))
con = duckdb.connect()
# Read only selected lagged feature dates. Eligibility and release-time provenance remain provisional.
dates = ['2025-03-18', '2025-04-01', '2025-05-01', '2025-06-02', '2025-07-01',
         '2025-08-01', '2025-09-02']
features = con.execute('SELECT symbol,date,market_cap_usd,adv20_usd FROM read_parquet(?) '
    'WHERE date IN (SELECT unnest(?::DATE[])) AND eligible '
    'AND isfinite(market_cap_usd) AND market_cap_usd>0 '
    'AND isfinite(adv20_usd) AND adv20_usd>0 ORDER BY date,market_cap_usd,symbol',
    [str(a.features), dates]).fetchdf()
if features.duplicated(['date', 'symbol']).any():
    raise ValueError('Feature identity is not unique')
formation = features[features.date.astype(str) == dates[0]].copy()
formation['cap_group'] = formation.market_cap_usd.map(cap_bucket)
formation['adv_group'] = formation.adv20_usd.map(lambda v: 'under_100k' if v < 1e5
                                               else '100k_1m' if v < 1e6 else 'over_1m')
# Deterministic hash order prevents alphabetic selection. This is not a probability sample.
formation['selection_order'] = formation.symbol.map(
    lambda s: hashlib.sha256(('smallcap-followup-v1:' + s).encode()).hexdigest())
candidates = formation[formation.market_cap_usd < 1e9].sort_values('selection_order').groupby(
    ['cap_group', 'adv_group']).head(4).drop(columns='selection_order')
candidates['date'] = candidates.date.astype(str)
result['candidate_pool'] = candidates.to_dict('records')
result['formation_counts'] = formation.groupby(['cap_group', 'adv_group']).size().reset_index(
    name='names').to_dict('records')
result['membership_experiment'] = []
for schedule, selected_dates in [('monthly', dates[1:]), ('quarterly', [dates[1], dates[4]])]:
    for exit_rank in [100, 150]:
        held = []
        for day in selected_dates:
            ranked = features[features.date.astype(str) == day].symbol.tolist()
            target = select_buffered(ranked, held, 100, exit_rank)
            result['membership_experiment'].append(dict(schedule=schedule, exit_rank=exit_rank,
                date=day, eligible_names=len(ranked), target_names=target,
                replaced_fraction=replacement_fraction(held, target)))
            held = target
result['scope'] = {'formation_date': dates[0], 'candidates': 'Provisional identities, not a certified historical equity universe',
    'membership': 'Smallest 100 positive-cap and positive-ADV eligible feature rows. Target membership only, no returns, price drift or trades.',
    'snapshot': 'Retrospective feature snapshot, original filing-time availability unverified',
    'cost': 'No inference of realised cost or executable capacity',
    'quarterly': 'Only one post-formation quarterly observation; no frequency ranking is supported'}
result['source_hashes'] = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name,path in
    [('quotes',a.pilot/'quotes.json'),('trades',a.pilot/'trades.json'),('features',a.features)]}
a.output.mkdir(parents=True)
(a.output/'followup.json').write_text(json.dumps(result, indent=2, allow_nan=False))
print(json.dumps({'candidates':len(candidates),'paired_securities':len(result['paired']),
                  'membership_observations':len(result['membership_experiment'])}))
