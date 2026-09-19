export type FactorDefinition = {
  factor: string;
  name: string;
  direction: string;
  method: string;
};

export type FactorDetail = {
  family: string;
  feature: string;
  calculation: string;
  current: string;
  verification: string;
};

export const factorIds = [
  'size', 'value', 'momentum', 'quality', 'earnings_yield', 'lowvol', 'growth', 'leverage', 'beta',
  'liquidity', 'liquidity_flow', 'chip_concentration', 'institution_holding', 'fund_breadth',
  'fund_breadth_change', 'fund_ownership', 'fund_ownership_change', 'dividend_yield', 'ps_value',
] as const;

export const factorNames: Record<string, string> = {
  beta: '低贝塔', chip_concentration: '筹码集中度', dividend_yield: '股息率', earnings_yield: '盈利收益率',
  fund_breadth: '公募重仓广度', fund_breadth_change: '公募重仓广度变化', fund_ownership: '公募重仓比例',
  fund_ownership_change: '公募重仓比例变化', growth: '成长', institution_holding: '机构持仓', leverage: '低杠杆',
  liquidity: '流动性（历史）', liquidity_flow: '交易流（历史）', lowvol: '低波动（历史）', momentum: '动量（历史）',
  ps_value: '市销率价值', quality: '复合质量', size: '市值', value: '价值',
};

export const factorDefinitions: FactorDefinition[] = [
  ['size', '市值', '大市值减小市值', '总市值取自然对数，每月分组'],
  ['value', '价值', '低市净率减高市净率', '市净率倒数，每月分组'],
  ['momentum', '短期动量（21日）', '强势减弱势', '排除形成日的21日收益，每月分组'],
  ['quality', '复合质量', '高质量减低质量', '盈利能力、低杠杆、盈利稳定性和现金流质量等权合成'],
  ['earnings_yield', '盈利收益率', '低市盈率减高市盈率', '滚动市盈率倒数'],
  ['lowvol', '总波动率（21日）', '低波动减高波动', '最近21个收益观察值的总收益波动率'],
  ['growth', '成长', '高增长减低增长', '净利润同比和营业收入同比，按公告日对齐'],
  ['leverage', '低杠杆', '低杠杆减高杠杆', '资产负债率，按公告日对齐'],
  ['beta', '低贝塔', '低贝塔减高贝塔', '252日滚动市场贝塔，至少126日'],
  ['liquidity', '低换手（当前快照）', '低换手减高换手', '形成日单日换手率，长期低换手研究另有20日和60日口径'],
  ['liquidity_flow', '大单资金流', '大单净买入较高减较低', '大单净买入占比'],
  ['chip_concentration', '筹码集中度', '集中度较高减较低', '前十大流通股东持股占比'],
  ['institution_holding', '机构持仓', '机构持仓较高减较低', '前十大机构流通持股占比'],
  ['fund_breadth', '公募前十大重仓广度', '重仓基金较多减较少', '按月末可见的持仓记录，统计将该股票列入前十大重仓的基金数量'],
  ['fund_breadth_change', '公募重仓广度变化', '重仓覆盖增加减减少', '前十大重仓基金数量相对上期变化'],
  ['fund_ownership', '公募重仓比例', '重仓比例较高减较低', '前十大重仓流通股持仓比例合计'],
  ['fund_ownership_change', '公募重仓比例变化', '重仓比例增加减减少', '前十大重仓流通股持仓比例相对上期变化'],
  ['dividend_yield', '股息率', '高股息率减低股息率', '过去12个月股息率'],
  ['ps_value', '市销率价值', '低市销率减高市销率', '滚动市销率倒数'],
].map(([factor, name, direction, method]) => ({ factor, name, direction, method }));

export const factorDetails: Record<string, FactorDetail> = Object.fromEntries(factorIds.map((factor) => {
  const name = factorNames[factor];
  const definition = factorDefinitions.find((item) => item.factor === factor);
  const familyByFactor: Record<string, string> = {
    size: '规模', value: '价值', earnings_yield: '价值', ps_value: '价值', dividend_yield: '价值 / 收益',
    momentum: '动量', lowvol: '波动率', growth: '成长', beta: '市场敏感度', liquidity: '流动性', liquidity_flow: '流动性 / 交易流',
    chip_concentration: '持仓 / 筹码', institution_holding: '持仓', fund_breadth: '基金持仓', fund_breadth_change: '基金持仓',
    fund_ownership: '基金持仓', fund_ownership_change: '基金持仓', quality: '质量', leverage: '质量',
  };
  return [factor, {
    family: familyByFactor[factor] ?? '其他',
    feature: `历史 ${name} 收益序列与当前可重算代理分别记录；历史底层特征未必完整保留。`,
    calculation: definition?.method ?? '历史计算公式未确认。',
    current: `当前核心字典中的 ${factor} 代理版本需结合来源、版本与适用边界阅读。`,
    verification: '历史收益摘要可验证；历史原始特征与完整公式未全部确认。',
  }];
}));

factorDetails.quality = {
  family: '质量',
  feature: '复合质量由盈利能力、低杠杆、盈利质量和盈利稳定性四个子因子构成。',
  calculation: '当前实现使用按公告排序的 8 个财务观测（至少 4 个），不保证为连续季度；各组件统一方向、缩尾、标准化后等权合成，组件缺失填 0，列整体缺失不参与平均。',
  current: 'profitability + leverage + earnings_quality + earnings_variability；ROA 仅作敏感性检查。',
  verification: '当前四子因子版本可验证；18 年历史收益尚未用该版本重跑。',
};

export function normalizeFactor(value: string | null): string {
  return value !== null && (factorIds as readonly string[]).includes(value) ? value : 'size';
}

export const FACTOR_NAMES = factorNames;
export const FACTOR_DEFINITIONS = factorDefinitions;
export const FACTOR_DETAILS = factorDetails;
