import json

import pytest

from market_research.studies.ashare_execution_costs.publication import public_pilot


def test_export_is_an_explicit_aggregate_allowlist():
    private = {'study_id':'ashare_execution_costs','measurement_code_sha256':'abc',
               'inputs':[{'path':'/private/source','day':20260424,'sha256':'input','bytes':100}],
               'spec':{'path':'/private/config'},'audit':[{'day':20260424,'rows_read':100,
                 'sampled_securities':1,'sampled_snapshots':10,'valid_books':9,
                 'excluded_books':1,'one_sided':1,'day_mismatch':0}],
               'pooled':{'snapshots':9,'security_days':1,'spread_bp':{'count':9,'p50':2},
                         'private_security_records':[{'SecuCode':1}]},
               'by_day':{},'by_depth_group':{}}
    result = public_pilot(private,confirmed_on='2026-10-12')
    encoded=json.dumps(result)
    assert '/private/' not in encoded
    assert 'SecuCode' not in encoded
    assert 'private_security_records' not in encoded
    assert result['pooled']['spread_bp']['p50']==2
    assert result['permission']['status']=='confirmed_by_owner'
    assert result['source_inputs'][0]['sha256']=='input'


def test_permission_date_and_identity_must_be_explicit():
    with pytest.raises(ValueError):
        public_pilot({'study_id':'other'},confirmed_on='2026-10-12')
    with pytest.raises(ValueError):
        public_pilot({'study_id':'ashare_execution_costs'},confirmed_on='not-a-date')
