export const executionCopy = {
  "low_turnover_execution_validation": [
    "Low-turnover execution validation",
    "低换手执行验证"
  ],
  "kicker": [
    "Trading simulation results",
    "模拟交易结果"
  ],
  "heading": [
    "Simulated portfolios under trading assumptions",
    "加入成交假设后的模拟组合表现"
  ],
  "coverage": [
    "Simulation data cover",
    "模拟数据覆盖"
  ],
  "through": [
    "through",
    "至"
  ],
  "scope": [
    ". The table compares candidates under one share-based ledger, suspension treatment and participation assumption. It does not show matched constrained and unconstrained versions of one signal, so it cannot isolate the effect of trading constraints.",
    "。下表在同一份额账本、停牌与成交比例假设下比较候选方案。它没有展示同一信号在约束前后的对照，不能据此计算成交约束单独带来的影响。"
  ],
  "tableGuide": [
    "Net annualized return expresses the simulated after-cost result per year. The Sharpe ratio compares average return with variability. Maximum drawdown measures the largest fall from a high to a later low. Annualized turnover measures the portfolio’s own trading relative to capital. Fill ratio is the fraction of target purchases filled; average cash is the fraction left uninvested.",
    "净年化是模拟中扣除模型成本后、按年折算的收益。夏普比率比较平均收益与波动的大小，最大回撤记录净值从高点跌到随后低点的最大幅度。年化换手衡量组合一年的买卖金额相对组合规模有多大。成交率是模拟目标买入量中填入的比例，平均现金表示资金有多少留在现金里。"
  ],
  "candidate": [
    "Candidate",
    "候选"
  ],
  "net_annualized": [
    "Net annualized",
    "净年化"
  ],
  "net_sharpe": [
    "Net Sharpe",
    "净夏普"
  ],
  "max_drawdown": [
    "Max drawdown",
    "最大回撤"
  ],
  "annualized_turnover": [
    "Annualized turnover",
    "年化换手"
  ],
  "x": [
    "x",
    "倍"
  ],
  "capacityNote": [
    "Capacity scenarios cap daily trading at 5% of the previous session’s traded value. These scenarios at CNY 1 million and above have incomplete fills; retained cash and delays change the holdings path. This uses prior-day traded value, unlike the separate ADV20 experiments.",
    "容量情景假设每天成交金额不超过前一交易日成交额的 5%。100 万元及以上的这些情景均未完全成交，留存现金和延迟成交会改变持仓路径。这里采用前一日成交额，与另一些使用 ADV20 的实验不同。"
  ],
  "capacityChart": [
    "Simulated fill ratio by capital, from 0% to 100%",
    "不同资金规模的模拟成交率，范围为 0% 至 100%"
  ],
  "cny": [
    "CNY",
    "元"
  ],
  "avg_cash": [
    "Avg. cash",
    "平均现金"
  ],
  "capacityGuide": [
    "Bars show simulated fill ratios. Actual order fills remain unverified.",
    "柱长按模拟成交率绘制，实际订单能否成交仍需核实。"
  ],
  "capital": [
    "Capital",
    "资金规模"
  ],
  "fill_ratio": [
    "Fill ratio",
    "成交率"
  ],
  "cash_weight": [
    "Cash weight",
    "现金权重"
  ],
  "snapshotNote": [
    "These data rely on traded-value proxies and impact assumptions. Actual costs still need execution-record calibration. Complete fields are in the ",
    "这些数据依赖成交额代理与冲击假设，实际成本仍待成交记录校准。完整字段见"
  ],
  "public_snapshot": [
    "public snapshot",
    "公开快照"
  ],
  "turnover_windows_and_rebalance_frequency": [
    "Turnover windows and rebalance frequency",
    "换手窗口与调仓频率"
  ],
  "windowNote": [
    "The archived monthly simulation associates longer windows with lower turnover and shallower drawdowns. Its 120-session value is 7.60%; a later same-input replay gives 4.22% at a 90-observation minimum and 6.26% at 45. The original run is unrecovered and the discrepancy unresolved. Retain this as historical sensitivity evidence, without selecting a best window.",
    "这份历史月度模拟中，较长窗口对应较低的组合换手和较浅的回撤。120 日原快照为 7.60%，后续同输入重放在最低 90 个有效观测时为 4.22%，45 个时为 6.26%。原运行尚未找回，差异未完全解释，图表暂作历史敏感性记录，不能据此选定最佳窗口。"
  ],
  "windowChart": [
    "Turnover lookback in the monthly ledger, net annualized return from 0% to ",
    "月度模拟的换手观察窗口，净年化收益范围为 0% 至 "
  ],
  "day_average": [
    "day average",
    "日平均"
  ],
  "drawdown": [
    "Drawdown",
    "回撤"
  ],
  "windowGuide": [
    "Bars show net annualized returns in this monthly simulation. Drawdown and portfolio turnover remain alongside them so risk can also be assessed.",
    "柱长表示这份月度模拟的净年化收益，旁边保留回撤和组合换手，便于同时查看风险。"
  ],
  "average_turnover_window": [
    "Average turnover window",
    "平均换手窗口"
  ],
  "days": [
    "days",
    "日"
  ],
  "jointNote": [
    "A separate archived window/frequency matrix reports about 17% to 21% net annualized returns biweekly and 8% to 14% monthly, with drawdowns around −59% to −69%. It is a different experiment record from the window table above. Without a fully reconciled run manifest, retain the records separately.",
    "另一个已归档的窗口与频率矩阵中，双周调仓的净年化约为 17% 至 21%，月度约为 8% 至 14%，回撤仍约为负 59% 至负 69%。它与上方窗口表来自不同的实验记录，缺少逐项对齐的运行清单，暂时分开保留。"
  ],
  "turnover_window": [
    "Turnover window",
    "换手窗口"
  ],
  "rebalance_frequency": [
    "Rebalance frequency",
    "调仓频率"
  ],
  "sentenceEnd": [
    ".",
    "。"
  ]
} as const;

export const executionLabels: Record<string, readonly [string,string]> = {
  "low_turnover": [
    "Low turnover",
    "低换手"
  ],
  "small_cap": [
    "Small cap",
    "小市值"
  ],
  "composite": [
    "Composite signal",
    "复合信号"
  ],
  "large_cap_control": [
    "Large-cap control",
    "大市值对照"
  ],
  "low_turnover_residual": [
    "Low-turnover residual",
    "低换手残差信号"
  ],
  "mean_20": [
    "20-session mean",
    "20 日均值"
  ],
  "mean_60": [
    "60-session mean",
    "60 日均值"
  ],
  "median_60": [
    "60-session median",
    "60 日中位数"
  ],
  "mean_120": [
    "120-session mean",
    "120 日均值"
  ],
  "weekly": [
    "Weekly",
    "每周"
  ],
  "biweekly": [
    "Every two weeks",
    "每两周"
  ],
  "monthly": [
    "Monthly",
    "每月"
  ],
  "quarterly": [
    "Quarterly",
    "每季度"
  ]
};
