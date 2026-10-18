"""Publish only reviewed aggregate exposure, account checks and register anchors."""

import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

PARTS = ('definite', 'possible', 'absent', 'unknown')
ARMS = ('owner_ideal_fee10', 'capacity_without_limits', 'capacity_with_limits',
        'prior20_budget_realized_guard')
MATERIALITY = ('owner_ideal_fee10', 'prior20_budget_realized_guard')
ENGINE = '15ec62b66e894395d694049eaaace931de4a1265'


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError('invalid count')
    return value


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError('invalid finite nonnegative value')
    return value


def clock(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('timezone required')
    return value


def partition(source, total):
    result = {key: count(source[key]) for key in PARTS}
    if sum(result.values()) != total:
        raise ValueError('event partition does not reconcile')
    return result


def project_exposure(source):
    total = count(source['unique_events'])
    if total != 94 or source['account_impact'] != (
            'nonidentifiable_without_raw_share_ledger_and_complete_action_terms'):
        raise ValueError('exposure scope changed; review required')
    result = {'unique_events': total, 'unknown_exdate_rows': count(source['unknown_exdate_rows']),
              'plans': {}, 'account_impact': source['account_impact'], 'materiality': {}}
    for plan in ('45', '90'):
        row = source['plans'][plan]
        projected = {'target': partition(row['target'], total), 'inventory': {}}
        if plan == '45':
            if row['inventory'] or row['inventory_status'] != 'not_retained':
                raise ValueError('minimum45 inventory changed; review required')
            projected['inventory_status'] = 'not_retained'
        else:
            if set(row['inventory']) != set(ARMS):
                raise ValueError('inventory arms changed; review required')
            projected['inventory'] = {arm: partition(row['inventory'][arm], total) for arm in ARMS}
        result['plans'][plan] = projected
    for arm in MATERIALITY:
        row = source['materiality'][arm]
        item = {'observations': count(row['observations'])}
        if item['observations'] != result['plans']['90']['inventory'][arm]['definite']:
            raise ValueError('materiality observation count mismatch')
        item['assumed_one_event_haircut'] = number(row['assumed_one_event_haircut'])
        if item['assumed_one_event_haircut'] != .1:
            raise ValueError('stress assumption changed; review required')
        for quantity in ('position_value_cny', 'position_fraction_nav', 'conditional_nav_loss_fraction'):
            for end in ('min', 'max'):
                item[f'{quantity}_{end}'] = number(row[f'{quantity}_{end}'])
            if item[f'{quantity}_min'] > item[f'{quantity}_max']:
                raise ValueError('invalid materiality range')
        for end in ('min', 'max'):
            expected = item[f'position_fraction_nav_{end}'] * item['assumed_one_event_haircut']
            if not math.isclose(item[f'conditional_nav_loss_fraction_{end}'], expected,
                                rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError('stress fraction does not reconcile')
        result['materiality'][arm] = item
    return result


FALSE_FLAGS = ('exposed_blocker_clearance', 'tax_and_historical_broker_fees_known',
               'historical_availability_certified', 'ordinary_historical_gates_certified',
               'selected_portfolio_entitlement_certified')
TRUE_FLAGS = ('synthetic_delayed_settlement_tests', 'conditional_conservative_gate_zero_fills',
              'provider_suspension_vs_primary_resumption_conflict',
              'accounting_oracle_source_bound', 'coherent_wrong_rights_marks_fees_rejected')


def project_account(source):
    if (source['schema'] != 'microcap-account-public/v1'
            or any(source[key] is not False for key in FALSE_FLAGS)
            or any(source[key] is not True for key in TRUE_FLAGS)
            or source['additional_exposed_event_primary_economics_reviewed'] != 1
            or source['empirical_delayed_receivable_days'] != 0):
        raise ValueError('account evidence scope changed; review required')
    expected = [f'account-{i}' for i in range(1, 5)]
    if [row['case_id'] for row in source['cases']] != expected:
        raise ValueError('account cases changed; review required')
    cases = []
    for row in source['cases']:
        if set(row['actions']) - {'record', 'ex', 'stock_release', 'cash_payment'}:
            raise ValueError('unknown account action')
        error = number(row['max_identity_error'])
        if error > 1e-7:
            raise ValueError('unreconciled account')
        cases.append({'case_id': row['case_id'], 'sessions': count(row['sessions']),
                      'fills': count(row['fills']), 'actions': list(row['actions']),
                      'max_identity_error': error})
    return {'cases': cases, **{key: False for key in FALSE_FLAGS},
            **{key: True for key in TRUE_FLAGS},
            'additional_exposed_event_primary_economics_reviewed': 1,
            'empirical_delayed_receivable_days': 0}


def project_register(rows):
    if len(rows) != 2:
        raise ValueError('reviewed register prefix changed')
    projected = []
    previous = None
    for sequence, row in enumerate(rows, 1):
        body = {key: value for key, value in row.items() if key != 'hash'}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':'),
                                          allow_nan=False).encode()).hexdigest()
        if (row['hash'] != digest or row['sequence'] != sequence
                or row['previous'] != previous or row['predecessor'] != previous
                or row['kind'] != 'historical_import'):
            raise ValueError('register chain changed; review required')
        receipt = row['receipt']
        if (receipt['protocol_id'] != 'microcap-prospective-20261017/v1'
                or receipt['formation'] != '2026-10-30'
                or receipt['status'] != 'pending_before_cutoff'
                or receipt['admitted'] is not False or receipt['new_cohort_completed_windows'] != 0
                or receipt['issue_count'] != (8 if sequence == 1 else 7)):
            raise ValueError('prospective evidence changed; review required')
        projected.append({'sequence': sequence, 'original_as_of_utc': clock(receipt['as_of_utc']),
                          'imported_utc': clock(row['event_utc']),
                          'status': receipt['status'], 'issue_count': receipt['issue_count']})
        previous = digest
    return {'entry_count': 2, 'head_sha256': previous, 'observations': projected,
            'admitted': False, 'new_completed_windows': 0, 'scheduler_installed': False,
            'whole_directory_replacement_protected': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('exposure', 'account', 'register', 'account-reproduction', 'register-guard-manifest', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    paths = {key: getattr(args, key) for key in ('exposure', 'account', 'register',
             'account_reproduction', 'register_guard_manifest')}
    raw = {key: path.read_bytes() for key, path in paths.items()}
    parsed = {key: json.loads(value) for key, value in raw.items()}
    if parsed['account_reproduction']['engine_commit'] != ENGINE:
        raise ValueError('engine revision changed; review required')
    result = {'schema_version': 1, 'reviewed_on': '2026-10-18', 'raw_share_ready': False,
              'original_runtime_recovered': False, 'account_engine_commit': ENGINE,
              'exposure': project_exposure(parsed['exposure']),
              'account': project_account(parsed['account']),
              'register': project_register(parsed['register']),
              'source_sha256': {key: hashlib.sha256(value).hexdigest() for key, value in raw.items()}}
    if any(path.read_bytes() != raw[key] for key, path in paths.items()):
        raise ValueError('source changed during projection')
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
