export const freshnessStatusCopy: Record<string, readonly [string, string]> = {
  derived: ['Derived summary', '衍生汇总'],
  pending: ['Pending', '待补'],
  unknown: ['Unknown', '尚未确认'],
  reviewed: ['Reviewed', '已审核'],
  exploratory: ['Exploratory', '探索中'],
  validated: ['Validated', '已验证'],
  partial: ['Partial coverage', '覆盖不完整'],
  incomplete: ['Incomplete coverage', '覆盖不完整'],
  exploration: ['Exploratory', '探索中'],
  blocked: ['Blocked', '暂不可用'],
};

export const snapshotTitleCopy: Record<string, readonly [string, string]> = {
  overview: ['Research overview', '研究总览'],
  microcap: ['Microcap reconstruction', '微盘重建'],
  microcap_repair: ['Microcap missing-price audit', '微盘缺失价格审计'],
  turnover: ['Small-cap turnover history', '小盘换手历史'],
  low_turnover: ['Low-turnover factor', '低换手因子'],
  barra: ['Historical style factors', '历史风格因子'],
  cashflow: ['Cash-flow indices', '现金流指数'],
  indices: ['Indices and ETFs', '指数与ETF'],
  liquidity: ['Liquidity', '流动性'],
  execution_costs: ['Trading costs: static L2 study', '交易成本：静态盘口研究'],
  execution_strategy: ['Trading costs: strategy diagnostic', '交易成本：策略诊断'],
};

export const freshnessSourceCopy: Record<string, readonly [string, string]> = {
  overview: ['reviewed public research snapshots', '已审核的公开研究快照'],
};
