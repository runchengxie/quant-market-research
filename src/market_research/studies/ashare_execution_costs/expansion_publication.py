"""Allowlisted publication of reviewed expansion and strategy aggregates."""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re

import pandas as pd

from market_research.studies.ashare_execution_costs.publication import aggregate, numeric

GROUPS = ('by_day','by_adv_group','by_cap_group','by_volatility_group','by_time_bucket')
BOOK_AUDIT = ('day','sampled_securities','sampled_snapshots','valid_books','excluded_books',
    'one_sided','crossed_or_locked','malformed','selected_source_rows','invalid_clock_rows',
    'duplicate_timestamp_excess','continuous_source_rows','securities','expected_security_minutes',
    'observed_security_minutes','missing_security_minutes','observed_fraction','ratio_between_0_8_and_1_2')
STREAM_AUDIT = ('rows','nonpositive_price_rows','nonpositive_volume_rows','null_clock_rows',
    'duplicate_event_rows','timestamp_regressions','sequence_regressions','duplicate_sequence_rows',
    'nonpositive_sequence_rows','null_sequence_rows','positive_sequence_regressions','duplicate_positive_sequence_rows')
REFERENCE = ('references','matched','unique','ambiguous','missing','match_rate','nonpositive_or_null_reference_rows')
SCENARIOS = ('gross','fee_only','fee_static_10k','fee_static_1m','fee_expanded_100k','fee_expanded_1m')
MODELED = ('capital_cny','anchor_notional_cny','terminal_nav','transaction_cost_cny',
    'negative_cash_sessions','executed_buy_cny','executed_sell_cny','unfilled_buy_cny','unfilled_sell_cny',
    'mean_one_way_turnover','max_one_way_turnover','partially_filled_orders','zero_fill_orders',
    'buy_static_bp','sell_static_bp','buy_reference_full_coverage_rate','sell_reference_full_coverage_rate')
OVERLAYS = ('capital_cny','source_initial_capital_cny','sessions','original_cost_cny','fee_cny',
    'static_cost_cny','mean_one_way_turnover','max_one_way_turnover','anchor_notional_cny',
    'buy_static_bp','sell_static_bp','buy_pilot_full_coverage_rate','sell_pilot_full_coverage_rate',
    'buy_requested_notional_above_anchor_fraction','sell_requested_notional_above_anchor_fraction',
    'executed_buy_cny','executed_sell_cny','unfilled_buy_cny','unfilled_sell_cny',
    *[f'{scenario}_{suffix}' for scenario in ('gross','fee_only','fee_static')
       for suffix in ('terminal_nav','negative_cash_sessions','max_funding_shortfall_cny')])
STRESS = ('capital_cny','sessions','one_way_turnover','daily_cost_fraction','daily_initial_capital_cost_cny',
    'terminal_cost_only_nav','linear_cost_fraction','compounded_cost_fraction','anchor_notional_cny')


def _numbers(value: dict, keys) -> dict:
    return {key:numeric(value[key]) for key in keys if key in value}


def _hash(value):
    if value is not None and (not isinstance(value,str) or not re.fullmatch('[a-f0-9]{64}',value)):
        raise ValueError('expected SHA256 or null')
    return value


def _permission(confirmed_on):
    date.fromisoformat(confirmed_on)
    return {'status':'confirmed_by_owner','confirmed_on':confirmed_on,'scope':'aggregate_derived_statistics'}


def _stream(value: dict):
    out = _numbers(value,STREAM_AUDIT)
    for key in ('sequence_available','channel_available'):
        if key in value:
            if not isinstance(value[key],bool):
                raise ValueError('stream flags must be boolean')
            out['sequence_column_present' if key=='sequence_available' else 'channel_column_present'] = value[key]
    for category in ('OrderType_counts','Side_counts'):
        if category in value:
            out[category] = {str(key):numeric(count) for key,count in value[category].items()
                             if re.fullmatch(r'-?\d+(?:\.0)?|nan',str(key))}
    return out


def _events(value: dict):
    row = {key:_stream(value[key]) for key in ('orders','trades','positive_price_trades','preopening_orders') if key in value}
    row.update(_numbers(value,('preopening_overlap_rows',)))
    row['references'] = []
    for reference in value.get('references',[]):
        if reference.get('candidate') not in ('OrderID','DBOrderID'):
            raise ValueError('unreviewed reference candidate')
        if reference.get('identity_scope') not in ('security_channel','security_only_channel_unavailable'):
            raise ValueError('unreviewed reference scope')
        record = {'candidate':reference['candidate'],'identity_scope':reference['identity_scope'],
            **_numbers(reference,('eligible_positive_trade_rows',))}
        for side in ('buy','sell'):
            record[side] = _numbers(reference.get(side,{}),REFERENCE)
        row['references'].append(record)
    row['dynamic_replay_gate'] = 'not_established_special_event_semantics_and_queue_order_unverified'
    if 'by_market' in value:
        row['by_market'] = {key:_events(market) for key,market in value['by_market'].items()
                            if key in ('shanghai','shenzhen')}
    return row


def public_expansion(private: dict, *, confirmed_on: str) -> dict:
    if private.get('study_id') != 'ashare_execution_costs':
        raise ValueError('unexpected study identity')
    receipts = []
    for row in private.get('inputs',[]):
        if row.get('clock_profile') not in ('relative_0930_ms','native_hhmmssmmm'):
            raise ValueError('unreviewed clock profile')
        receipts.append({'sha256':_hash(row.get('sha256')),'clock_profile':row['clock_profile'],
                         **_numbers(row,('bytes','metadata_rows'))})
    out = {'schema_version':'ashare_execution_costs.expansion.public.v1',
        'study_id':'ashare_execution_costs','evidence':'descriptive_historical_static_expansion',
        'permission':_permission(confirmed_on),
        'measurement_code_sha256':_hash(private.get('measurement_code_sha256')),
        'pilot_code_sha256':_hash(private.get('pilot_code_sha256')),
        'source_inputs':receipts,'daily_input_count':len(private.get('daily_inputs',[])),
        'audit':[_numbers(row,BOOK_AUDIT) for row in private.get('audit',[])],
        'pooled':aggregate(private.get('pooled',{})),
        'covariate_missing':_numbers(private.get('covariate_missing',{}),('adv20_cny','market_cap_cny','volatility20'))}
    allowed_groups = {'by_day':None,'by_adv_group':('low','middle','high','unavailable'),
        'by_cap_group':('low','middle','high','unavailable'),
        'by_volatility_group':('low','middle','high','unavailable'),
        'by_time_bucket':('opening','late_morning','early_afternoon','late_afternoon')}
    for category in GROUPS:
        out[category] = {key:aggregate(value) for key,value in private.get(category,{}).items()
            if (re.fullmatch(r'\d{8}',key) if category=='by_day' else key in allowed_groups[category])}
    comparison = private.get('comparison',{})
    out['comparison'] = _numbers(comparison,('common_securities','paired_valid_security_minutes'))
    out['comparison']['days'] = [numeric(day) for day in comparison.get('days',[])]
    out['comparison']['minute_coverage'] = {key:_numbers(row,('securities','expected_security_minutes',
        'observed_security_minutes','missing_security_minutes','observed_fraction'))
        for key,row in comparison.get('minute_coverage',{}).items() if re.fullmatch(r'\d{8}',key)}
    for category in ('common_security_results','paired_results'):
        out['comparison'][category] = {key:aggregate(value) for key,value in comparison.get(category,{}).items()
                                      if re.fullmatch(r'\d{8}',key)}
    out['event_audit'] = {}
    for day,value in private.get('event_audit',{}).items():
        if not re.fullmatch(r'\d{8}',day):
            continue
        out['event_audit'][day] = _events(value)
    if 'review' in private:
        out['review'] = {key:_hash(private['review'].get(key)) for key in ('source_summary_sha256','review_code_sha256')}
    out['covariate_audit'] = [{key:row[key] for key in ('day','history_start','history_end','required_prior_sessions') if key in row}
                             for row in private.get('covariate_audit',[])]
    for row in out['covariate_audit']:
        for key in ('history_start','history_end'):
            if key in row and not re.fullmatch(r'\d{8}',str(row[key])):
                raise ValueError('unreviewed covariate date')
    out['definitions'] = {
        'price_unit':'CNY','quantity_unit':'share','benchmark':'contemporaneous_midpoint',
        'reference_notional':'midpoint_times_target_shares_fractional_shares_allowed',
        'sampling':'stocklike_prefixes_security_modulus_earliest_minute_before_book_validation',
        'security_modulus':int(private.get('spec',{}).get('security_modulus',37)),
        'minute_denominator':'237_continuous_minutes_per_security_observed_on_declared_day',
        'covariates':'20_prior_daily_sessions_ADV_and_log_return_volatility_previous_session_circulating_market_cap',
        'covariate_groups':'terciles_of_available_prior_daily_cross_section_including_Beijing_no_PIT_status_filter',
        'historical_release_times_verified':False,
        'uncertainty':'selected_sample_quantiles_not_population_confidence_intervals',
        'zero_price_event_semantics_verified':False,'order_reference_match_proves_replay':False,
        'sequence_flags':'field_presence_not_authenticated_ordering',
        'fees_included':False,'dynamic_impact_calibrated':False,'actual_order_calibrated':False}
    return out


def public_strategy(modeled: list, overlays: list, stress: list, receipt: dict, *, confirmed_on: str) -> dict:
    records = []
    for row in modeled:
        if row.get('scenario') not in SCENARIOS:
            raise ValueError('unreviewed strategy scenario')
        records.append({'scenario':row['scenario'],**_numbers(row,MODELED)})
    configuration = receipt.get('simulator_configuration',{})
    config = _numbers(configuration,('participation_rate','liquidity_notional_multiplier','buy_max_days','sell_max_days'))
    for key in ('enforce_t1','enforce_price_limits','enforce_round_lots'):
        if key in configuration:
            if not isinstance(configuration[key],bool):
                raise ValueError('configuration flag must be boolean')
            config[key] = configuration[key]
    period = receipt.get('source_period',[])
    if any(not re.fullmatch(r'\d{8}',str(day)) for day in period):
        raise ValueError('unreviewed source period')
    out = {'schema_version':'ashare_execution_costs.strategy.public.v1',
        'study_id':'ashare_execution_costs','evidence':'diagnostic_modeled_execution_cost_sensitivity',
        'permission':_permission(confirmed_on),'source_period':period,'configuration':config,
        'modeled':records,'overlays':[_numbers(row,OVERLAYS) for row in overlays],
        'stress':[_numbers(row,STRESS) for row in stress],
        'source_sha256':{key:_hash(value) for key,value in receipt.get('source_sha256',{}).items()
                         if key in ('daily_ledger','fills','orders','performance','positions')},
        'pilot_sha256':_hash(receipt.get('pilot_sha256')),
        'original_reference_replay_max_nav_error_cny':numeric(receipt.get('original_reference_replay_max_nav_error_cny')),
        'definitions':{'initial_capitals_cny':[10000000,100000000,1000000000],
            'modeled_engine':'quant_platform_shared_execution_simulator',
            'prices':'daily_adjusted_close_proxy','volume':'daily_amount_5pct_participation_proxy',
            'shares':'fractional_model_no_round_lot_enforcement',
            'original_cost_replaced_bp':5,'commission_assumption_bp_per_side':1,'seller_stamp_bp':5,
            'minimum_commission_cny':0,'static_anchors':'three_day_2026_baseline_and_ten_day_2021_2025_2026_conditional_P50',
            'frozen_path':'replace_debits_on_fixed_fills_negative_cash_is_funding_shortfall',
            'unfilled_notional':'sum_of_unfilled_order_records_not_terminal_backlog',
            'stress':'250_sessions_60pct_each_side_cost_only_no_market_return',
            'corporate_actions_and_release_times_verified':False,'dynamic_impact_calibrated':False,
            'actual_order_calibrated':False,'verified_net_alpha':False}}
    records.sort(key=lambda row:(row.get('capital_cny',0),SCENARIOS.index(row['scenario'])))
    if 'expanded_receipt' in receipt:
        extra = receipt['expanded_receipt']
        out['expanded_reference_sha256'] = _hash(extra.get('static_reference_sha256'))
        dates = [str(day) for day in extra.get('static_reference_dates',[])]
        if any(not re.fullmatch(r'\d{8}',day) for day in dates):
            raise ValueError('unreviewed static reference dates')
        out['expanded_reference_dates'] = dates
        out['engine_modules_sha256'] = {key:_hash(value) for key,value in extra.get('engine_modules_sha256',{}).items()
                                       if re.fullmatch(r'[A-Za-z0-9_]+\.py',key)}
        out['fee_model_module_sha256'] = _hash(extra.get('fee_model_module_sha256'))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--l2-summary',type=Path)
    parser.add_argument('--strategy-root',type=Path)
    parser.add_argument('--strategy-extra-root',type=Path)
    parser.add_argument('--confirmed-on',required=True)
    parser.add_argument('--output-root',type=Path,required=True)
    args = parser.parse_args()
    args.output_root.mkdir(parents=True,exist_ok=True)
    if args.l2_summary:
        private = json.loads(args.l2_summary.read_text())
        public = public_expansion(private,confirmed_on=args.confirmed_on)
        public['source_summary_sha256'] = hashlib.sha256(args.l2_summary.read_bytes()).hexdigest()
        (args.output_root/'expansion.json').write_text(json.dumps(public,indent=2,allow_nan=False)+'\n')
    if args.strategy_root:
        root = args.strategy_root
        frames = [pd.read_csv(root/name).to_dict('records') for name in
                  ('modeled-summary.csv','overlay-summary.csv','turnover-stress.csv')]
        receipt = json.loads((root/'receipt.json').read_text())
        if args.strategy_extra_root:
            extra = args.strategy_extra_root
            frames[0].extend(pd.read_csv(extra/'modeled-summary.csv').to_dict('records'))
            receipt['expanded_receipt'] = json.loads((extra/'receipt.json').read_text())
        public = public_strategy(*frames,receipt,confirmed_on=args.confirmed_on)
        public['source_receipt_sha256'] = hashlib.sha256((root/'receipt.json').read_bytes()).hexdigest()
        (args.output_root/'strategy.json').write_text(json.dumps(public,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
