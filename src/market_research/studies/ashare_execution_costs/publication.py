"""Export reviewed L2 aggregates through an explicit public-data allowlist."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re

QUANTILES = ('count', 'p50', 'p90', 'p95')
AUDIT = ('day', 'rows_read', 'sampled_securities', 'sampled_snapshots', 'valid_books',
         'excluded_books', 'one_sided', 'crossed_or_locked', 'malformed', 'invalid_clock',
         'day_mismatch', 'outside_continuous_session', 'null_clock_or_identity')
METRICS = ('spread_bp', 'bid_depth_cny', 'ask_depth_cny')


def numeric(value):
    if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                              or not math.isfinite(value)):
        raise ValueError('aggregate values must be finite numbers or null')
    return value


def quantiles(value):
    return {key: numeric(value[key]) for key in QUANTILES if key in value}


def aggregate(value):
    out = {key: numeric(value[key]) for key in ('snapshots', 'security_days') if key in value}
    for key in METRICS:
        if key in value:
            out[key] = quantiles(value[key])
    if 'cost_surface' in value:
        rows = []
        for row in value['cost_surface']:
            if row['side'] not in ('buy', 'sell') or row['reference_notional_cny'] not in (
                    10000, 100000, 1000000, 10000000):
                raise ValueError('unexpected side or reference notional')
            rows.append({'side':row['side'], 'reference_notional_cny':row['reference_notional_cny'],
                         'full_coverage_rate':numeric(row['full_coverage_rate']),
                         'coverage_fraction':quantiles(row['coverage_fraction']),
                         'full_order_cost_bp':quantiles(row['full_order_cost_bp'])})
        out['cost_surface'] = rows
    if 'common_full_subset' in value:
        out['common_full_subset'] = aggregate(value['common_full_subset'])
    return out


def public_pilot(private: dict, *, confirmed_on: str) -> dict:
    date.fromisoformat(confirmed_on)
    if private.get('study_id') != 'ashare_execution_costs':
        raise ValueError('unexpected study identity')
    out = {'schema_version':'ashare_execution_costs.public_pilot.v1',
           'study_id':'ashare_execution_costs', 'evidence':'descriptive_static_book_pilot',
           'permission':{'status':'confirmed_by_owner','confirmed_on':confirmed_on,
                         'scope':'aggregate_derived_statistics'},
           'measurement_code_sha256':private.get('measurement_code_sha256'),
           'source_inputs':[{key:entry[key] for key in ('day','sha256','bytes')}
                            for entry in private.get('inputs', [])],
           'audit':[{key:numeric(row[key]) for key in AUDIT if key in row}
                    for row in private.get('audit',[])],
           'pooled':aggregate(private.get('pooled',{})),
           'by_day':{key:aggregate(value) for key,value in private.get('by_day',{}).items()
                     if re.fullmatch(r'\d{8}',key)},
           'by_depth_group':{key:aggregate(value) for key,value in
                             private.get('by_depth_group',{}).items()
                             if key in ('shallow','middle','deep')},
           'definitions':{'price_unit':'CNY','quantity_unit':'share',
             'benchmark':'contemporaneous_midpoint',
             'reference_notional':'midpoint_times_target_shares_fractional_shares_allowed',
             'weights':'one_earliest_snapshot_per_selected_security_minute',
             'sampling':'Shanghai_Shenzhen_stocklike_prefixes_security_code_modulo_37_equals_zero',
             'uncovered_orders':'full_order_cost_missing_no_extrapolation',
             'depth_groups':'same_day_median_depth_terciles_not_lagged_signals',
             'uncertainty':'sample_quantiles_not_population_confidence_intervals',
             'fees_included':False,'dynamic_impact_calibrated':False,'actual_order_calibrated':False}}
    # Never copy private paths, schemas, source specs, identifiers or measured rows.
    encoded = json.dumps(out, allow_nan=False)
    if re.search(r'/home/|/mnt/|/Users/|SecuCode|TickTime|API_KEY=|TOKEN=',encoded):
        raise ValueError('public export contains a private marker')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary',type=Path,required=True)
    parser.add_argument('--confirmed-on',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    raw = args.summary.read_bytes()
    public = public_pilot(json.loads(raw),confirmed_on=args.confirmed_on)
    public['source_summary_sha256'] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(public,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
