"""Project reviewed backfill aggregates; exclude private event and source locators."""
import argparse
import hashlib
import json
from pathlib import Path


EVENT_FIELDS = {'end_date', 'cash_div', 'cash_div_tax', 'stk_div', 'stk_bo_rate',
                'stk_co_rate', 'record_date', 'pay_date', 'div_listdate', 'imp_ann_date'}

def project(summary):
    if summary['status'] != 'completed':
        raise ValueError('completed audit required')
    result = {'schema_version': 1, 'reviewed_on': '2026-10-17',
              'independent_event_completeness': False, 'raw_share_ready': False, 'plans': {}}
    for minimum in ('45', '90'):
        coverage = summary['coverage'][minimum]
        events = summary['event_resolution'][minimum]
        for histogram in ('conflict_fields', 'missing_fields'):
            if set(events[histogram]) - EVENT_FIELDS:
                raise ValueError('unreviewed event field')
        if coverage['unqueried_names'] or coverage['unqueried_stock_months']:
            raise ValueError('backfill query coverage is still incomplete')
        result['plans'][minimum] = {
            key: coverage[key] for key in ('names', 'stock_months', 'queried_names', 'unqueried_names', 'unqueried_stock_months')}
        result['plans'][minimum]['events'] = {
            key: events[key] for key in ('implemented_rows', 'ready_events', 'equivalent_versions_collapsed', 'missing_ex_date_rows', 'blocked_event_count', 'conflict_fields', 'missing_fields')}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    payload = project(json.loads(args.summary.read_text()))
    payload['source_sha256'] = hashlib.sha256(args.summary.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
