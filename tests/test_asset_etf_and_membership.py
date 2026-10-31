import numpy as np
import pandas as pd
import pytest
from market_research.studies.asset_returns.etf import etf_gap
from market_research.studies.asset_returns.constituents import constituent_retention


def test_etf_three_layer_identity_retains_distribution_basis_residual():
    f=pd.DataFrame({'date':pd.date_range('2024-12-31',periods=13,freq='ME'),
        'index_total':np.linspace(100,110,13),'unit_nav':np.linspace(1,1.05,13),
        'adj_nav':np.linspace(1,1.08,13),'close':np.linspace(1,1.06,13),
        'adj_factor':np.linspace(1,1.03,13)})
    r=etf_gap(f)
    assert r['nav_cagr']==pytest.approx(.08)
    assert r['market_total_proxy_cagr']==pytest.approx(1.06*1.03-1)
    assert r['geometric_reconciliation_error']==pytest.approx(0,abs=1e-12)
    assert r['distribution_basis_wealth_ratio']!=pytest.approx(1)
    assert r['manager_fees_subtracted_again'] is False
    with pytest.raises(ValueError):
        etf_gap(f.assign(adj_nav=np.nan))


def test_membership_retains_exits_and_distinguishes_weight_drift():
    f=pd.DataFrame({'date':['2020-12-31']*2+['2021-12-31']*2,
                    'symbol':['A','B','B','C'],'weight':[.6,.4,.3,.7]})
    r=constituent_retention(f,expected_count=2)
    assert r['cohort_retained_count']==1
    assert r['cohort_retained_fraction']==.5
    assert r['retained_initial_weight']==.4
    assert r['transitions'][0]['entries']==1
    assert r['transitions'][0]['exits']==1
    assert r['transitions'][0]['weight_distance']==pytest.approx(.7)
    assert r['measured_turnover'] is False
    with pytest.raises(ValueError):
        constituent_retention(f.assign(weight=.1),expected_count=2)
    with pytest.raises(ValueError):
        constituent_retention(f.iloc[:-1],expected_count=2)


def test_profit_bridge_does_not_call_membership_change_company_growth():
    from market_research.studies.asset_returns.constituents import profit_bridge
    f=pd.DataFrame({'symbol':['A','B','C'],'opening_profit':[10,90,np.nan],
                    'closing_profit':[10,90,190], 'opening_member':[True,True,False],
                    'closing_member':[True,False,True]})
    r=profit_bridge(f)
    assert r['dynamic_profit_change']==100
    assert r['incumbent_profit_change']==0
    assert r['net_membership_change']==100
    assert r['fixed_initial_cohort_profit_change']==0
    assert r['per_share_index_attribution'] is False
    with pytest.raises(ValueError):
        profit_bridge(f.assign(closing_profit=[10,np.nan,190]))
