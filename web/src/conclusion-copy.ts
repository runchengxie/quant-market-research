// Conclusions summarize reviewed evidence; they are not forecasts.
export const conclusionCopy = {
  heading: { en: 'Current conclusion', zh: '当前结论' },
  boundary: { en: 'Evidence boundary', zh: '证据边界' },
  byTopic: {
    cashflow: { en: 'Past cash-flow index results can be studied, but a real stock portfolio that follows those rules has not yet been fully rebuilt and checked. Price-only returns and returns including dividends answer different questions.', zh: '可以研究现金流指数过去的表现，但按规则买卖股票的组合还没有完整复现并核验。只看价格的收益和包含分红的收益回答的是不同问题。' },
    microcap: { en: 'Rebuilt portfolios of the smallest stocks show large losses and long waits to recover old highs. Some prices and delisting outcomes are missing, so these historical results do not yet show what a real account could have earned.', zh: '按规则重建的小市值组合曾大幅下跌，也有多年没有回到前高。部分价格和退市结果缺失，因此这些历史结果还不能说明真实账户能赚多少。' },
    barra: { en: 'These style-factor comparisons describe historical group differences. Financial data availability and future-period performance have not been fully checked, so the results do not establish a tradable edge.', zh: '这些风格因子对照描述的是历史分组差异。财务数据当时是否可得、未来时期能否重复以及能否实际交易，都还没有充分核实。' },
    indices: { en: 'The index and ETF charts show different historical market paths. Their dates, fees, and treatment of dividends differ, so the numbers are not directly comparable investment results.', zh: '指数和 ETF 图表展示了不同的历史走势。日期范围、费用和分红处理方式可能不同，因此这些数字不能直接当成同一口径的投资结果比较。' },
    liquidity: { en: 'Trading-value comparisons show how much the sampled stocks traded and how complete the data is. They do not yet tell us how large an order could be filled or what trading would cost.', zh: '成交额对照说明样本股票交易有多活跃、数据覆盖有多完整；它还不能回答大额订单能否成交或实际交易要花多少钱。' },
  },
} as const;
