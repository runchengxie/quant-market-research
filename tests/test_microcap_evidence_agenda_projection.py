import copy
import json
from pathlib import Path

import pytest

from scripts.review_microcap_evidence_agenda import project, project_size


def test_public_projection_excludes_private_locators_and_requires_review_of_future_state():
    data=json.loads(Path('web/public/data/microcap_evidence_agenda.json').read_text())
    failure=copy.deepcopy(data['failure_atlas'])
    failure['private_path']='/private/source'
    for curve in failure['curves'].values():
        for row in curve:
            row['symbol']='PRIVATE'
    protocol=copy.deepcopy(data['prospective'])
    claims={'claims':data['claims'],'next_scheduled_review':data['next_manual_claim_review']}
    result=project(failure,protocol,claims)
    encoded=json.dumps(result)
    assert '/private/' not in encoded
    assert 'PRIVATE' not in encoded
    assert result['prospective']['new_cohort_completed_windows']==0
    assert len(result['claims'])==6
    protocol['new_cohort_completed_windows']=1
    with pytest.raises(ValueError,match='review required'):
        project(failure,protocol,claims)


def test_nonfinite_curve_cannot_be_published():
    data=json.loads(Path('web/public/data/microcap_evidence_agenda.json').read_text())
    data['failure_atlas']['curves']['ideal_one_day'][0]['nav']=float('nan')
    with pytest.raises(ValueError,match='nonfinite'):
        project(data['failure_atlas'],data['prospective'],{'claims':data['claims'],'next_scheduled_review':data['next_manual_claim_review']})


def test_duplicate_known_contrasts_cannot_replace_missing_pairs():
    data=json.loads(Path('web/public/data/microcap_size_liquidity_review.json').read_text())
    data['summaries']=[data['summaries'][0]]*24
    with pytest.raises(ValueError,match='unreviewed size contrasts'):
        project_size(data)


def test_missing_effect_cannot_be_formatted_as_zero():
    data=json.loads(Path('web/public/data/microcap_size_liquidity_review.json').read_text())
    data['summaries'][0]['coefficient_mean']=None
    with pytest.raises(ValueError,match='missing public effect estimate'):
        project_size(data)
