import pandas as pd
import pytest
from market_research.studies.asset_returns.allocation import compare_allocation


def levels(a,b):
    return pd.DataFrame({'date':pd.date_range('2019-12-31',periods=len(a),freq='ME'), 'total':a,'bond':b})


def test_buy_hold_drifts_and_threshold_trades_only_after_return():
    f=levels([100,200,200],[100,100,100])
    hold=compare_allocation(f,{'total':.5,'bond':.5},'buy_hold')
    rule=compare_allocation(f,{'total':.5,'bond':.5},'threshold_5pp')
    assert hold['path'][1]['gross_wealth']==pytest.approx(1.5)
    assert rule['path'][1]['gross_wealth']==pytest.approx(1.5)
    assert rule['summary']['rebalance_count']==1
    assert rule['path'][1]['post_weights']['total']==pytest.approx(.5)
    assert hold['path'][1]['post_weights']['total']==pytest.approx(2/3)


def test_cost_accounting_is_self_financing_and_initial_purchase_excluded():
    f=levels([100,200,200],[100,100,100])
    result=compare_allocation(f,{'total':.5,'bond':.5},'threshold_5pp',cost_bps=50)
    p=result['path'][1]
    assert p['cost_paid']==pytest.approx(p['traded_notional']*.005)
    assert p['wealth']+p['cost_paid']==pytest.approx(1.5)
    assert sum(p['post_holdings'].values())==pytest.approx(p['wealth'])
    assert result['path'][0]['cost_paid']==0
    assert result['summary']['net_cagr']<result['summary']['gross_cagr']
    # The final mark is valued but not rebalanced: no future holding interval.
    assert result['path'][-1]['rebalance'] is False


def test_annual_rebalance_uses_twelve_elapsed_months_not_calendar_label():
    dates=pd.date_range('2020-02-29',periods=14,freq='ME')
    f=pd.DataFrame({'date':dates,'total':[100]+[200]*13,'bond':[100]*14})
    r=compare_allocation(f,{'total':.5,'bond':.5},'annual')
    assert [p['date'] for p in r['path'] if p['rebalance']]==['2021-02-28']
    with pytest.raises(ValueError):
        compare_allocation(f,{'total':1.1,'bond':-.1},'annual')
