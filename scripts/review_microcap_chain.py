"""Project reviewed follow-up counts; never publish held-event identities."""

import argparse
import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit


def require(condition, message='Evidence changed; independent review required'):
    if not condition:
        raise ValueError(message)


def numeric(value):
    require(isinstance(value, str))
    result = Decimal(value)
    require(result.is_finite() and result >= 0)
    return result


def date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()


def project_primary(source):
    require(source['schema'] == 'private-held-event-primary-terms/v1')
    rows = source['events']
    require(len(rows) == 7 and len({r['event_id'] for r in rows}) == 7
            and len({r['symbol'] for r in rows}) == 7)
    for row in rows:
        require(row['holder_account_and_integer_raw_inventory_certified'] is False
                and row['tax_certified'] is False)
        require(numeric(row['capitalization_new_shares_per_raw_share']) > 0)
        if row['cash_per_raw_share_gross_rmb'] is not None:
            numeric(row['cash_per_raw_share_gross_rmb'])
        require(date(row['record_date']) < date(row['ex_date'])
                <= date(row['unrestricted_new_share_listing_date']))
        require(re.fullmatch('[0-9a-f]{64}', row['source_sha256']) is not None)
        url = urlsplit(row['primary_url'])
        require(url.scheme == 'https' and url.hostname in {
            'static.cninfo.com.cn', 'disc.static.szse.cn'})
    result = {'reviewed_held_events': 7, 'primary_notices': 7,
              'explicit_fraction_methods': sum(r['fraction_allocation']['status'] == 'explicit'
                                               for r in rows),
              'listing_after_ex': sum(date(r['unrestricted_new_share_listing_date'])
                                     > date(r['ex_date']) for r in rows),
              'cash_numeric_unspecified': sum(r['cash_per_raw_share_gross_rmb'] is None
                                              for r in rows),
              'holder_inventory_certified': False, 'tax_certified': False}
    require((result['explicit_fraction_methods'], result['listing_after_ex'],
             result['cash_numeric_unspecified']) == (6, 1, 3))
    return result


def project_trace(source):
    require(source['schema'] == 'microcap-unknown-inventory-trace/v1'
            and source['consumed_inputs_unchanged'] is True)
    rows = source['events']
    require(len(rows) == 6)
    for row in rows:
        require(row['retained_dated_inventory_classification'] == 'unknown'
                and row['original_inventory_recovered'] is False
                and row['raw_share_entitlement_identified'] is False
                and row['candidate_source_derived_classification'] ==
                'absent_under_explicit_pre_activation_cash_contract')
    convention = source['original_convention']
    require(convention['pre_first_entry_dated_account_rows_retained'] is False
            and convention['leading_return_padding_rows'] == 63)
    engine = source['original_engine_hash_checks']
    require(len(engine) == 19 and all(r['matches_original_receipt'] is True for r in engine))
    require(len(source['retained_output_coverage']) == 38)
    require(source['min45_remedy_feasibility']['old_fills_or_inventory_recovered'] is False)
    positive = sum(any(r['latest_target_weight'] > 0 for r in e['target_history']['45'])
                   for e in rows)
    require(positive == 1)
    return {'dated_inventory_unknown': 6, 'derived_pre_activation_cash_absence': 6,
            'original_inventory_recovered': False, 'leading_cash_sessions': 63,
            'matched_original_engine_files': 19, 'retained_account_files_checked': 38,
            'min45_positive_prior_target_events': positive, 'min45_fills_recovered': False}


def project_prospective(source):
    require(source['kind'] == 'manual_read_only_verification_not_market_observation')
    require(all(source[k] is True for k in ('anchor_verified', 'register_all_files_unchanged',
                                           'no_append', 'no_alias_change', 'no_job_installed')))
    require(source['pending_transaction'] is False and source['register_entries'] == 2
            and source['anchor_sequence'] == 2)
    require(re.fullmatch('[0-9a-f]{64}', source['register_head']) is not None)
    summary = source['summary']
    require(summary['issue_count'] == 7 and summary['admitted'] is False
            and summary['new_cohort_completed_windows'] == 0
            and summary['status'] == 'pending_before_cutoff')
    clock = datetime.fromisoformat(source['actual_review_utc'])
    require(clock.tzinfo is not None and clock.utcoffset().total_seconds() == 0)
    require(source['production']['readiness_cli_exists'] is False)
    return {'kind': 'manual_verification', 'actual_review_utc': source['actual_review_utc'],
            'register_entries': 2, 'anchored_head': source['register_head'],
            'register_unchanged': True, 'pending_categories': 7, 'admitted': False,
            'new_completed_windows': 0, 'scheduler_installed': False,
            'stable_release_has_register_cli': False}


def project_slice(source):
    require(source['schema'] == 'microcap-frozen-target-raw-account/v1'
            and source['status'] == 'account_reconciliation_failed'
            and source['fail_closed'] is True
            and source['source_checks_unchanged'] is True
            and source['engine_source_checks_unchanged'] is True)
    require(source['failure'].startswith(
        'AssertionError: fill violates 100-share lot/full-liquidation assumption:'))
    require(set(source['outputs_sha256']) == {
        'all_cached_query_rows.parquet', 'executed_audit.py', 'original_terms.json',
        'raw_inputs.parquet', 'targets.parquet', 'uncertified_candidate_actions.parquet',
        'uncertified_candidate_fills.parquet', 'uncertified_candidate_orders.parquet'})
    preflight = source['preflight']
    targets = source['target_count_per_formation']
    require(len(targets) == 2 and set(targets.values()) == {40}
            and source['action_query_covered_symbols'] == 46
            and (preflight['sessions'], preflight['symbols'], preflight['query_rows_scanned'])
            == (21, 46, 2230)
            and len(preflight['included_events']) == len(preflight['excluded_events']) == 1)
    return {'status': 'blocked_by_sell_quantity_contract', 'fail_closed': True,
            'accepted_nav': False, 'formations': 2, 'targets_per_formation': 40,
            'distinct_target_names': 46, 'sessions': 21, 'query_rows_scanned': 2230,
            'included_actions': 1, 'excluded_pre_entry_actions': 1,
            'historical_account_recovered': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('primary', 'trace', 'prospective', 'slice', 'output'):
        parser.add_argument('--' + key, type=Path, required=True)
    args = parser.parse_args()
    paths = {key: getattr(args, key) for key in ('primary', 'trace', 'prospective', 'slice')}
    raw = {key: path.read_bytes() for key, path in paths.items()}
    result = {'schema_version': 1, 'reviewed_on': '2026-10-18',
              'raw_share_strategy_ready': False,
              'primary': project_primary(json.loads(raw['primary'])),
              'trace': project_trace(json.loads(raw['trace'])),
              'prospective': project_prospective(json.loads(raw['prospective'])),
              'target_slice': project_slice(json.loads(raw['slice'])),
              'source_sha256': {key: hashlib.sha256(value).hexdigest()
                                for key, value in raw.items()}}
    require(all(path.read_bytes() == raw[key] for key, path in paths.items()),
            'Input changed during projection')
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
