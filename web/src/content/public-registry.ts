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
  'docs/research/factors/smallcap-turnover-history.md',
  'docs/research/factors/barra-factor-dictionary.md',
  'docs/research/factors/barra-source-inventory.md',
]);
const allowedSnapshotKeys = new Set([
  'cashflow.performance', 'cashflow.recovery', 'microcap.summary',
  'liquidity.cross-market', 'indices.returns', 'barra.returns', 'liquidity.summary', 'low-turnover.ledger',
]);

const page = (value: PublicPage): PublicPage => value;

export const publicPages: readonly PublicPage[] = [
  page({ id: 'overview', route: '/', title: '研究总览', summary: '研究主题、数据边界与最新可验证证据。', section: 'overview', aliases: ['/index.html'], related: ['research', 'docs', 'data-sources'], snapshotKeys: [] }),
  page({ id: 'research', route: '/research/', title: '研究专题', summary: '按研究问题浏览现金流、规模、风格、指数与流动性专题。', section: 'research', aliases: [], related: ['cashflow', 'microcap', 'style', 'low-turnover', 'indices', 'liquidity'], snapshotKeys: [] }),
  page({ id: 'cashflow', route: '/research/cashflow/', title: '现金流与分红', summary: '现金流与分红因子的长期表现、恢复性检验与边界。', section: 'research', topic: 'cashflow', aliases: [], related: ['cashflow-recovery', 'indices'], snapshotKeys: ['cashflow.performance'] }),
  page({ id: 'cashflow-recovery', route: '/research/cashflow/recovery/', title: '现金流恢复性', summary: '现金流研究的恢复、复制与可执行性证据。', section: 'research', topic: 'cashflow', aliases: [], related: ['cashflow'], snapshotKeys: ['cashflow.recovery'] }),
  page({ id: 'microcap', route: '/research/microcap/', title: '小微盘研究', summary: '小微盘规模、成交额与样本覆盖的研究证据。', section: 'research', topic: 'microcap', aliases: [], related: ['cross-market-liquidity', 'low-turnover'], snapshotKeys: ['microcap.summary'] }),
  page({ id: 'cross-market-liquidity', route: '/research/microcap/cross-market-liquidity/', title: '跨市场流动性', summary: '不同市场口径下的流动性与复制性比较。', section: 'research', topic: 'microcap', aliases: [], related: ['microcap', 'liquidity'], snapshotKeys: ['liquidity.cross-market'] }),
  page({ id: 'indices', route: '/research/indices/', title: '指数与长期回报', summary: '指数样本、分类筛选与长期回报证据。', section: 'research', topic: 'indices', aliases: [], related: ['cashflow', 'style'], snapshotKeys: ['indices.returns'] }),
  page({ id: 'style', route: '/research/style-factors-18y/', title: '18 年风格因子', summary: '风格因子的逐年表现、Barra 定义与研究边界。', section: 'research', topic: 'style', aliases: [], related: ['low-turnover', 'indices'], snapshotKeys: ['barra.returns'] }),
  page({ id: 'liquidity', route: '/research/liquidity/', title: '流动性研究', summary: '流动性研究的覆盖、数据口径与可验证结论。', section: 'research', topic: 'liquidity', aliases: [], related: ['cross-market-liquidity', 'microcap'], snapshotKeys: ['liquidity.summary'] }),
  page({ id: 'low-turnover', route: '/research/factors/low-turnover/', title: '低换手因子', summary: '低换手因子的长期表现、执行账本与复制证据。', section: 'research', topic: 'low-turnover', aliases: [], related: ['style', 'microcap'], snapshotKeys: ['low-turnover.ledger'] }),
  page({ id: 'docs', route: '/docs/', title: '方法与字典', summary: '研究方法、因子定义、数据来源与收尾状态。', section: 'docs', aliases: [], related: ['research', 'data-sources'], snapshotKeys: [] }),
  page({ id: 'research-closeout-status', route: '/docs/research-closeout-status/', title: '研究收尾状态', summary: '研究项目的完成度、边界与未完成事项。', section: 'docs', aliases: [], related: ['docs'], snapshotKeys: [] }),
  page({ id: 'low-turnover-method', route: '/docs/research/factors/low-turnover/', title: '低换手因子方法', summary: '低换手研究的方法、执行与验证说明。', section: 'docs', topic: 'low-turnover', aliases: [], related: ['low-turnover'], snapshotKeys: [] }),
  page({ id: 'pb-roe-method', route: '/docs/research/factors/pb-roe/', title: 'PB 与 ROE 方法', summary: '估值与盈利能力联合比较的数据口径和验证边界。', section: 'docs', topic: 'style', aliases: [], related: ['style', 'barra-factor-dictionary'], snapshotKeys: [] }),
  page({ id: 'microcap-method', route: '/docs/research/factors/microcap/', title: '小微盘因子方法', summary: '小微盘研究的方法、覆盖与限制。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap'], snapshotKeys: [] }),
  page({ id: 'smallcap-turnover-history', route: '/docs/research/factors/smallcap-turnover-history/', title: '小盘换手历史', summary: '小盘换手历史研究的口径与结果。', section: 'docs', topic: 'microcap', aliases: [], related: ['microcap'], snapshotKeys: [] }),
  page({ id: 'barra-factor-dictionary', route: '/docs/research/factors/barra-factor-dictionary/', title: 'Barra 因子字典', summary: '19 个历史因子、检查过的定义与核心代理。', section: 'docs', topic: 'style', aliases: [], related: ['style'], snapshotKeys: [] }),
  page({ id: 'barra-source-inventory', route: '/docs/research/factors/barra-source-inventory/', title: 'Barra 来源清单', summary: 'Barra 因子来源、版本与可验证程度。', section: 'docs', topic: 'style', aliases: [], related: ['style'], snapshotKeys: [] }),
  page({ id: 'data-sources', route: '/data-sources/', title: '数据与版本', summary: '公开数据快照、覆盖日期和生成版本。', section: 'data', aliases: [], related: ['overview', 'docs'], snapshotKeys: [] }),
];

export const publicDocs: readonly PublicDoc[] = [
  { ...publicPages.find((p) => p.id === 'docs'), source: 'docs/index.md', slug: '' },
  { ...publicPages.find((p) => p.id === 'research-closeout-status'), source: 'docs/research-closeout-status.md', slug: 'research-closeout-status' },
  { ...publicPages.find((p) => p.id === 'low-turnover-method'), source: 'docs/research/factors/low-turnover.md', slug: 'research/factors/low-turnover' },
  { ...publicPages.find((p) => p.id === 'pb-roe-method'), source: 'docs/research/factors/pb-roe.md', slug: 'research/factors/pb-roe' },
  { ...publicPages.find((p) => p.id === 'microcap-method'), source: 'docs/research/factors/microcap.md', slug: 'research/factors/microcap' },
  { ...publicPages.find((p) => p.id === 'smallcap-turnover-history'), source: 'docs/research/factors/smallcap-turnover-history.md', slug: 'research/factors/smallcap-turnover-history' },
  { ...publicPages.find((p) => p.id === 'barra-factor-dictionary'), source: 'docs/research/factors/barra-factor-dictionary.md', slug: 'research/factors/barra-factor-dictionary' },
  { ...publicPages.find((p) => p.id === 'barra-source-inventory'), source: 'docs/research/factors/barra-source-inventory.md', slug: 'research/factors/barra-source-inventory' },
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
