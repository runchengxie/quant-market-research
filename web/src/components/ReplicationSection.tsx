import { useEffect, useState } from 'react';
import { publicDataUrl } from '../lib/public-data';

type Scope = 'cashflow' | 'microcap';
type Measurement = {
  code: string; official_cagr: number | null; replica_gross_cagr: number | null;
  replica_net_cagr: number | null; replica_net_max_drawdown: number | null;
  daily_correlation: number | null; tracking_error: number | null;
};
type Snapshot = {
  schema_version: 1; as_of: string;
  sources: {id: string; label: string; detail: string; url: string}[];
  indices: {code: string; name: string; scope: Scope; status: string; finding: string; limitation: string; next: string; source_id: string}[];
  comparisons: {scope: Scope; basis: 'price' | 'total'; start: string; end: string; source_id: string; rows: Measurement[]}[];
};
const isObject = (x: unknown): x is Record<string, unknown> => x !== null && typeof x === 'object';
const nonempty = (x: unknown): x is string => typeof x === 'string' && x.trim().length > 0;
const date = (x: unknown): x is string => typeof x === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(x) && Number.isFinite(Date.parse(x)) && new Date(x).toISOString().slice(0, 10) === x;
const finiteOrNull = (x: unknown): x is number | null => x === null || typeof x === 'number' && Number.isFinite(x);
const scope = (x: unknown) => x === 'cashflow' || x === 'microcap';

export function isReplicationSnapshot(x: unknown): x is Snapshot {
  if (!isObject(x) || x.schema_version !== 1 || !date(x.as_of) || !Array.isArray(x.sources) || !Array.isArray(x.indices) || !Array.isArray(x.comparisons)) return false;
  if (!x.sources.every(s => isObject(s) && ['id', 'label', 'detail'].every(k => nonempty(s[k])) && typeof s.url === 'string' && /^https:\/\//.test(s.url))) return false;
  const sourceIds = new Set(x.sources.map(s => s.id));
  if (sourceIds.size !== x.sources.length) return false;
  if (!x.indices.every(i => isObject(i) && scope(i.scope) && ['code', 'name', 'status', 'finding', 'limitation', 'next'].every(k => nonempty(i[k])) && sourceIds.has(i.source_id))) return false;
  const indexScope = new Map(x.indices.map(i => [i.code, i.scope]));
  if (indexScope.size !== x.indices.length) return false;
  return x.comparisons.every(g => isObject(g) && scope(g.scope) && ['price', 'total'].includes(String(g.basis))
    && date(g.start) && date(g.end) && g.start < g.end && g.end <= String(x.as_of)
    && sourceIds.has(g.source_id) && Array.isArray(g.rows) && g.rows.length > 0
    && new Set(g.rows.map(r => isObject(r) ? r.code : null)).size === g.rows.length
    && g.rows.every(r => isObject(r) && indexScope.get(r.code) === g.scope
      && ['official_cagr', 'replica_gross_cagr', 'replica_net_cagr', 'replica_net_max_drawdown', 'daily_correlation', 'tracking_error'].every(k => finiteOrNull(r[k]))
      && ['official_cagr', 'replica_gross_cagr', 'replica_net_cagr'].every(k => r[k] === null || Number(r[k]) >= -1)
      && (r.daily_correlation === null || Math.abs(Number(r.daily_correlation)) <= 1)
      && (r.tracking_error === null || Number(r.tracking_error) >= 0)
      && (r.replica_net_max_drawdown === null || Number(r.replica_net_max_drawdown) >= -1 && Number(r.replica_net_max_drawdown) <= 0)));
}

export default function ReplicationSection({scope}: {scope: Scope}) {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    fetch(publicDataUrl('research/replication.json', import.meta.env?.BASE_URL ?? '/'), {signal: controller.signal})
      .then(r => { if (!r.ok) throw new Error('Unavailable'); return r.json(); })
      .then(data => { if (!controller.signal.aborted && isReplicationSnapshot(data)) setSnapshot(data); })
      .catch(() => {})
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, []);
  if (loading) return <p role="status" data-locale-text data-en="Loading replication research…" data-zh="正在读取复刻研究…">Loading replication research…</p>;
  if (!snapshot) return <section className="panel" role="status" data-locale-text data-en="Replication research data is temporarily unavailable. Other topic data remains available." data-zh="复刻研究数据暂不可用，请稍后重试。其他专题数据仍可查看。">Replication research data is temporarily unavailable. Other topic data remains available.</section>;
  return <ReplicationContent scope={scope} snapshot={snapshot} locale={typeof document !== 'undefined' ? document.documentElement.lang : 'en-US'}/>;
}

const pct = (x: number | null, unavailable: string) => x === null ? unavailable : `${(x * 100).toFixed(2)}%`;
const indexEnglish: Record<string, {name: string; status: string; finding: string; limitation: string; next: string}> = {
  '932368': {name: 'CSI 800 Free Cash Flow', status: 'Execution validation blocked', finding: 'The cost calculation has been corrected, but the complete portfolio still has one missing sell quote. The comparison remains incomplete.', limitation: 'The former net-return results were withdrawn. One sell quote is missing, finance revisions are incomplete, and industry data and corporate actions still use approximations.', next: 'Resolve the trading-suspension treatment, then recalculate the full index and the three-stock proxy separately.'},
  '980092': {name: 'CSI Guozheng Free Cash Flow', status: 'Execution validation blocked', finding: 'The cost calculation has been corrected, but the complete portfolio still has three missing sell quotes. The comparison remains incomplete.', limitation: 'Eligibility, industry data, and the pre-2024 methodology history remain unresolved; three sell quotes are also missing.', next: 'Resolve execution and historical eligibility before comparing the full index with the small-basket proxy.'},
  '931082': {name: 'CSI A500 Free Cash Flow', status: 'Historical inputs incomplete', finding: 'The 50-stock selection, cash-flow weighting, 10% cap, and rebalance constraints are implemented. Strict historical inputs failed validation, so no replication return is published.', limitation: 'Early historical-universe records and quality-metric inputs are incomplete.', next: 'Fill the available universe and raw financial data, then verify a continuous replay.'},
  '932369': {name: 'CSI 1000 Free Cash Flow', status: 'Financial inputs incomplete', finding: 'The 100-stock selection and weighting rules are implemented. All 22 formation windows failed the universe or quality-data checks, so no replication return is published.', limitation: 'Financial raw data is missing; omitting those records would change stock rankings.', next: 'Fill financial-data gaps, then calculate universe overlap and tracking error.'},
  '883418.TI': {name: 'Tonghuashun Micro-cap Index', status: 'Historical constituents unavailable', finding: 'Vendor prices are available, and an API snapshot of 290 codes and names has been retained. It does not provide effective dates, weights, or completeness, so it cannot establish historical constituents.', limitation: 'Historical constituent membership, effective dates, weights, and snapshot completeness are unavailable.', next: 'Accumulate dated constituent snapshots and verify the index rules and history.'},
  '8841431.WI': {name: 'Wind Micro-cap Index and custom 400-stock basket', status: 'Historical eligibility and valuation unresolved', finding: 'A future-quote selection issue was corrected. Audits found missing prices and ST-status records in the old target; complete official Wind daily bars are unavailable, so no reliable replica can be established.', limitation: 'Historical eligibility must be reconstructed. Suspension valuation, deferred trades, and delisting treatment are not yet specified well enough for a reliable replay.', next: 'Rebuild candidates using historical eligibility and specify suspension valuation, deferred trades, and delisting treatment.'},
};
const sourceEnglish: Record<string, {label: string; detail: string}> = {
  'tracking-20260909': {label: 'CSI 800 and Guozheng legacy valuation experiment (net results withdrawn)', detail: 'The cost allocation in the legacy available_data_tracking_20260909 experiment used information from the end of the holding period. Net returns and drawdowns were withdrawn. After correction, some rebalance dates still lacked sell quotes, so the full portfolio failed execution checks and the old all-constituent performance table was removed. Financial data uses a single revision dated 2026-09-06; industry classifications and corporate actions still include approximations.'},
  'microcap-audit-20260909': {label: 'Micro-cap market data and valuation audit', detail: 'An independent check of the legacy target from 2015-01-05 through 2026-09-08 found 3,708 missing-price records in the 400-stock basket and 88 in the three-stock weekly research proxy. The proxy has not been confirmed against the historical strategy specification. All 88 records match same-day suspension events, but the full suspension period, valuation prices, and execution have not been verified. Historical name records also identify 102,578 ST records and 14,442 unknown-status records in the 400-stock target; the three-stock proxy has 32 and 24, respectively. Record counts are not stock counts. Stocks must be selected using historical status; no custom NAV series was published in this review.'},
  'family-methodologies': {label: 'Index methodologies and data coverage', detail: 'The A500 methodology follows the July 2025 rules and the CSI 1000 methodology follows the December 2024 rules. Implemented rules include 50- and 100-stock selection, cash-flow-amount weighting, a 10% cap, and a block on A500 constituent changes that exceed the specified threshold. All 44 formation windows across both indices failed strict checks because historical universe or quality-metric inputs were incomplete. No holdings or replicated returns were published.'},
};
const copy = (locale: string) => locale === 'zh-CN' ? {
  heading: '指数复刻进展', kicker: '指数复刻', question: '自行计算的结果与官方指数有多接近？', intro: '本节展示本地选股和持仓回放结果，帮助读者区分完整指数表现与少量股票组合的复刻误差。', updated: '研究更新', remaining: '仍需解决', next: '下一步', source: '查看来源与方法 ↗', basisPrice: '价格回报', basisTotal: '税前全收益', estimate: '估值对照', period: '至', fixed: '本表使用固定实验区间，不随其他图表筛选变化。年化按252个交易日计算，扣成本结果采用25基点成交成本模型，尚未完整模拟实际成交限制。', withdrawn: '旧实验仅保留未扣成本的估值结果。净收益与净回撤已撤回，部分调仓缺少卖出报价，这组数字不能作为可成交业绩。', headers: ['指数', '官方年化', '复刻年化（未扣成本）', '复刻年化（扣成本）', '复刻最大回撤（扣成本）', '日收益相关性', '年化跟踪误差'], unavailable: '未提供', relation: '相关性与跟踪误差均比较未扣成本复刻与官方收益。相关性越接近1，日常涨跌越相似。跟踪误差衡量收益差的波动，数值越小越稳定。两项指标都要结合长期收益差判断。来源：', details: '数据来源与研究边界', historical: '历史包含回溯构建，尚未补齐的数据会影响结论。这些结果只支持研究与模拟评估，不能作为飞书少量选股组合的业绩证明。', loading: '正在读取复刻研究…', unavailableData: '复刻研究数据暂不可用，请稍后重试。其他专题数据仍可查看。'
} : {
  heading: 'Index replication progress', kicker: 'INDEX REPLICATION', question: 'How closely do local reconstructions track official indices?', intro: 'This section presents local constituent selection and holdings replays, distinguishing full-index performance from reconstruction error in small stock baskets.', updated: 'Updated', remaining: 'Open questions', next: 'Next step', source: 'View source and methods ↗', basisPrice: 'Price-return', basisTotal: 'Gross total-return', estimate: 'comparison', period: 'to', fixed: 'This table uses a fixed experiment window and does not change with other chart filters. Annualized figures use 252 trading days. The after-cost estimate applies a 25 bp transaction-cost model and does not fully simulate execution constraints.', withdrawn: 'The legacy experiment retains gross estimates only. Net returns and drawdowns were withdrawn, and some rebalance dates lack sell quotes; these figures do not represent executable performance.', headers: ['Index', 'Official annualized', 'Replica annualized (gross)', 'Replica annualized (after costs)', 'Replica max drawdown (after costs)', 'Daily return correlation', 'Annualized tracking error'], unavailable: 'Not reported', relation: 'Correlation and tracking error compare gross replica returns with official returns. Correlation closer to 1 indicates more similar daily moves. Tracking error measures return-difference volatility; lower values indicate greater stability. Both metrics should be considered alongside long-run return differences. Source: ', details: 'Sources and research limitations', historical: 'The history includes backfilled data, and missing inputs may affect the conclusions. These results support research and simulation only; they do not demonstrate the performance of a small Feishu stock-selection portfolio.', loading: 'Loading replication research…', unavailableData: 'Replication research data is temporarily unavailable. Other topic data remains available.'
};
export function ReplicationContent({scope, snapshot, locale = 'en-US'}: {scope: Scope; snapshot: Snapshot; locale?: string}) {
  const t = copy(locale);
  const indices = snapshot.indices.filter(i => i.scope === scope);
  const comparisons = snapshot.comparisons.filter(g => g.scope === scope);
  const sources = snapshot.sources.filter(s => indices.some(i => i.source_id === s.id) || comparisons.some(g => g.source_id === s.id));
  return <section className="replication-section" aria-label={t.heading}>
    <div className="theme-heading"><div><span className="section-kicker">{t.kicker}</span><h2>{t.question}</h2><p>{t.intro}</p></div><span className="asof">{t.updated} {snapshot.as_of}</span></div>
    <div className="evidence-grid">{indices.map(i => { const en = indexEnglish[i.code]; const name = locale === 'zh-CN' ? i.name : en?.name ?? i.code; return <article className="evidence-card" key={i.code}><span className="tag warm">{locale === 'zh-CN' ? i.status : en?.status ?? 'Status under review'}</span><h3>{name}</h3><p>{locale === 'zh-CN' ? i.finding : en?.finding ?? 'Research finding is not yet translated.'}</p><dl><dt>{t.remaining}</dt><dd>{locale === 'zh-CN' ? i.limitation : en?.limitation ?? 'Research limitations are not yet translated.'}</dd><dt>{t.next}</dt><dd>{locale === 'zh-CN' ? i.next : en?.next ?? 'Next step is not yet translated.'}</dd></dl><a href={snapshot.sources.find(s => s.id === i.source_id)?.url}>{t.source}</a></article>; })}</div>
    {comparisons.map(g => <section className="panel" key={`${g.basis}-${g.start}-${g.end}`}>
      <h3>{locale === 'zh-CN' ? (g.basis === 'price' ? t.basisPrice : t.basisTotal) : (g.basis === 'price' ? t.basisPrice : t.basisTotal)} {t.estimate}</h3>
      {g.source_id === 'tracking-20260909' && <p className="panel-note">{t.withdrawn}</p>}
      <p className="panel-note">{g.start} {t.period} {g.end}. {t.fixed}</p>
      <div className="table-scroll"><table><thead><tr>{t.headers.map(h => <th key={h}>{h}</th>)}</tr></thead><tbody>{g.rows.map(r => <tr key={r.code}><td>{locale === 'zh-CN' ? indices.find(i => i.code === r.code)?.name ?? r.code : indexEnglish[r.code]?.name ?? r.code}</td><td>{pct(r.official_cagr, t.unavailable)}</td><td>{pct(r.replica_gross_cagr, t.unavailable)}</td><td>{pct(r.replica_net_cagr, t.unavailable)}</td><td>{pct(r.replica_net_max_drawdown, t.unavailable)}</td><td>{r.daily_correlation === null ? t.unavailable : r.daily_correlation.toFixed(4)}</td><td>{pct(r.tracking_error, t.unavailable)}</td></tr>)}</tbody></table></div>
      <p className="panel-note">{t.relation}{locale === 'zh-CN' ? snapshot.sources.find(s => s.id === g.source_id)?.label ?? g.source_id : sourceEnglish[g.source_id]?.label ?? g.source_id}.</p>
    </section>)}
    <details className="panel"><summary>{t.details}</summary>{sources.map(s => {const en = sourceEnglish[s.id]; return <p key={s.id}><a href={s.url}>{locale === 'zh-CN' ? s.label : en?.label ?? s.id} ↗</a>: {locale === 'zh-CN' ? s.detail : en?.detail ?? 'Source details are available in the source record.'}</p>;})}<p>{t.historical}</p></details>
  </section>;
}
