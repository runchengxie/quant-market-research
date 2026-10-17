"""Allowlisted public projection of four reviewed microcap evidence follow-ups."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ARMS = {'ideal_one_day', 'retry_tradable_unlimited', 'same_day_capacity',
        'same_day_capacity_lots', 'same_day_capacity_lots_t1',
        'same_day_capacity_lots_t1_limits', 'prior20_budget', 'prior20_budget_realized_guard'}
DRAW_FIELDS = ('arm', 'peak_date', 'peak_is_initial_capital', 'trough_date', 'recovery_date',
               'right_censored', 'drawdown_pct', 'peak_to_trough_sessions',
               'trough_to_recovery_or_end_sessions', 'peak_to_recovery_or_end_sessions',
               'worst_calendar_year', 'worst_calendar_return_pct', 'worst_year_observed_sessions',
               'worst_year_partial')
CASE_FIELDS = ('selection_field', 'date', 'cash_weight_pct', 'open_orders_end_of_day',
               'orders_active_inclusive_date_count', 'active_orders_with_zero_fill_days',
               'window_positive_fill_records')
ORDER_FIELDS = ('entry_date', 'closed_date', 'side', 'status', 'zero_fill_days', 'fill_days',
                'max_days', 'requested_notional', 'filled_notional', 'unfilled_notional', 'fill_ratio')
PROTOCOL_FIELDS = ('protocol_id', 'decision_utc', 'registration_status', 'next_candidate_formation',
                   'new_cohort_completed_windows', 'legacy_completed_windows', 'legacy_pending_windows',
                   'legacy_as_of', 'primary_stage', 'comparator_stage', 'turnover_window_sessions',
                   'minimum_turnover_observations', 'bucket_count', 'primary_confirmatory_windows',
                   'hac_maxlags', 'scheduler_installed')
CLAIM_FIELDS = ('id', 'title', 'stage', 'upgrade_condition', 'invalidating_evidence', 'resumption_trigger')


def fields(record, names):
    return {key: record[key] for key in names}


def finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('nonfinite public number')
    if isinstance(value, dict):
        for item in value.values():
            finite_tree(item)
    if isinstance(value, list):
        for item in value:
            finite_tree(item)


def project(failure, protocol, claims):
    if len(failure['drawdown_cases']) != 8 or {row['arm'] for row in failure['drawdown_cases']} != ARMS:
        raise ValueError('unreviewed execution arms')
    if protocol['new_cohort_completed_windows'] != 0 or protocol['scheduler_installed']:
        raise ValueError('prospective state changed; review required')
    if [row['id'] for row in claims['claims']] != [f'MC-C{i:02}' for i in range(1, 7)]:
        raise ValueError('claim register scope changed')
    failures = fields(failure, ('sessions', 'start', 'end', 'synthetic_adjusted_shares',
                                'capital_cny', 'cost_bps', 'leading_cash_sessions', 'execution_case_arm'))
    failures['drawdown_cases'] = [fields(row, DRAW_FIELDS) for row in failure['drawdown_cases']]
    failures['curves'] = {key: [fields(row, ('date', 'nav', 'drawdown_pct')) for row in failure['curves'][key]] for key in (
        'ideal_one_day', 'same_day_capacity_lots_t1_limits', 'prior20_budget', 'prior20_budget_realized_guard')}
    failures['execution_cases'] = [{**fields(row, CASE_FIELDS), 'window': [fields(point, ('date', 'cash_weight_pct', 'open_orders_end_of_day')) for point in row['window']]} for row in failure['execution_cases']]
    failures['maximum_zero_fill_order'] = fields(failure['maximum_zero_fill_order'], ORDER_FIELDS)
    payload = {'schema_version': 1, 'reviewed_on': '2026-10-17', 'failure_atlas': failures,
               'prospective': fields(protocol, PROTOCOL_FIELDS),
               'next_manual_claim_review': claims['next_scheduled_review'],
               'claims': [fields(row, CLAIM_FIELDS) for row in claims['claims']]}
    finite_tree(payload)
    return payload


SIZE_TOP = ('schema_version', 'evidence_status', 'causal', 'untouched_holdout', 'bucket_count',
            'hac_maxlags', 'formation_start', 'formation_end', 'period_end', 'formation_count',
            'return_clock', 'common_support', 'direction')
SIZE_STATS = ('universe', 'coefficient', 'coefficient_mean', 'hac_standard_error', 't_stat',
              'formation_count', 'positive_share', 'coefficient_std', 'median_r_squared',
              'hac_maxlags', 'ci95_low', 'ci95_high')
COVER_COUNT = ('input_rows', 'feature_complete_rows', 'common_rows', 'common_return_rows',
              'common_missing_return_rows', 'dropped_rows', 'missing_log_total_mv',
              'missing_turnover_lagged_mean_60d', 'missing_illiquidity_20d_raw',
              'missing_activity_20d_raw', 'missing_forward_return')
COVER_META = ('input_formations', 'common_support_formations', 'common_start', 'common_end',
              'cell_count', 'expected_cell_count', 'missing_return_cells', 'empty_assigned_cells',
              'empty_observed_cells', 'assigned_cell_count_min', 'assigned_cell_count_max',
              'observed_cell_count_min', 'observed_cell_count_max')
SOURCE_ROLES = ('retained_features_sha256', 'retained_turnover_sha256', 'retained_eligibility_sha256',
                'trading_calendar_sha256', 'daily_source_file_count',
                'daily_source_content_set_sha256', 'executed_driver_sha256')


def project_size(source):
    if source['causal'] or source['untouched_holdout']:
        raise ValueError('size evidence scope changed')
    universes = {'retained_deconfounding', 'retained_eligible'}
    contrasts = {f'{target}:{mode}' for target in (
        'size_given_illiquidity', 'size_given_activity', 'turnover_given_size') for mode in (
        'conditional', 'unconditional_ordinary', 'unconditional_common',
        'paired_conditional_minus_unconditional')}
    expected = {(universe, contrast) for universe in universes for contrast in contrasts}
    actual = {(row['universe'], row['coefficient']) for row in source['summaries']}
    if len(source['summaries']) != len(expected) or actual != expected:
        raise ValueError('unreviewed size contrasts')
    result = fields(source, SIZE_TOP)
    result['summaries'] = [fields(row, SIZE_STATS) for row in source['summaries']]
    result['coverage'] = {}
    for universe in sorted(universes):
        record = source['coverage'][universe]
        result['coverage'][universe] = {
            **fields(record, COVER_META), 'counts': fields(record['counts'], COVER_COUNT),
            'monthly': [fields(row, ('formation_date', *COVER_COUNT)) for row in record['monthly']]}
    result['source_hashes'] = fields(source['source_hashes'], SOURCE_ROLES)
    finite_tree(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('failure', 'protocol', 'claims', 'size', 'size-output', 'output'):
        parser.add_argument(f'--{name}', type=Path, required=True)
    args = parser.parse_args()
    paths = {key: getattr(args, key) for key in ('failure', 'protocol', 'claims')}
    payload = project(*(json.loads(paths[key].read_text()) for key in ('failure', 'protocol', 'claims')))
    payload['source_sha256'] = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in paths.items()}
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    projected_size = project_size(json.loads(args.size.read_text()))
    projected_size['review_source_sha256'] = hashlib.sha256(args.size.read_bytes()).hexdigest()
    args.size_output.write_text(json.dumps(projected_size, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
