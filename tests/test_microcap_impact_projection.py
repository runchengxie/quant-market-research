import copy
import hashlib
import json

import pytest

from scripts.review_microcap_impact import project_account, project_exposure, project_register


def exposure():
    partition = {'definite': 7, 'possible': 0, 'absent': 81, 'unknown': 6}
    return {
        'unique_events': 94, 'unknown_exdate_rows': 1,
        'plans': {
            '45': {'target': {'definite': 6, 'possible': 0, 'absent': 88, 'unknown': 0},
                   'inventory': {}, 'inventory_status': 'not_retained'},
            '90': {'target': {'definite': 6, 'possible': 0, 'absent': 88, 'unknown': 0},
                   'inventory': {key: dict(partition, definite=6, absent=82)
                                 if key.startswith('capacity') else partition.copy()
                                 for key in ['owner_ideal_fee10', 'capacity_without_limits',
                                             'capacity_with_limits', 'prior20_budget_realized_guard']}},
        },
        'materiality': {key: {'observations': 7, 'position_value_cny_min': 1_000_000,
                             'position_value_cny_max': 2_000_000,
                             'position_fraction_nav_min': .01, 'position_fraction_nav_max': .02,
                             'assumed_one_event_haircut': .1,
                             'conditional_nav_loss_fraction_min': .001,
                             'conditional_nav_loss_fraction_max': .002,
                             'interpretation': '/private/ignored'}
                        for key in ['owner_ideal_fee10', 'prior20_budget_realized_guard']},
        'account_impact': 'nonidentifiable_without_raw_share_ledger_and_complete_action_terms',
        'private_rows': [{'symbol': 'PRIVATE'}],
    }


def account():
    return {'schema': 'microcap-account-public/v1',
            'scope': '/private',
            'cases': [{'case_id': f'account-{i}', 'sessions': 3 if i == 4 else 4,
                       'fills': 1, 'actions': [] if i == 4 else ['record', 'ex',
                       'cash_payment' if i == 2 else 'stock_release'],
                       'max_identity_error': 1e-11, 'symbol': 'PRIVATE'} for i in range(1, 5)],
            'accounting_oracle_source_bound': True,
            'coherent_wrong_rights_marks_fees_rejected': True,
            'additional_exposed_event_primary_economics_reviewed': 1,
            'empirical_delayed_receivable_days': 0,
            'synthetic_delayed_settlement_tests': True,
            'conditional_conservative_gate_zero_fills': True,
            'provider_suspension_vs_primary_resumption_conflict': True,
            **{key: False for key in ['exposed_blocker_clearance',
               'tax_and_historical_broker_fees_known', 'historical_availability_certified',
               'ordinary_historical_gates_certified', 'selected_portfolio_entitlement_certified']}}


def registry():
    rows = []
    for sequence, issues in [(1, 8), (2, 7)]:
        previous = rows[-1]['hash'] if rows else None
        row = {'sequence': sequence, 'previous': previous, 'predecessor': previous,
               'kind': 'historical_import', 'event_utc': f'2026-10-18T03:16:{sequence:02d}+00:00',
               'receipt': {'protocol_id': 'microcap-prospective-20261017/v1',
                           'formation': '2026-10-30', 'as_of_utc': f'2026-10-17T23:4{sequence}:00+00:00',
                           'status': 'pending_before_cutoff', 'issue_count': issues,
                           'admitted': False, 'new_cohort_completed_windows': 0,
                           'issues': ['/private'] * issues},
               'spec': {'private': '/home/private'}}
        row['hash'] = hashlib.sha256(json.dumps(row, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        rows.append(row)
    return rows


def test_exposure_preserves_missing_inventory_and_unknown_record_dates():
    result = project_exposure(exposure())
    assert result['plans']['45']['inventory_status'] == 'not_retained'
    assert result['plans']['45']['inventory'] == {}
    assert result['plans']['90']['inventory']['owner_ideal_fee10'] == {
        'definite': 7, 'possible': 0, 'absent': 81, 'unknown': 6}
    assert 'PRIVATE' not in json.dumps(result)
    assert '/private' not in json.dumps(result)
    assert result['materiality']['owner_ideal_fee10']['conditional_nav_loss_fraction_min'] == .001


@pytest.mark.parametrize('fault', ['null', 'nan', 'negative', 'partition', 'ratio', 'haircut', 'min45_inventory'])
def test_invalid_exposure_or_unreviewed_assumptions_fail_closed(fault):
    source = exposure()
    row = source['plans']['90']['inventory']['owner_ideal_fee10']
    if fault in ['null', 'nan', 'negative']:
        row['unknown'] = {'null': None, 'nan': float('nan'), 'negative': -1}[fault]
    elif fault == 'partition':
        row['absent'] += 1
    elif fault == 'min45_inventory':
        source['plans']['45']['inventory'] = {'invented': row}
    else:
        source['materiality']['owner_ideal_fee10'][
            'assumed_one_event_haircut' if fault == 'haircut' else 'conditional_nav_loss_fraction_min'] = .2
    with pytest.raises(ValueError):
        project_exposure(source)


def test_account_projection_keeps_conditional_gate_and_no_clearance():
    result = project_account(account())
    assert len(result['cases']) == 4
    assert sum(row['sessions'] for row in result['cases']) == 15
    assert result['provider_suspension_vs_primary_resumption_conflict'] is True
    assert result['exposed_blocker_clearance'] is False
    assert 'PRIVATE' not in json.dumps(result)
    assert '/private' not in json.dumps(result)


@pytest.mark.parametrize('fault', ['error', 'nonfinite', 'duplicate', 'tax_upgrade', 'clearance', 'source_oracle'])
def test_account_rejects_unreconciled_or_upgraded_scope(fault):
    source = account()
    if fault == 'error':
        source['cases'][0]['max_identity_error'] = .01
    elif fault == 'nonfinite':
        source['cases'][0]['max_identity_error'] = float('nan')
    elif fault == 'duplicate':
        source['cases'][1]['case_id'] = 'account-1'
    elif fault == 'source_oracle':
        source['accounting_oracle_source_bound'] = False
    else:
        source['tax_and_historical_broker_fees_known' if fault == 'tax_upgrade'
               else 'exposed_blocker_clearance'] = True
    with pytest.raises(ValueError):
        project_account(source)


def test_registry_preserves_original_vs_import_clocks_without_private_receipts():
    result = project_register(registry())
    assert result['entry_count'] == 2
    assert [row['issue_count'] for row in result['observations']] == [8, 7]
    assert result['observations'][0]['original_as_of_utc'] != result['observations'][0]['imported_utc']
    assert result['whole_directory_replacement_protected'] is False
    assert 'PRIVATE' not in json.dumps(result)
    assert '/private' not in json.dumps(result)


@pytest.mark.parametrize('fault', ['reorder', 'hash', 'truncation', 'new_market_observation'])
def test_changed_registry_requires_review(fault):
    source = copy.deepcopy(registry())
    if fault == 'reorder':
        source.reverse()
    elif fault == 'hash':
        source[1]['hash'] = '0' * 64
    elif fault == 'truncation':
        source.pop()
    else:
        source[1]['receipt']['admitted'] = True
    with pytest.raises(ValueError):
        project_register(source)
