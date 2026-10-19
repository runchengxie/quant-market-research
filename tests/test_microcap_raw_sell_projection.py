"""Only an independently reviewed, source-bound bounded replay may be published."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


CHECKS = {
    'provider_merged_pin_verified', 'provider_regression_tests_passed',
    'default_continuous_compatibility_verified', 'independent_account_oracle_passed',
    'integer_holdings_verified', 'sell_lot_or_full_liquidation_verified', 'buy_lot_verified',
    'frozen_inputs_verified', 'prior_failed_receipt_preserved', 'source_and_engine_unchanged',
    'raw_or_unspecified_price_basis_only', 'adjusted_price_basis_rejected',
    'capacity_weight_ledger_rejected', 'tiny_residue_preserved', 'capacity_not_expanded',
    'fractional_inventory_fails_closed',
}
CAPTURES = ['raw_inputs.parquet', 'targets.parquet', 'all_cached_query_rows.parquet',
            'original_terms.json']


def projector():
    path = Path(__file__).parents[1] / 'scripts/review_microcap_raw_sell.py'
    spec = importlib.util.spec_from_file_location('raw_sell_projection', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def evidence():
    """Synthetic review only; these fill counts and errors are not research results."""
    previous = {'raw_share_strategy_ready': False,
                'target_slice': {'status': 'blocked_by_sell_quantity_contract',
                                 'accepted_nav': False, 'formations': 2,
                                 'targets_per_formation': 40, 'distinct_target_names': 46,
                                 'sessions': 21, 'query_rows_scanned': 2230,
                                 'included_actions': 1, 'excluded_pre_entry_actions': 1},
                'source_sha256': {'slice': 'b' * 64}}
    source = {'schema': 'microcap-frozen-target-raw-account/v1', 'status': 'completed',
              'fail_closed': False, 'evidence_stage': 'pinned_provider',
              'publication_eligible_without_independent_review': False,
              'engine_revision': 'a' * 40, 'source_checks_unchanged': True,
              'engine_source_checks_unchanged': True,
              'execution_policy': {'round_lot': 100, 'sell_round_lot': 100,
                                   'full_integral_liquidation_allowed': True,
                                   'default_provider_continuous_compatibility':
                                   'provider tests only; not inferred from this replay'},
              'certification': {key: False for key in ['full_period', 'historical_account',
                                 'tax', 'registrar_holder', 'historical_information_set']},
              'formations': ['PRIVATE-formation-a', 'PRIVATE-formation-b'],
              'window': ['2000-01-01', '2000-01-31'],
              'target_count_per_formation': {'PRIVATE-a': 40, 'PRIVATE-b': 40},
              'action_query_covered_symbols': 46,
              'preflight': {'sessions': 21, 'symbols': 46, 'query_rows_scanned': 2230,
                            'included_events': ['PRIVATE'], 'excluded_events': ['PRIVATE']},
              'comparison': {'baseline_manifest_sha256': 'b' * 64,
                             'baseline_status': 'account_reconciliation_failed',
                             'baseline_fail_closed': True, 'frozen_inputs_match': True,
                             'matched_fields': ['formations', 'window', 'starting_cash_cny',
                                                'assumptions', 'preflight',
                                                'target_count_per_formation',
                                                'action_query_covered_symbols'],
                             'matched_noncode_input_count': 57,
                             'adapter_code_change_permitted': True,
                             'captured_frozen_artifacts_match': True,
                             'captured_frozen_artifacts_sha256': {k: 'c' * 64 for k in CAPTURES}},
              'sessions': 21, 'fills': 5, 'max_identity_error': 1e-10,
              'ending_value_cny': 9999999, 'source_path': '/home/PRIVATE',
              'outputs_sha256': {k: 'c' * 64 for k in CAPTURES + [
                  'daily.parquet', 'holdings.parquet', 'fills.parquet', 'orders.parquet',
                  'actions.parquet', 'identity_errors.json']}}
    review = {'schema': 'microcap-raw-sell-independent-review/v1',
              'status': 'approved_bounded_account_replay', 'reviewed_on': '2000-02-01',
              'source_manifest_sha256': sha(source), 'identity_errors_sha256': 'c' * 64,
              'provider_revision': 'a' * 40, 'checks': {key: True for key in CHECKS},
              'fill_counts': {'buy': 4, 'sell': 1},
              'max_errors_cny': {'cash': 1e-11, 'marked_value': 1e-10,
                                 'fees': 0.0, 'identity': 1e-10},
              'account_tolerance_cny': 1e-7}
    return source, review, previous


def project(source, review, previous):
    return projector().project_replay(source, review, sha(source), sha(review), previous)


def test_projection_emits_aggregates_and_retains_uncertified_scope():
    source, review, previous = evidence()
    result = project(source, review, previous)
    assert result['status'] == 'bounded_account_reconciled'
    assert result['account']['fills'] == 5
    assert result['account']['buy_fills'] + result['account']['sell_fills'] == 5
    assert result['account']['max_errors_cny']['fees'] == 0.0
    assert result['account']['tolerance_cny'] == 1e-7
    assert result['comparison']['noncode_inputs_matched'] == 57
    assert result['comparison']['captured_artifacts_matched'] == 4
    assert result['policy']['default_compatibility_scope'] == 'provider_regression_tests'
    assert result['raw_share_strategy_ready'] is False
    assert not any(result['certification'].values())
    assert result['new_prospective_observations'] == 0
    assert 'PRIVATE' not in json.dumps(result)
    assert 'ending_value' not in json.dumps(result)
    assert '/home/' not in json.dumps(result)


@pytest.mark.parametrize('key', sorted(CHECKS))
def test_any_unreviewed_contract_gate_rejects_projection(key):
    source, review, previous = evidence()
    review['checks'][key] = False
    with pytest.raises(ValueError):
        project(source, review, previous)


@pytest.mark.parametrize('mutation', [
    'source_changed', 'engine_changed', 'unmerged', 'provisional', 'self_approved',
    'source_hash', 'identity_hash', 'provider_pin', 'prior_receipt', 'frozen_mismatch',
    'capture_mismatch', 'capture_output', 'scope_mismatch', 'fill_mismatch', 'error_large',
    'error_nan', 'error_negative', 'tolerance_relaxed', 'identity_mismatch', 'unknown_review_field',
])
def test_changed_sources_mismatches_and_relaxed_checks_fail_closed(mutation):
    source, review, previous = evidence()
    if mutation == 'source_changed':
        source['source_checks_unchanged'] = False
    elif mutation == 'engine_changed':
        source['engine_source_checks_unchanged'] = False
    elif mutation == 'unmerged':
        review['checks']['provider_merged_pin_verified'] = False
    elif mutation == 'provisional':
        source['evidence_stage'] = 'provisional'
    elif mutation == 'self_approved':
        source['publication_eligible_without_independent_review'] = True
    elif mutation == 'source_hash':
        review['source_manifest_sha256'] = 'd' * 64
    elif mutation == 'identity_hash':
        review['identity_errors_sha256'] = 'd' * 64
    elif mutation == 'provider_pin':
        review['provider_revision'] = 'd' * 40
    elif mutation == 'prior_receipt':
        previous['source_sha256']['slice'] = 'd' * 64
    elif mutation == 'frozen_mismatch':
        source['comparison']['frozen_inputs_match'] = False
    elif mutation == 'capture_mismatch':
        source['comparison']['captured_frozen_artifacts_match'] = False
    elif mutation == 'capture_output':
        source['outputs_sha256'][CAPTURES[0]] = 'd' * 64
    elif mutation == 'scope_mismatch':
        source['sessions'] += 1
    elif mutation == 'fill_mismatch':
        review['fill_counts']['sell'] += 1
    elif mutation == 'error_large':
        review['max_errors_cny']['cash'] = 1e-6
    elif mutation == 'error_nan':
        review['max_errors_cny']['cash'] = float('nan')
    elif mutation == 'error_negative':
        review['max_errors_cny']['cash'] = -1e-10
    elif mutation == 'tolerance_relaxed':
        review['account_tolerance_cny'] = 1e-6
    elif mutation == 'identity_mismatch':
        review['max_errors_cny']['identity'] = 0
    else:
        review['certified_full_history'] = True
    # Refresh binding to exercise the semantic rejection as well as hash rejection.
    if mutation != 'source_hash':
        review['source_manifest_sha256'] = sha(source)
    with pytest.raises(ValueError):
        project(source, review, previous)


@pytest.mark.parametrize('claim', ['full_period', 'historical_account', 'tax',
                                   'registrar_holder', 'historical_information_set'])
def test_successful_slice_cannot_become_full_strategy_or_holder_certification(claim):
    source, review, previous = evidence()
    source['certification'][claim] = True
    review['source_manifest_sha256'] = sha(source)
    with pytest.raises(ValueError):
        project(source, review, previous)


def test_source_fingerprint_cannot_be_changed_after_independent_review():
    source, review, previous = evidence()
    changed = copy.deepcopy(source)
    changed['ending_value_cny'] += 1
    with pytest.raises(ValueError):
        project(changed, review, previous)
