export type SectionId = 'overview' | 'research' | 'docs' | 'data';
export type TopicId = 'cashflow' | 'microcap' | 'style' | 'low-turnover' | 'indices' | 'liquidity';

export type PublicPage = {
  id: string;
  route: string;
  title: string;
  summary: string;
  section: SectionId;
  topic?: TopicId;
  aliases: readonly string[];
  related: readonly string[];
  snapshotKeys: readonly string[];
};

export type PublicDoc = PublicPage & { source: string; slug: string };

const docSources = new Set([
  'docs/index.md',
  'docs/research-closeout-status.md',
  'docs/research/factors/low-turnover.md',
  'docs/research/factors/pb-roe.md',
  'docs/research/factors/microcap.md',
  'docs/research/experiments/microcap-execution-diagnostic-20260928.md',
  'docs/research/factors/smallcap-turnover-history.md',
  'docs/research/factors/barra-factor-dictionary.md',
  'docs/research/factors/barra-source-inventory.md',
  'docs/index.zh-CN.md',
  'docs/research-closeout-status.zh-CN.md',
  'docs/research/factors/low-turnover.zh-CN.md',
  'docs/research/factors/pb-roe.zh-CN.md',
  'docs/research/factors/microcap.zh-CN.md',
  'docs/research/experiments/microcap-execution-diagnostic-20260928.zh-CN.md',
  'docs/research/factors/smallcap-turnover-history.zh-CN.md',
  'docs/research/factors/barra-factor-dictionary.zh-CN.md',
  'docs/research/factors/barra-source-inventory.zh-CN.md',
]);
const allowedSnapshotKeys = new Set([
  'cashflow.performance', 'cashflow.recovery', 'microcap.summary',
  'liquidity.cross-market', 'indices.returns', 'barra.returns', 'liquidity.summary', 'low-turnover.ledger',
]);

const page = (value: PublicPage): PublicPage => value;

export const publicPages: readonly PublicPage[] = [
  page({ id: 'overview', route: '/', title: '研究总览', summary: '每项研究发现了什么、数据覆盖哪些日期，还有哪些问题没有答案。', section: 'overview', aliases: ['/index.html'], related: ['research', 'docs', 'data-sources'], snapshotKeys: [] }),
  page({ id: 'research', route: '/research/', title: '研究专题', summary: '从研究问题出发，先看结论，再查数据和证据限制。', section: 'research', aliases: [], related: ['cashflow', 'microcap', 'style', 'pb-roe', 'low-turnover', 'indices', 'liquidity'], snapshotKeys: [] }),
  page({ id: 'cashflow', route: '/research/cashflow/', title: '现金流与分红', summary: '现金流和分红相关股票过去表现如何，经历下跌后多久回到前高。', section: 'research', topic: 'cashflow', aliases: [], related: ['cashflow-recovery', 'indices'], snapshotKeys: ['cashflow.performance'] }),
  page({ id: 'cashflow-recovery', route: '/research/cashflow/recovery/', title: '现金流恢复性', summary: '现金流研究中的回本时间、结果复核和实际交易限制。', section: 'research', topic: 'cashflow', aliases: [], related: ['cashflow'], snapshotKeys: ['cashflow.recovery'] }),
  page({ id: 'microcap', route: '/research/microcap/', title: '小微盘研究', summary: '小市值股票组合过去涨跌如何，数据缺口会怎样影响结果。', section: 'research', topic: 'microcap', aliases: [], related: ['cross-market-liquidity', 'low-turnover'], snapshotKeys: ['microcap.summary'] }),
  page({ id: 'cross-market-liquidity', route: '/research/microcap/cross-market-liquidity/', title: '跨市场流动性', summary: '不同市场的股票交易有多活跃，这些数据能否放在一起比较。', section: 'research', topic: 'microcap', aliases: [], related: ['microcap', 'liquidity'], snapshotKeys: ['liquidity.cross-market'] }),
  page({ id: 'indices', route: '/research/indices/', title: '指数与长期回报', summary: '网站展示了哪些指数和 ETF，它们的历史收益为什么不能直接比较。', section: 'research', topic: 'indices', aliases: [], related: ['cashflow', 'style'], snapshotKeys: ['indices.returns'] }),
  page({ id: 'style', route: '/research/style-factors-18y/', title: '18 年风格因子', summary: '价值、规模等股票分组在不同年份和市场阶段的表现。', section: 'research', topic: 'style', aliases: [], related: ['low-turnover', 'indices'], snapshotKeys: ['barra.returns'] }),
  page({ id: 'pb-roe', route: '/research/factors/pb-roe/', title: 'PB 与 ROE 历史对照', summary: '在同一批股票中加入盈利指标后，估值排序的历史结果怎样变化。', section: 'research', topic: 'style', aliases: [], related: ['pb-roe-method', 'style'], snapshotKeys: [] }),
  page({ id: 'liquidity', route: '/research/liquidity/', title: '流动性研究', summary: '样本股票交易有多活跃、数据覆盖有多完整，目前能得出什么结论。', section: 'research', topic: 'liquidity', aliases: [], related: ['cross-market-liquidity', 'microcap'], snapshotKeys: ['liquidity.summary'] }),
  page({ id: 'low-turnover', route: '/research/factors/low-turnover/', title: '低换手因子', summary: '低换手股票过去表现如何，考虑其他股票特征后差距还剩多少。', section: 'research', topic: 'low-turnover', aliases: [], related: ['style', 'microcap'], snapshotKeys: ['low-turnover.ledger'] }),
  page({ id: 'docs', route: '/docs/', title: '方法与字典', summary: '研究方法、因子定义、数据来源与收尾状态。', section: 'docs', aliases: [], related: ['research', 'data-sources'], snapshotKeys: [] }),
  page({ id: 'research-closeout-status', route: '/docs/research-closeout-status/', title: '研究收尾状态', summary: '研究项目的完成度、边界与未完成事项。', section: 'docs', aliases: [], related: ['docs'], snapshotKeys: [] }),
  page({ id: 'low-turnover-method', route: '/docs/research/factors/low-turnover/', title: '低换手因子方法', summary: '低换手研究的方法、执行与验证说明。', section: 'docs', topic: 'low-turnover', aliases: [], related: ['low-turnover'], snapshotKeys: [] }),
  page({ id: 'pb-roe-method', route: '/docs/research/factors/pb-roe/', title: 'PB 与 ROE 历史对照', summary: '估值与盈利能力的历史配对结果、候选池审计和验证边界。', section: 'docs', topic: 'style', aliases: [], related: ['pb-roe', 'barra-factor-dictionary'], snapshotKeys: [] }),
  page({ id: 'microcap-method', route: '/docs/research/factors/microcap/', title: '小微盘因子方法', summary: '小微盘研究的方法、覆盖与限制。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap'], snapshotKeys: [] }),
  page({ id: 'microcap-execution-diagnostic', route: '/docs/research/experiments/microcap-execution-diagnostic-20260928/', title: '微盘执行模拟诊断', summary: '微盘执行账本、缺失结算事件与可验证边界。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap-method'], snapshotKeys: [] }),
  page({ id: 'smallcap-turnover-history', route: '/docs/research/factors/smallcap-turnover-history/', title: '小盘换手历史', summary: '小盘换手历史研究的口径与结果。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap'], snapshotKeys: [] }),
  page({ id: 'barra-factor-dictionary', route: '/docs/research/factors/barra-factor-dictionary/', title: 'Barra 因子字典', summary: '19 个历史因子、检查过的定义与核心代理。', section: 'docs', topic: 'style', aliases: [], related: ['style'], snapshotKeys: [] }),
  page({ id: 'barra-source-inventory', route: '/docs/research/factors/barra-source-inventory/', title: 'Barra 来源清单', summary: 'Barra 因子来源、版本与可验证程度。', section: 'docs', topic: 'style', aliases: [], related: ['style'], snapshotKeys: [] }),
  page({ id: 'docs-zh-CN', route: '/docs/index.zh-CN/', title: '研究说明', summary: '中文研究方法、因子定义、数据来源与收尾状态。', section: 'docs', aliases: [], related: ['docs'], snapshotKeys: [] }),
  page({ id: 'research-closeout-status-zh-CN', route: '/docs/research-closeout-status.zh-CN/', title: '研究收口状态', summary: '中文研究项目完成度、边界与未完成事项。', section: 'docs', aliases: [], related: ['docs'], snapshotKeys: [] }),
  page({ id: 'low-turnover-method-zh-CN', route: '/docs/research/factors/low-turnover.zh-CN/', title: '低换手因子方法', summary: '中文低换手研究方法、执行与验证说明。', section: 'docs', topic: 'low-turnover', aliases: [], related: ['low-turnover'], snapshotKeys: [] }),
  page({ id: 'pb-roe-method-zh-CN', route: '/docs/research/factors/pb-roe.zh-CN/', title: 'PB 与 ROE 历史对照', summary: '中文估值与盈利能力历史配对结果和验证边界。', section: 'docs', topic: 'style', aliases: [], related: ['pb-roe', 'barra-factor-dictionary'], snapshotKeys: [] }),
  page({ id: 'microcap-method-zh-CN', route: '/docs/research/factors/microcap.zh-CN/', title: '小微盘因子方法', summary: '中文小微盘研究方法、覆盖与限制。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap'], snapshotKeys: [] }),
  page({ id: 'microcap-execution-diagnostic-zh-CN', route: '/docs/research/experiments/microcap-execution-diagnostic-20260928.zh-CN/', title: '微盘执行模拟诊断', summary: '中文微盘执行账本和可验证边界。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap-method'], snapshotKeys: [] }),
  page({ id: 'smallcap-turnover-history-zh-CN', route: '/docs/research/factors/smallcap-turnover-history.zh-CN/', title: '小盘换手历史', summary: '中文小盘换手历史研究口径与结果。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap'], snapshotKeys: [] }),
  page({ id: 'barra-factor-dictionary-zh-CN', route: '/docs/research/factors/barra-factor-dictionary.zh-CN/', title: 'Barra 因子字典', summary: '中文 Barra 因子定义与历史快照边界。', section: 'docs', topic: 'style', aliases: [], related: ['style'], snapshotKeys: [] }),
  page({ id: 'barra-source-inventory-zh-CN', route: '/docs/research/factors/barra-source-inventory.zh-CN/', title: 'Barra 来源清单', summary: '中文 Barra 因子来源、版本与可验证程度。', section: 'docs', topic: 'style', aliases: [], related: ['style'], snapshotKeys: [] }),
  page({ id: 'data-sources', route: '/data-sources/', title: '数据与版本', summary: '公开数据快照、覆盖日期和生成版本。', section: 'data', aliases: [], related: ['overview', 'docs'], snapshotKeys: [] }),
];

export const publicDocs: readonly PublicDoc[] = [
  { ...publicPages.find((p) => p.id === 'docs'), source: 'docs/index.md', slug: '' },
  { ...publicPages.find((p) => p.id === 'research-closeout-status'), source: 'docs/research-closeout-status.md', slug: 'research-closeout-status' },
  { ...publicPages.find((p) => p.id === 'low-turnover-method'), source: 'docs/research/factors/low-turnover.md', slug: 'research/factors/low-turnover' },
  { ...publicPages.find((p) => p.id === 'pb-roe-method'), source: 'docs/research/factors/pb-roe.md', slug: 'research/factors/pb-roe' },
  { ...publicPages.find((p) => p.id === 'microcap-method'), source: 'docs/research/factors/microcap.md', slug: 'research/factors/microcap' },
  { ...publicPages.find((p) => p.id === 'microcap-execution-diagnostic'), source: 'docs/research/experiments/microcap-execution-diagnostic-20260928.md', slug: 'research/experiments/microcap-execution-diagnostic-20260928' },
  { ...publicPages.find((p) => p.id === 'smallcap-turnover-history'), source: 'docs/research/factors/smallcap-turnover-history.md', slug: 'research/factors/smallcap-turnover-history' },
  { ...publicPages.find((p) => p.id === 'barra-factor-dictionary'), source: 'docs/research/factors/barra-factor-dictionary.md', slug: 'research/factors/barra-factor-dictionary' },
  { ...publicPages.find((p) => p.id === 'barra-source-inventory'), source: 'docs/research/factors/barra-source-inventory.md', slug: 'research/factors/barra-source-inventory' },
  { ...publicPages.find((p) => p.id === 'docs-zh-CN'), source: 'docs/index.zh-CN.md', slug: 'index.zh-CN' },
  { ...publicPages.find((p) => p.id === 'research-closeout-status-zh-CN'), source: 'docs/research-closeout-status.zh-CN.md', slug: 'research-closeout-status.zh-CN' },
  { ...publicPages.find((p) => p.id === 'low-turnover-method-zh-CN'), source: 'docs/research/factors/low-turnover.zh-CN.md', slug: 'research/factors/low-turnover.zh-CN' },
  { ...publicPages.find((p) => p.id === 'pb-roe-method-zh-CN'), source: 'docs/research/factors/pb-roe.zh-CN.md', slug: 'research/factors/pb-roe.zh-CN' },
  { ...publicPages.find((p) => p.id === 'microcap-method-zh-CN'), source: 'docs/research/factors/microcap.zh-CN.md', slug: 'research/factors/microcap.zh-CN' },
  { ...publicPages.find((p) => p.id === 'microcap-execution-diagnostic-zh-CN'), source: 'docs/research/experiments/microcap-execution-diagnostic-20260928.zh-CN.md', slug: 'research/experiments/microcap-execution-diagnostic-20260928.zh-CN' },
  { ...publicPages.find((p) => p.id === 'smallcap-turnover-history-zh-CN'), source: 'docs/research/factors/smallcap-turnover-history.zh-CN.md', slug: 'research/factors/smallcap-turnover-history.zh-CN' },
  { ...publicPages.find((p) => p.id === 'barra-factor-dictionary-zh-CN'), source: 'docs/research/factors/barra-factor-dictionary.zh-CN.md', slug: 'research/factors/barra-factor-dictionary.zh-CN' },
  { ...publicPages.find((p) => p.id === 'barra-source-inventory-zh-CN'), source: 'docs/research/factors/barra-source-inventory.zh-CN.md', slug: 'research/factors/barra-source-inventory.zh-CN' },
].map((doc) => ({ ...doc } as PublicDoc));

export function validateRegistry(pages: readonly PublicPage[], docs: readonly PublicDoc[]): void {
  const ids = new Set<string>();
  const routes = new Set<string>();
  const sources = new Set<string>();
  for (const item of pages) {
    if (ids.has(item.id) || routes.has(item.route)) throw new Error(`duplicate registry id or route: ${item.id}`);
    ids.add(item.id); routes.add(item.route);
  }
  for (const item of pages) {
    for (const related of item.related) if (!ids.has(related)) throw new Error(`unknown related page: ${related}`);
    for (const snapshot of item.snapshotKeys) if (!allowedSnapshotKeys.has(snapshot)) throw new Error(`unknown snapshotKey: ${snapshot}`);
  }
  for (const doc of docs) {
    if (!ids.has(doc.id) || !routes.has(doc.route)) throw new Error(`document is not registered: ${doc.id}`);
    if (sources.has(doc.source) || !docSources.has(doc.source) || doc.source.includes('..')) throw new Error(`source allowlist violation: ${doc.source}`);
    sources.add(doc.source);
    if (!doc.route.startsWith('/docs/')) throw new Error(`document route outside docs: ${doc.route}`);
    if (doc.slug !== '' && /(^\/|\/$)/.test(doc.slug)) throw new Error(`invalid document slug: ${doc.slug}`);
  }
}

validateRegistry(publicPages, publicDocs);

export function pageForRoute(route: string): PublicPage | undefined {
  const normalized = route === '/' ? '/' : `/${route.replace(/^\/+|\/+$/g, '')}/`;
  return publicPages.find((page) => page.route === normalized || page.aliases.includes(route));
}
