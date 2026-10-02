import type { Snapshot } from './recovery-data';
import { PUBLIC_ROUTES, withBase } from '../lib/routes';

type BarraEvidence = {legacy_barra_result?: {coverage_start?: string; coverage_end?: string; factor_count?: number}};
const englishLocale = () => typeof document === 'undefined' || document.documentElement.lang === 'en-US';
const dayCount = (value: number | null) => value == null ? t('尚未观察到完整回本区间', 'No complete recovery interval observed') : `${value.toLocaleString(englishLocale() ? 'en-US' : 'zh-CN')} ${t('个自然日', 'calendar days')}`;
const t = (zh: string, en: string) => englishLocale() ? en : zh;

export function OverviewContent({recovery, barra}: {recovery: Snapshot | null; barra: BarraEvidence | null}) {
  const available = (group: string) => !recovery?.issues.some(issue => !issue.group || issue.group === group);
  const cashflow = available('cashflow_price') ? recovery?.series.find(row => row.ts_code === '932368.CSI' && row.group === 'cashflow_price') : undefined;
  const microcap = available('microcap_vendor_close') ? recovery?.series.find(row => row.ts_code === '883418.TI' && row.group === 'microcap_vendor_close') : undefined;
  const history = barra?.legacy_barra_result;
  const styleAvailable = typeof history?.coverage_end === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(history.coverage_end)
    && typeof history.factor_count === 'number' && Number.isInteger(history.factor_count) && history.factor_count > 0;
  return <>
    <div className="theme-heading"><div><span className="section-kicker" data-locale-text data-en="Research overview" data-zh="研究总览">Research overview</span><h1 data-locale-text data-en="Start with the main findings" data-zh="从主要发现开始了解这些研究">Start with the main findings</h1><p data-locale-text data-en="Review each study's conclusion and evidence scope before opening its data, charts, and calculation methods." data-zh="先浏览每项研究的结论和证据范围，再进入专题查看数据、图表与计算方法。">Review each study's conclusion and evidence scope before opening its data, charts, and calculation methods.</p></div><span className="asof" data-locale-text data-en="Dates are marked by topic" data-zh="数据日期按专题分别标注">Dates are marked by topic</span></div>
    <section className="featured-study" aria-label={t('重点研究：18 年 A 股风格因子', 'Featured study: 18-year A-share style factors')}>
      <div>
        <span className="section-kicker">{t('重点研究 · Barra 风格因子', 'Featured study · Barra-style factors')}</span>
        <h2>{t('18 年 A 股风格因子动态：收益、稳定性与市场阶段', '18-year A-share style factors: returns, stability, and market regimes')}</h2>
        <p>{t('已有历史风格因子对照，但尚不能认定为已验证的预测性 Alpha。IC、样本外验证与统计显著性仍在补充。', 'Historical style-factor comparisons are available, but they do not establish validated predictive alpha. IC, out-of-sample validation, and statistical significance remain under review.')}</p>
        <div className="featured-facts" aria-label={t('研究范围', 'Research scope')}><span><strong>{t('18 年', '18 years')}</strong>{t('历史样本', ' of history')}</span><span><strong>{t('19 个', '19')}</strong>{t('历史因子', ' historical factors')}</span><span><strong>{t('分年度', 'Annual')}</strong>{t('和分阶段比较', ' and regime comparisons')}</span></div>
      </div>
      <a href={withBase(PUBLIC_ROUTES.styleFactors, import.meta.env?.BASE_URL ?? "/")}>{t('进入风格因子研究 ↗', 'Open style-factor research ↗')}</a>
    </section>
    <section className="research-library" aria-label={t('研究目录', 'Research library')}>
      <div className="theme-heading library-heading"><div><span className="section-kicker">{t('研究目录', 'Research library')}</span><h2>{t('按关心的问题进入报告', 'Enter through a research question')}</h2><p>{t('每个专题都把结论、证据、图表和限制放在一起，详细方法与数据口径收录在文档区。', 'Each topic brings conclusions, evidence, charts, and limitations together; detailed methods and data definitions live in the documentation.')}</p></div></div>
    </section>
    <section className="evidence-grid overview-evidence-grid" aria-label={t('各专题研究进展', 'Research progress by topic')}>
      <EvidenceCard domain="基本面与现金流" title="现金流" href={withBase(PUBLIC_ROUTES.cashflow, import.meta.env?.BASE_URL ?? "/")} status={cashflow ? '指数数据已检查' : '数据暂不可用'}
        conclusion={cashflow ? cashflow.longest_completed_underwater_calendar_days == null ? t('800现金流价格指数在样本内尚无完整的回本记录。', 'The 800 cash-flow price index has no complete recovery record in this sample.') : `${t('800现金流价格指数在样本内，最长一次从高点跌落后等待了', 'For the 800 cash-flow price index, the longest wait from a peak to recovery was')} ${dayCount(cashflow.longest_completed_underwater_calendar_days)}。` : t('数据恢复后显示回本统计。', 'Recovery statistics will appear when data is restored.')}
        date={cashflow ? `${cashflow.start} ${t('至', 'to')} ${cashflow.end}` : t('数据暂不可用', 'Data unavailable')}
        scope={t('供应商指数表现，价格回报与税前全收益分开比较。', 'Vendor index performance; price and gross total return are compared separately.')}/>
      <EvidenceCard domain="规模与微盘" title="小微盘" href={withBase(PUBLIC_ROUTES.microcap, import.meta.env?.BASE_URL ?? "/")} status={microcap ? '参考指数可供研究' : '数据暂不可用'}
        conclusion={microcap ? microcap.longest_completed_underwater_calendar_days == null ? t('同花顺微盘在样本内尚无完整的回本记录。', 'The vendor micro-cap reference has no complete recovery record in this sample.') : `${t('同花顺微盘在样本内，最长一次完整回本等待为', 'For the vendor micro-cap reference, the longest complete recovery wait was')} ${dayCount(microcap.longest_completed_underwater_calendar_days)}。` : t('数据恢复后显示微盘参考指数统计。', 'Micro-cap reference statistics will appear when data is restored.')}
        date={microcap ? `${microcap.start} ${t('至', 'to')} ${microcap.end}` : t('数据暂不可用', 'Data unavailable')}
        scope={t('同花顺微盘用于观察微盘表现，中证2000和国证2000作为小盘对照。', 'The vendor micro-cap series describes micro-cap performance; CSI 2000 and SZSE 2000 provide small-cap comparisons.')}/>
      <EvidenceCard domain="市场与板块" title="长期风格" href={withBase(PUBLIC_ROUTES.indices, import.meta.env?.BASE_URL ?? "/")} status={styleAvailable ? '历史结果供研究参考' : '数据暂不可用'}
        conclusion={styleAvailable ? `${t('已整理', 'Historical results are available for')} ${history.factor_count} ${t('个因子的历史结果，用于观察不同风格在各阶段的表现。', 'factors, to compare style performance across market regimes.')}` : t('数据恢复后显示长期风格研究范围。', 'Long-run style coverage will appear when data is restored.')}
        date={styleAvailable ? `${t('Barra 历史研究截至', 'Barra historical research through')} ${history.coverage_end}` : t('数据暂不可用', 'Data unavailable')}
        scope={t('指数和 ETF 反映市场表现，风格研究观察高分组与低分组的收益差异。', 'Indices and ETFs describe market performance; style research compares returns between high- and low-scoring groups.')}/>
      <EvidenceCard domain="因子与风格" title="低换手因子" href={withBase(PUBLIC_ROUTES.lowTurnover, import.meta.env?.BASE_URL ?? "/")} status="探索性研究"
        conclusion={t('低换手在控制规模、低波动和现有特征后仍保留历史条件相关性，但尚未证明能稳定转化为净收益。', 'Low turnover retains historical conditional association after controls for size, low volatility, and existing features, but stable conversion into net returns has not been demonstrated.')}
        date={t('共同样本 2019-05 至 2026-06', 'Common sample: 2019-05 to 2026-06')} scope={t('比较原始换手、低波动、流动性和组合执行之间的关系。', 'Compares raw turnover, low volatility, liquidity, and portfolio execution.')}/>
    </section>
    <div className="fine-print"><span className="section-kicker">{t('阅读提示', 'Reading note')}</span><p>{t('各专题的样本时间不同，历史最长等待也会受到样本范围影响。页面保留尚未回本和数据缺失的记录。历史结果仅供研究参考。', 'Sample windows differ by topic, so the longest historical wait depends on coverage. Unrecovered and missing-data records remain visible. Historical results are for research only.')}</p></div>
  </>;
}

function EvidenceCard({domain, title, href, status, conclusion, date, scope}: {
  domain: string; title: string; href: string; status: string; conclusion: string; date: string; scope: string;
}) {
  const labels: Record<string, string> = { '基本面与现金流': 'Fundamentals and cash flow', '规模与微盘': 'Size and micro-caps', '市场与板块': 'Markets and segments', '因子与风格': 'Factors and style', 现金流: 'Cash flow', 小微盘: 'Micro-caps', 长期风格: 'Long-run style', 低换手因子: 'Low-turnover factor', '指数数据已检查': 'Index data checked', '参考指数可供研究': 'Reference index available', '历史结果供研究参考': 'Historical results for research', 探索性研究: 'Exploratory research', '数据暂不可用': 'Data unavailable' };
  const localized = (value: string) => englishLocale() ? labels[value] ?? value : value;
  return <article className="evidence-card"><span className="section-kicker">{localized(domain)}</span><span className="tag warm">{localized(status)}</span><h3>{localized(title)}</h3><p className="evidence-conclusion">{conclusion}</p>
    <dl><dt>{t('数据范围', 'Coverage')}</dt><dd>{date}</dd><dt>{t('观察什么', 'What it shows')}</dt><dd>{scope}</dd></dl><a href={href}>{t('查看', 'Open ')}{localized(title)}{t('专题 ↗', ' study ↗')}</a></article>;
}
