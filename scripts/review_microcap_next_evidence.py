"""Project reviewed microcap follow-up aggregates without private source locators."""
import argparse
import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path

READINESS_ISSUES = {
    'benchmark', 'calendar', 'capitalization_valuation', 'industry_membership',
    'prices_adjustments', 'signal', 'turnover_amounts', 'universe_status',
}


def project_readiness(source, *, initial=False):
    if source['status'] != 'pending_before_cutoff':
        raise ValueError('readiness status changed; new review required')
    if source['admitted'] is not False or source['new_cohort_completed_windows'] != 0:
        raise ValueError('prospective admission changed; new review required')
    expected = READINESS_ISSUES if initial else READINESS_ISSUES - {'calendar'}
    if (set(source['issue_categories']) != expected
            or len(source['issue_categories']) != len(expected)
            or source['issue_count'] != len(expected)):
        raise ValueError('readiness scope changed; new review required')
    if (source['protocol_id'] != 'microcap-prospective-20261017/v1'
            or source['formation'] != '2026-10-30'):
        raise ValueError('prospective protocol changed; new review required')
    stamp = source['as_of_utc']
    if not isinstance(stamp, str) or not re.fullmatch(
            r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:[.][0-9]+)?[+]00:00', stamp):
        raise ValueError('invalid readiness timestamp')
    datetime.fromisoformat(stamp)
    return {key: source[key] for key in (
        'protocol_id', 'formation', 'status', 'issue_count', 'issue_categories',
        'new_cohort_completed_windows', 'admitted', 'as_of_utc')}


EVENT_COUNTS = (
    'dated_unique_blockers', 'unknown_exdate_rows',
    'retrospective_economic_adjudications', 'dated_unresolved',
    'ordinary_share_ledger_examples', 'no_original_holder_ledger_examples',
    'cash_ledger_examples', 'period_metadata_still_unresolved_in_reviewed_cases',
    'differential_holder_cash_examples', 'holder_classification_required_in_reviewed_cases',
)
PRIORITIES = (
    'announcement_or_period_conflict', 'economic_conflict',
    'missing_amount_requires_primary_notice', 'settlement_or_unknown_date',
)


def project_events(source):
    if (source['schema_version'] != 'microcap-event-adjudication.v1'
            or source['raw_share_ready'] is not False
            or source['owner_resolver_recomputed'] is not False
            or source['owner_blocker_inventory_unchanged'] is not True):
        raise ValueError('event readiness changed; new review required')
    result = {key: source[key] for key in EVENT_COUNTS}
    result['plan_blockers'] = {key: source['plan_blockers'][key] for key in ('45', '90')}
    result['priority_counts'] = {key: source['priority_counts'][key] for key in PRIORITIES}
    counts = [result[key] for key in EVENT_COUNTS]
    counts += list(result['plan_blockers'].values()) + list(result['priority_counts'].values())
    if any(type(value) is not int or value < 0 for value in counts):
        raise ValueError('invalid event count')
    if (sum(result['priority_counts'].values()) != result['dated_unique_blockers']
            or result['dated_unresolved'] + result['retrospective_economic_adjudications']
            != result['dated_unique_blockers']):
        raise ValueError('event inventory does not reconcile')
    result.update(raw_share_ready=False, owner_resolver_recomputed=False,
                  owner_blocker_inventory_unchanged=True)
    return result


CASE_IDS = (
    'unrestricted_ordinary_capitalization',
    'restructuring_no_original_holder_entitlement',
    'gross_ordinary_cash_distribution',
    'differential_cash_requires_holder_classification',
)
CASE_SOURCES = {
    'unrestricted_ordinary_capitalization': (
        'https://epaper.stcn.com/pic/202406/26/8f7dd3652e682ceb00f5b19695fd561d.pdf',
        '47eb6c36a2a4b460df07f2b032104c399b1bbc3d57d002ba2d61d1b0c2a39507'),
    'restructuring_no_original_holder_entitlement': (
        'https://static.cninfo.com.cn/finalpage/2025-12-30/1224906744.PDF',
        '102db0e2d61978c54af65ea9fb3d7689a21048d4d77823d692a9fcd47ec9df86'),
    'gross_ordinary_cash_distribution': (
        'https://disc.static.szse.cn/disc/disk03/finalpage/2025-01-17/9d039b93-fbaf-4777-b017-05a28821c285.PDF',
        '78549e6908050e9fde1e5f9a07220032b64ad617dc222157413eeda6838a2301'),
    'differential_cash_requires_holder_classification': (
        'https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2024-07-18/600989_20240718_2K7K.pdf',
        'd47db5c0b7d2c9bfc37dbc71cfdd2e34ed299948baaad08e7fadedb6fa2dde86'),
}
SNAPSHOT_FIELDS = (
    'cash', 'cash_receivable', 'settled_shares', 'share_receivable',
    'action_settlement_eligible_shares', 'mark', 'nav',
)


def public_number(value):
    if not isinstance(value, (str, int)) or isinstance(value, bool):
        raise ValueError('invalid case number')
    encoded = str(value)
    if not re.fullmatch(r'[0-9]+(?:[.][0-9]+)?', encoded):
        raise ValueError('invalid case number')
    return encoded


def public_date(value):
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{8}', value):
        raise ValueError('invalid case date')
    return datetime.strptime(value, '%Y%m%d').strftime('%Y-%m-%d')


def project_snapshot(row):
    if row['executable_sellable_shares'] is not None or Decimal(str(row['mark'])) != 1:
        raise ValueError('case execution or valuation scope changed; new review required')
    result = {key: public_number(row[key]) for key in SNAPSHOT_FIELDS}
    result.update(date=public_date(row['date']), executable_sellable_shares=None)
    nav = sum(Decimal(result[key]) for key in (
        'cash', 'cash_receivable', 'settled_shares', 'share_receivable'))
    if nav != Decimal(result['nav']):
        raise ValueError('unit valuation does not reconcile')
    return result


def project_cases(cases, primary):
    if [row['case'] for row in cases] != list(CASE_IDS):
        raise ValueError('case scope changed; new review required')
    result = []
    for row in cases:
        evidence = row['evidence']
        url, digest = CASE_SOURCES[row['case']]
        if (evidence['source_url'], evidence['source_pdf_sha256']) != (url, digest):
            raise ValueError('case primary source changed; new review required')
        if not any(item['source_url'] == url and item['source_pdf_sha256'] == digest for item in primary):
            raise ValueError('primary notice binding missing')
        if row['assumed_record_shares'] != 1000 or Decimal(str(row['opening_cash'])) != 0:
            raise ValueError('assumed inventory changed; new review required')
        projected = {
            'case': row['case'], 'assumed_record_shares': 1000, 'opening_cash': '0',
            'source_url': url, 'source_pdf_sha256': digest,
            'dates': {key: public_date(evidence.get(key)) for key in (
                'source_announcement_date', 'record_date', 'ex_date', 'pay_date', 'stock_listing_date')},
            'stock_per_share': public_number(evidence['stock_per_share']),
        }
        if 'cash_per_share' in evidence:
            projected['cash_per_share'] = public_number(evidence['cash_per_share'])
        if 'holder_rates' in evidence:
            projected['holder_rates'] = {key: public_number(evidence['holder_rates'][key])
                                         for key in ('minority', 'named_large_holder')}
            projected['reference_price_deduction'] = public_number(evidence['reference_price_deduction'])
        if 'snapshots' in row:
            projected['snapshots'] = [project_snapshot(point) for point in row['snapshots']]
        else:
            projected['snapshots_by_assumed_holder_class'] = {
                key: [project_snapshot(point) for point in row['snapshots_by_assumed_holder_class'][key]]
                for key in ('minority', 'named_large_holder')}
        if 'exdate_pre_settlement' in row:
            projected['exdate_pre_settlement'] = {key: public_number(row['exdate_pre_settlement'][key])
                                                 for key in ('cash', 'cash_receivable', 'settled_shares', 'share_receivable')}
        result.append(projected)
    return result


CALENDAR_URLS = {
    'annual': 'https://www.sse.com.cn/disclosure/announcement/general/c/c_20251222_10802507.shtml',
    'national_holiday': 'https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/announcement/general/c/c_20260915_10832273.shtml',
}


def project_calendar(source):
    expected = {
        'schema_version': 1, 'status': 'official_published_schedule_crosschecked',
        'civil_days': 61, 'october_open_sessions': 17, 'november_open_sessions': 21,
        'vendor_calendar_mismatches': 0, 'formation': '2026-10-30',
        'entry': '2026-11-02', 'holding_end': '2026-11-30',
        'review_cutoff_utc': '2026-11-02T00:30:00+00:00',
    }
    if any(source[key] != value or type(source[key]) is not type(value)
           for key, value in expected.items()):
        raise ValueError('official schedule changed; new review required')
    if [item['role'] for item in source['sources']] != list(CALENDAR_URLS):
        raise ValueError('official source scope changed; new review required')
    sources = []
    for item in source['sources']:
        if (item['url'] != CALENDAR_URLS[item['role']]
                or not re.fullmatch(r'[a-f0-9]{64}', item['sha256'])
                or type(item['bytes']) is not int or item['bytes'] <= 0):
            raise ValueError('invalid official source binding')
        if datetime.fromisoformat(item['retrieved_utc']).utcoffset() is None:
            raise ValueError('official retrieval timestamp needs timezone')
        sources.append({key: item[key] for key in ('role', 'url', 'sha256', 'bytes', 'retrieved_utc')})
    return {**expected, 'sources': sources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--readiness', type=Path, required=True)
    parser.add_argument('--initial-readiness', type=Path, required=True)
    parser.add_argument('--calendar', type=Path, required=True)
    parser.add_argument('--events', type=Path, required=True)
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--primary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.readiness.read_bytes()
    event_raw = args.events.read_bytes()
    case_raw = args.cases.read_bytes()
    primary_raw = args.primary.read_bytes()
    initial_raw = args.initial_readiness.read_bytes()
    calendar_raw = args.calendar.read_bytes()
    payload = {
        'schema_version': 1, 'reviewed_on': '2026-10-18',
        'raw_share_ready': False, 'original_runtime_recovered': False,
        'readiness': project_readiness(json.loads(raw)),
        'initial_readiness': project_readiness(json.loads(initial_raw), initial=True),
        'calendar': project_calendar(json.loads(calendar_raw)),
        'events': project_events(json.loads(event_raw)),
        'cases': project_cases(json.loads(case_raw), json.loads(primary_raw)),
        'source_sha256': {'readiness_summary': hashlib.sha256(raw).hexdigest(),
                          'events_summary': hashlib.sha256(event_raw).hexdigest(),
                          'case_ledgers': hashlib.sha256(case_raw).hexdigest(),
                          'primary_evidence': hashlib.sha256(primary_raw).hexdigest(),
                          'initial_readiness': hashlib.sha256(initial_raw).hexdigest(),
                          'official_calendar': hashlib.sha256(calendar_raw).hexdigest()},
    }
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
