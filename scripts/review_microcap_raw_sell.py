"""Project an independently reviewed bounded replay; never publish account identities."""

import argparse
import hashlib
import json
import re
from datetime import date
from decimal import Decimal
from pathlib import Path


REVIEW_CHECKS = {
    'provider_merged_pin_verified', 'provider_regression_tests_passed',
    'default_continuous_compatibility_verified', 'independent_account_oracle_passed',
    'integer_holdings_verified', 'sell_lot_or_full_liquidation_verified', 'buy_lot_verified',
    'frozen_inputs_verified', 'prior_failed_receipt_preserved', 'source_and_engine_unchanged',
    'raw_or_unspecified_price_basis_only', 'adjusted_price_basis_rejected',
    'capacity_weight_ledger_rejected', 'tiny_residue_preserved', 'capacity_not_expanded',
    'fractional_inventory_fails_closed',
}
CAPTURES = {'raw_inputs.parquet', 'targets.parquet', 'all_cached_query_rows.parquet',
            'original_terms.json'}
MATCHED_FIELDS = {'formations', 'window', 'starting_cash_cny', 'assumptions', 'preflight',
                  'target_count_per_formation', 'action_query_covered_symbols'}
CERTIFICATIONS = {'full_period', 'historical_account', 'tax', 'registrar_holder',
                  'historical_information_set'}
REVIEW_KEYS = {'schema', 'status', 'reviewed_on', 'source_manifest_sha256',
               'identity_errors_sha256', 'provider_revision', 'checks', 'fill_counts',
               'max_errors_cny', 'account_tolerance_cny'}


def require(condition, message='Evidence changed; independent review required'):
    if not condition:
        raise ValueError(message)


def digest(value, length=64):
    require(isinstance(value, str) and re.fullmatch(f'[0-9a-f]{{{length}}}', value) is not None)
    return value


def number(value):
    require(type(value) in (int, float))
    result = Decimal(str(value))
    require(result.is_finite() and result >= 0)
    return result


def count(value):
    require(type(value) is int and value >= 0)
    return value


def project_replay(source, review, source_sha256, review_sha256, previous):
    """The wrapper records a separate review; successful execution is insufficient."""
    digest(source_sha256)
    digest(review_sha256)
    require(set(review) == REVIEW_KEYS)
    require(review['schema'] == 'microcap-raw-sell-independent-review/v1'
            and review['status'] == 'approved_bounded_account_replay')
    date.fromisoformat(review['reviewed_on'])
    require(digest(review['source_manifest_sha256']) == source_sha256)
    require(set(review['checks']) == REVIEW_CHECKS
            and all(value is True for value in review['checks'].values()))
    require(source['schema'] == 'microcap-frozen-target-raw-account/v1'
            and source['status'] == 'completed' and source['fail_closed'] is False
            and source['evidence_stage'] == 'pinned_provider'
            and source['publication_eligible_without_independent_review'] is False)
    require(digest(source['engine_revision'], 40) == digest(review['provider_revision'], 40))
    require(source['source_checks_unchanged'] is True
            and source['engine_source_checks_unchanged'] is True)
    require(set(source['certification']) == CERTIFICATIONS
            and all(value is False for value in source['certification'].values()))
    policy = source['execution_policy']
    require(policy['round_lot'] == 100 and policy['sell_round_lot'] == 100
            and policy['full_integral_liquidation_allowed'] is True)

    prior = previous['target_slice']
    require(previous['raw_share_strategy_ready'] is False
            and prior['status'] == 'blocked_by_sell_quantity_contract'
            and prior['accepted_nav'] is False)
    comparison = source['comparison']
    require(digest(comparison['baseline_manifest_sha256']) == previous['source_sha256']['slice']
            and comparison['baseline_status'] == 'account_reconciliation_failed'
            and comparison['baseline_fail_closed'] is True
            and comparison['frozen_inputs_match'] is True
            and comparison['captured_frozen_artifacts_match'] is True
            and comparison['adapter_code_change_permitted'] is True)
    require(set(comparison['matched_fields']) == MATCHED_FIELDS
            and len(comparison['matched_fields']) == len(MATCHED_FIELDS)
            and count(comparison['matched_noncode_input_count']) == 57)
    captures = comparison['captured_frozen_artifacts_sha256']
    require(set(captures) == CAPTURES)
    outputs = source['outputs_sha256']
    require(CAPTURES | {'daily.parquet', 'holdings.parquet', 'fills.parquet',
                        'orders.parquet', 'actions.parquet', 'identity_errors.json'} <= set(outputs))
    require(all(digest(value) == outputs[name] for name, value in captures.items()))
    require(digest(review['identity_errors_sha256']) == outputs['identity_errors.json'])

    preflight = source['preflight']
    targets = source['target_count_per_formation']
    require(len(source['formations']) == len(targets) == prior['formations'] == 2
            and set(targets.values()) == {prior['targets_per_formation']} == {40}
            and count(source['sessions']) == preflight['sessions'] == prior['sessions'] == 21
            and source['action_query_covered_symbols'] == preflight['symbols']
            == prior['distinct_target_names'] == 46
            and preflight['query_rows_scanned'] == prior['query_rows_scanned'] == 2230
            and len(preflight['included_events']) == prior['included_actions'] == 1
            and len(preflight['excluded_events']) == prior['excluded_pre_entry_actions'] == 1)
    require(set(review['fill_counts']) == {'buy', 'sell'})
    buys, sells = (count(review['fill_counts'][key]) for key in ('buy', 'sell'))
    require(count(source['fills']) == buys + sells and sells > 0)
    require(number(review['account_tolerance_cny']) == Decimal('1e-7'))
    errors = review['max_errors_cny']
    require(set(errors) == {'cash', 'marked_value', 'fees', 'identity'})
    require(all(number(value) <= Decimal('1e-7') for value in errors.values()))
    require(number(errors['identity']) == number(source['max_identity_error'])
            == max(number(value) for value in errors.values()))

    return {
        'schema_version': 1, 'reviewed_on': review['reviewed_on'],
        'status': 'bounded_account_reconciled', 'raw_share_strategy_ready': False,
        'new_prospective_observations': 0,
        'comparison': {'noncode_inputs_matched': comparison['matched_noncode_input_count'],
                       'captured_artifacts_matched': len(captures),
                       'window_targets_calendar_match': True, 'inputs_unchanged': True,
                       'prior_failure_retained': True},
        'policy': {'explicit_sell_round_lot': 100, 'buy_lot_independent': True,
                   'sell_round_lot_default_is_continuous': True,
                   'default_compatibility_scope': 'provider_regression_tests',
                   'full_integer_liquidation_allowed': True,
                   'adjusted_price_basis_allowed': False, 'capacity_weight_ledger_allowed': False,
                   'fraction_tolerance_cap': 1e-8, 'tiny_float_residue_preserved': True,
                   'capacity_expansion': False},
        'account': {'sessions': source['sessions'], 'formations': len(targets),
                    'targets_per_formation': 40, 'distinct_target_names': preflight['symbols'],
                    'query_rows_scanned': preflight['query_rows_scanned'],
                    'included_actions': len(preflight['included_events']),
                    'excluded_pre_entry_actions': len(preflight['excluded_events']),
                    'fills': source['fills'], 'buy_fills': buys, 'sell_fills': sells,
                    'all_inventory_integral': True, 'max_errors_cny': dict(errors),
                    'tolerance_cny': review['account_tolerance_cny']},
        'certification': dict(source['certification']),
        'source_sha256': {'account_manifest': source_sha256,
                          'independent_review': review_sha256,
                          'prior_failed_receipt': comparison['baseline_manifest_sha256']},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('source', 'review', 'previous_public', 'output'):
        parser.add_argument('--' + key.replace('_', '-'), type=Path, required=True)
    args = parser.parse_args()
    paths = {'source': args.source, 'review': args.review, 'previous': args.previous_public}
    raw = {key: path.read_bytes() for key, path in paths.items()}
    values = {key: json.loads(value) for key, value in raw.items()}
    result = project_replay(values['source'], values['review'],
                            hashlib.sha256(raw['source']).hexdigest(),
                            hashlib.sha256(raw['review']).hexdigest(), values['previous'])
    require(all(path.read_bytes() == raw[key] for key, path in paths.items()),
            'Input changed during projection')
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
