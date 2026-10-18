"""Publication must preserve unknowns and strip private event/account identities."""

import copy
import importlib.util
from pathlib import Path

import pytest


def projector():
    spec = importlib.util.spec_from_file_location(
        'chain_projection', Path(__file__).parents[1] / 'scripts/review_microcap_chain.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def notices():
    return {'schema': 'private-held-event-primary-terms/v1', 'events': [
        {'event_id': f'PRIVATE-{i}', 'symbol': f'PRIVATE-{i}',
         'record_date': '2021-10-12', 'ex_date': '2021-10-13',
         'unrestricted_new_share_listing_date': '2021-10-14' if i == 6 else '2021-10-13',
         'cash_per_raw_share_gross_rmb': None if i < 3 else '0',
         'capitalization_new_shares_per_raw_share': '0.4',
         'fraction_allocation': {'status': 'explicit' if i < 6 else 'unknown in this notice'},
         'holder_account_and_integer_raw_inventory_certified': False, 'tax_certified': False,
         'source_path': '/home/PRIVATE', 'source_sha256': 'a' * 64,
         'primary_url': 'https://static.cninfo.com.cn/source.pdf'} for i in range(7)]}


def test_notices_publish_counts_without_private_rows_or_unknown_cash_as_zero():
    result = projector().project_primary(notices())
    assert result == {'reviewed_held_events': 7, 'primary_notices': 7,
                      'explicit_fraction_methods': 6, 'listing_after_ex': 1,
                      'cash_numeric_unspecified': 3,
                      'holder_inventory_certified': False, 'tax_certified': False}
    assert 'PRIVATE' not in str(result)


@pytest.mark.parametrize('mutation', ['duplicate', 'holder', 'tax', 'negative', 'listing'])
def test_changed_notice_scope_or_certification_fails_closed(mutation):
    value = notices()
    row = value['events'][0]
    if mutation == 'duplicate':
        value['events'][1] = copy.deepcopy(row)
    elif mutation == 'holder':
        row['holder_account_and_integer_raw_inventory_certified'] = True
    elif mutation == 'tax':
        row['tax_certified'] = True
    elif mutation == 'negative':
        row['capitalization_new_shares_per_raw_share'] = '-1'
    else:
        row['unrestricted_new_share_listing_date'] = '2021-10-11'
    with pytest.raises(ValueError):
        projector().project_primary(value)


def test_trace_keeps_dated_unknown_separate_from_initial_cash_interpretation():
    source = {'schema': 'microcap-unknown-inventory-trace/v1',
              'consumed_inputs_unchanged': True,
              'original_convention': {'leading_return_padding_rows': 63,
                                      'pre_first_entry_dated_account_rows_retained': False},
              'events': [{'retained_dated_inventory_classification': 'unknown',
                          'original_inventory_recovered': False,
                          'candidate_source_derived_classification':
                          'absent_under_explicit_pre_activation_cash_contract',
                          'raw_share_entitlement_identified': False,
                          'target_history': {'45': [{'latest_target_weight': .025 if i == 0 else 0}]}}
                         for i in range(6)],
              'original_engine_hash_checks': [{'matches_original_receipt': True}] * 19,
              'retained_output_coverage': {str(i): {} for i in range(38)},
              'min45_remedy_feasibility': {'old_fills_or_inventory_recovered': False}}
    result = projector().project_trace(source)
    assert result['dated_inventory_unknown'] == 6
    assert result['derived_pre_activation_cash_absence'] == 6
    assert result['min45_positive_prior_target_events'] == 1
    assert result['original_inventory_recovered'] is False
    source['events'][0]['original_inventory_recovered'] = True
    with pytest.raises(ValueError):
        projector().project_trace(source)


def test_manual_review_cannot_become_new_observation_or_admission():
    source = {'kind': 'manual_read_only_verification_not_market_observation',
              'actual_review_utc': '2026-10-18T15:17:12+00:00',
              'register_entries': 2, 'register_head': '6' * 64,
              'anchor_sequence': 2, 'anchor_verified': True,
              'register_all_files_unchanged': True, 'pending_transaction': False,
              'no_append': True, 'no_alias_change': True, 'no_job_installed': True,
              'summary': {'issue_count': 7, 'admitted': False,
                          'new_cohort_completed_windows': 0, 'status': 'pending_before_cutoff'},
              'production': {'readiness_cli_exists': False}}
    result = projector().project_prospective(source)
    assert result['kind'] == 'manual_verification'
    assert result['new_completed_windows'] == 0
    assert result['scheduler_installed'] is False
    source['summary']['admitted'] = True
    with pytest.raises(ValueError):
        projector().project_prospective(source)


def failed_slice():
    return {'schema': 'microcap-frozen-target-raw-account/v1',
            'status': 'account_reconciliation_failed', 'fail_closed': True,
            'preflight': {'sessions': 21, 'symbols': 46, 'query_rows_scanned': 2230,
                          'included_events': ['PRIVATE'], 'excluded_events': [{'symbol': 'PRIVATE'}]},
            'target_count_per_formation': {'PRIVATE-A': 40, 'PRIVATE-B': 40},
            'action_query_covered_symbols': 46, 'source_checks_unchanged': True,
            'engine_source_checks_unchanged': True,
            'failure': 'AssertionError: fill violates 100-share lot/full-liquidation assumption: PRIVATE',
            'outputs_sha256': {name: 'a' * 64 for name in [
                'all_cached_query_rows.parquet', 'executed_audit.py', 'original_terms.json',
                'raw_inputs.parquet', 'targets.parquet', 'uncertified_candidate_actions.parquet',
                'uncertified_candidate_fills.parquet', 'uncertified_candidate_orders.parquet']}}


def test_failed_account_publishes_input_coverage_without_an_accepted_nav():
    result = projector().project_slice(failed_slice())
    assert result == {'status': 'blocked_by_sell_quantity_contract', 'fail_closed': True,
                      'accepted_nav': False, 'formations': 2, 'targets_per_formation': 40,
                      'distinct_target_names': 46, 'sessions': 21, 'query_rows_scanned': 2230,
                      'included_actions': 1, 'excluded_pre_entry_actions': 1,
                      'historical_account_recovered': False}
    assert 'PRIVATE' not in str(result)


@pytest.mark.parametrize('mutation', ['source_changed', 'accepted_nav', 'completed'])
def test_changed_account_claims_require_a_new_review(mutation):
    source = failed_slice()
    if mutation == 'source_changed':
        source['source_checks_unchanged'] = False
    elif mutation == 'accepted_nav':
        source['outputs_sha256']['daily.parquet'] = 'a' * 64
    else:
        source['status'] = 'completed'
    with pytest.raises(ValueError):
        projector().project_slice(source)
