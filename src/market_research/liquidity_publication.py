"""Validate a reviewed liquidity aggregate against its receipt and public schema."""
from __future__ import annotations

import hashlib
import json
import math
import re

from .liquidity_rebuild import BUCKET_LABELS

TOP = {'schema_version','generated_on','method','markets','periods','source_profiles','source_receipts','code_receipts','caveats'}
METHOD = {'roll_days','metric','currency','source_project','snapshot_note','market_cap_anchor','feature_lag_sessions','minimum_session_stocks','calendar_method','fx_method','zero_and_missing','historical_pit_eligible'}
MARKET = {'market','status','aggregation','as_of','coverage_start','coverage_end','unique_stocks','eligible_observations','below_100m_observations','fx_start','fx_end','buckets','eligible_stocks','sub_100m_count','sub_100m_median_usd'}
BUCKET = {'label','observations','count','median_usd','mean_usd','p90_usd','median20_median_usd','median20_mean_usd','median20_p90_usd'}
PERIOD = {'requested_start','requested_end','included_markets','missing_markets','common_start','common_end','common_dates','markets','period','status'}
PROFILE = {'source_rows','observed_stocks','coverage_start','coverage_end','eligible_observations','exclusions','duplicate_keys'}
RECEIPT = {'source_id','files','bytes','sha256'}
REASONS = {'included','insufficient_history','missing_market_sessions','missing_turnover','prior_source_ineligible','missing_prior_cap','missing_or_stale_fx','numeric_overflow','sparse_non_market_date'}


def _fields(value: dict, allowed: set[str]):
    unexpected = set(value)-allowed
    if unexpected:
        raise ValueError(f'nonpublic or unknown fields: {sorted(unexpected)}')


def _safe(value):
    if isinstance(value,str) and re.search(r'/home/|/Users/|/mnt/|[A-Za-z]:\\|TOKEN=|API_KEY=',value):
        raise ValueError('private path or credential marker in public aggregate')
    if isinstance(value,float) and not math.isfinite(value):
        raise ValueError('nonfinite public number')
    if isinstance(value,dict):
        for key,item in value.items():
            _safe(key)
            _safe(item)
    elif isinstance(value,list):
        for item in value:
            _safe(item)


def _market(item):
    _fields(item,MARKET)
    buckets=item['buckets']
    if [b['label'] for b in buckets] != list(BUCKET_LABELS):
        raise ValueError('incorrect bucket definitions')
    for bucket in buckets:
        _fields(bucket,BUCKET)
        if not isinstance(bucket['observations'],int) or bucket['observations']<0:
            raise ValueError('invalid bucket observations')
        if not isinstance(bucket['count'],int) or not 0<=bucket['count']<=bucket['observations']:
            raise ValueError('invalid stock count')
        values=[bucket[key] for key in BUCKET-{'label','observations','count'}]
        if bucket['observations']==0 and any(v is not None for v in values):
            raise ValueError('empty buckets must have null statistics')
        if bucket['observations'] and any(v is None or v<0 for v in values):
            raise ValueError('populated buckets require finite nonnegative statistics')
    if sum(b['observations'] for b in buckets)!=item['eligible_observations']:
        raise ValueError('bucket observations do not reconcile')
    if sum(b['observations'] for b in buckets[:2])!=item['below_100m_observations']:
        raise ValueError('below-100m observations do not reconcile')
    if item['aggregation']=='snapshot':
        if sum(b['count'] for b in buckets)!=item['eligible_stocks']:
            raise ValueError('snapshot stock counts do not reconcile')
        if sum(b['count'] for b in buckets[:2])!=item['sub_100m_count']:
            raise ValueError('snapshot below-100m counts do not reconcile')
    elif item['aggregation']!='security_day':
        raise ValueError('unknown aggregate grain')


def reviewed_publication(raw: bytes, review: dict) -> dict:
    if hashlib.sha256(raw).hexdigest()!=review.get('reviewed_summary_sha256'):
        raise ValueError('independent review checksum does not match proposal')
    if not (review.get('aggregate_cells_reconciled',0)>0 and review.get('count_and_reason_conservation') is True and review.get('strict_prior_fx_checked') is True):
        raise ValueError('independent aggregate checks are incomplete')
    summary=json.loads(raw)
    _safe(summary)
    _fields(summary,TOP)
    if summary['schema_version']!='liquidity.rebuilt.v1':
        raise ValueError('unsupported public liquidity schema')
    _fields(summary['method'],METHOD)
    if summary['method']['roll_days']!=20 or summary['method']['historical_pit_eligible'] is not False:
        raise ValueError('invalid rolling/PIT evidence declaration')
    for item in summary['markets']:
        _market(item)
    for period in summary['periods']:
        _fields(period,PERIOD)
        if set(period['included_markets'])!={m['market'] for m in period['markets']}:
            raise ValueError('period market coverage does not reconcile')
        for item in period['markets']:
            _market(item)
            if item['coverage_start']!=period['common_start'] or item['coverage_end']!=period['common_end']:
                raise ValueError('markets are not on a common period')
    for profile in summary['source_profiles'].values():
        _fields(profile,PROFILE)
        _fields(profile['exclusions'],REASONS)
        if sum(profile['exclusions'].values())!=profile['source_rows'] or profile['duplicate_keys']!=0:
            raise ValueError('source exclusion ledger does not reconcile')
    for receipt in summary['source_receipts']:
        _fields(receipt,RECEIPT)
        if not re.fullmatch('[0-9a-f]{64}',receipt['sha256']):
            raise ValueError('invalid source checksum')
    return summary
