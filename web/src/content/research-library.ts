import type { Copy } from './research-reading';
export const libraryGroups = [
  { id:'characteristics', title:['Stock characteristics','股票特征'] as Copy, description:['Valuation and turnover: how stock groups differ.','从估值和换手率出发，比较不同股票分组。'] as Copy, topics:['low-turnover','valuation-groups'] },
  { id:'portfolios', title:['Portfolios and indices','组合与指数'] as Copy, description:['Micro-caps, cash flow and index histories, with their reconstruction limits.','查看小微盘、现金流和指数历史，以及组合重建的限制。'] as Copy, topics:['microcap','cashflow','indices'] },
  { id:'styles', title:['Market styles and timing','市场风格与择时'] as Copy, description:['Long-run styles, overseas information and theme rotation.','研究长期风格、海外盘面信息和主题轮动。'] as Copy, topics:['style','overseas-leadlag','rotation'] },
  { id:'execution', title:['Trading and liquidity','交易与流动性'] as Copy, description:['Costs, liquidity and the gap between a simulation and real fills.','了解成本、流动性，以及模拟结果与实际成交的距离。'] as Copy, topics:['liquidity'] },
];
export const libraryCopy = {
  areas:['Research areas','研究方向'],
  topicCount:['9 topics across 4 research areas','9 个专题 · 4 个研究方向'],
  intro:['Choose a question, read the finding and its limits, then explore the evidence. Each topic keeps its own sample dates.','从感兴趣的问题出发，先看发现与限制，再进入证据。各专题分别标注样本日期。'],
  open:['Read the study →','进入专题 →'],
  detail:['Full finding','完整结论'],
  update:['About the latest editorial update','最近一次阅读更新'],
} satisfies Record<string, Copy>;
export const librarySummaries: Record<string, Copy> = {
  'low-turnover':['Low-turnover stocks performed better in this historical comparison. The gap became smaller after accounting for other stock characteristics.','这段历史里低换手组表现较好；考虑其他股票特征后，组间差距缩小。'],
  'valuation-groups':['Different accounting definitions change valuation comparisons. Full-market coverage and achievable returns remain unverified.','财务口径会改变估值比较；全市场覆盖和实际可实现收益仍待验证。'],
  microcap:['Reconstructed small-cap portfolios suffered deep drawdowns. Missing exit prices complicate the return calculation.','重建的小市值组合经历过较深回撤，退出价格缺失也影响收益判断。'],
  cashflow:['Compare cash-flow index histories, drawdowns and rule reconstructions while keeping official indices and shadow portfolios separate.','比较现金流指数的历史表现、回撤和规则复刻，并区分官方指数与影子组合。'],
  indices:['Read index and ETF histories with their dates and dividend conventions. Different series cannot be ranked on equal terms.','结合日期与分红口径查看指数和 ETF；不同序列不能直接混排。'],
  style:['Value, size and other styles behaved differently across years and market regimes. Historical factor results need separate trading validation.','价值、规模等风格在不同年份和市场阶段表现各异；因子历史结果仍需实际交易检验。'],
  'overseas-leadlag':['Separate overseas-market forecasting information from the return of a T+1 ETF trading scenario.','区分海外盘面的预测信息与 T+1 ETF 交易情景的收益。'],
  rotation:['Published experiments have not established a stable trading advantage from theme-to-ETF signals.','已公开实验尚未证实主题信号转为 ETF 组合后有稳定交易优势。'],
  liquidity:['Compare trading activity and cost scenarios before judging strategy capacity. Real fills and price impact still need calibration.','先看交易活跃度与成本情景，再判断策略容量；真实成交与价格冲击仍待校准。'],
};
