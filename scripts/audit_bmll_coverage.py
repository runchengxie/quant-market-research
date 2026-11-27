"""Prepare or summarize a bounded private coverage check of the prior candidate pool."""
import argparse
import hashlib
import json
from pathlib import Path

from market_research.bmll_coverage import coverage_sql, audit_coverage
from market_research.bmll_pilot import decode_statement

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate-report', required=True, type=Path)
p.add_argument('--dates', nargs='+', required=True)
p.add_argument('--output', required=True, type=Path)
p.add_argument('--response', type=Path)
p.add_argument('--executed-sql', type=Path, help='Retained SQL paired with the response')
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
if a.output.resolve().is_relative_to(repo) or a.output.exists():
    raise ValueError('Use a new output file outside the repository')
report = json.loads(a.candidate_report.read_text())
symbols = sorted(r['symbol'] for r in report['candidate_pool'])
sql = coverage_sql(symbols, a.dates)
a.output.parent.mkdir(parents=True, exist_ok=True)
if a.response is None:
    a.output.write_text(sql)
else:
    if a.executed_sql is None or a.executed_sql.read_text() != sql:
        raise ValueError('Retained executed SQL must match this candidate/date request')
    result = audit_coverage(decode_statement(json.loads(a.response.read_text())), symbols, a.dates)
    result['input_hashes'] = {key: hashlib.sha256(path.read_bytes()).hexdigest()
                              for key, path in [('candidates', a.candidate_report), ('response', a.response)]}
    result['requested_sql_sha256'] = hashlib.sha256(sql.encode()).hexdigest()
    result['by_stratum'] = []
    groups = {(r['cap_group'], r['adv_group']) for r in report['candidate_pool']}
    for day in a.dates:
        for cap, adv in sorted(groups):
            members = {r['symbol'] for r in report['candidate_pool']
                       if (r['cap_group'], r['adv_group']) == (cap, adv)}
            subset = [r for r in result['observations'] if r['reference_date'] == day and r['ticker'] in members]
            result['by_stratum'].append(dict(date=day, cap_group=cap, adv_group=adv,
                candidates=len(subset), quotes_observed=sum(r['status'] == 'quotes_observed' for r in subset)))
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps(result['by_date']))
