// Conclusions summarize reviewed evidence; they are not forecasts.
export const conclusionCopy = {
  heading: { en: 'Current conclusion', zh: '当前结论' },
  boundary: { en: 'Evidence boundary', zh: '证据边界' },
  byTopic: {
    cashflow: { en: 'Cash-flow index history is observable, but an independently executable stock-portfolio replication remains under review. Price and total-return evidence must be read separately.', zh: '现金流指数历史可供观察，但独立可执行的股票组合复刻仍在核验中。价格收益与全收益证据须分别解读。' },
    microcap: { en: 'The smallest-cap reconstruction remains conditional on missing-price treatment. Historical portfolio results cannot yet establish executable net returns.', zh: '最小市值组合重建结果仍取决于缺失价格的处理方式。历史组合结果尚不能证明可执行的净收益。' },
    barra: { en: 'Style comparisons remain exploratory; PIT integrity and executable alpha are unverified.', zh: '历史风格对照仍属探索性证据；预测性 Alpha、时点完整性与可交易性尚未验证。' },
    indices: { en: 'Index and ETF histories describe the observed market paths. Different coverage and return bases prevent treating every series as a directly comparable investment result.', zh: '指数与 ETF 历史描述已观察到的市场路径。覆盖区间与收益口径不同，不能将全部序列直接视为可比的投资结果。' },
    liquidity: { en: 'Traded-value comparisons describe observed liquidity and coverage; they do not yet establish order-level capacity or implementation costs.', zh: '成交额对照描述已观察到的流动性与数据覆盖，尚不能确定订单层面的容量或实际交易成本。' },
  },
} as const;
