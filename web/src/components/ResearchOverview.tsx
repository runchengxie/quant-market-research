import { cloneElement, isValidElement, type ReactElement, type ReactNode } from 'react';
import { overviewCopy, overviewLabels } from '../content/overview-copy';
import { executionCostCopy as costCopy } from '../content/execution-cost-copy';
import type { Snapshot } from './recovery-data';
import { PUBLIC_ROUTES, withBase } from '../lib/routes';

type StyleFactorEvidence = {legacy_barra_result?: {coverage_start?: string; coverage_end?: string; factor_count?: number}};
type OverviewProps = {recovery: Snapshot | null; barra: StyleFactorEvidence | null};

export function OverviewContent(props: OverviewProps) {
  return bilingualOverview(overviewTree(props, 'en-US'), overviewTree(props, 'zh-CN'));
}

function overviewTree({recovery, barra}: OverviewProps, locale: 'en-US' | 'zh-CN') {
  const englishLocale = () => locale === 'en-US';
  const text = (key: keyof typeof overviewCopy) => overviewCopy[key][englishLocale() ? 0 : 1];
  const dayCount = (value: number | null) => value == null ? text('noRecovery') : `${value.toLocaleString(locale)} ${text('calendarDays')}`;
  const available = (group: string) => !recovery?.issues.some(issue => !issue.group || issue.group === group);
  const cashflow = available('cashflow_price') ? recovery?.series.find(row => row.ts_code === '932368.CSI' && row.group === 'cashflow_price') : undefined;
  const microcap = available('microcap_vendor_close') ? recovery?.series.find(row => row.ts_code === '883418.TI' && row.group === 'microcap_vendor_close') : undefined;
  const history = barra?.legacy_barra_result;
  const styleAvailable = typeof history?.coverage_end === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(history.coverage_end)
    && typeof history.factor_count === 'number' && Number.isInteger(history.factor_count) && history.factor_count > 0;
  return <>
    <div className="theme-heading"><div><span className="section-kicker" data-locale-text data-en="Research overview" data-zh="研究总览">Research overview</span><h1 data-locale-text data-en="Start with the main findings" data-zh="从主要发现开始了解这些研究">Start with the main findings</h1><p data-locale-text data-en="Review each study's conclusion and evidence scope before opening its data, charts, and calculation methods." data-zh="先浏览每项研究的结论和证据范围，再进入专题查看数据、图表与计算方法。">Review each study's conclusion and evidence scope before opening its data, charts, and calculation methods.</p></div><span className="asof" data-locale-text data-en="Dates are marked by topic" data-zh="数据日期按专题分别标注">Dates are marked by topic</span></div>
    <section className="featured-study" aria-label={text('featuredLabel')}>
      <div>
        <span className="section-kicker">{text('featuredKicker')}</span>
        <h2>{text('featuredTitle')}</h2>
        <p>{text('featuredConclusion')}</p>
        <div className="featured-facts" aria-label={text('researchScope')}><span><strong>{text('historyYears')}</strong>{text('historyLabel')}</span><span><strong>{text('factorCount')}</strong>{text('factorsLabel')}</span><span><strong>{text('annualLabel')}</strong>{text('regimesLabel')}</span></div>
      </div>
      <a href={withBase(PUBLIC_ROUTES.styleFactors, import.meta.env?.BASE_URL ?? "/")}>{text('styleLink')}</a>
    </section>
    <section className="research-library" aria-label={text('libraryLabel')}>
      <div className="theme-heading library-heading"><div><span className="section-kicker">{text('libraryLabel')}</span><h2>{text('libraryTitle')}</h2><p>{text('libraryDescription')}</p></div></div>
    </section>
    <section className="evidence-grid overview-evidence-grid" aria-label={text('progressLabel')}>
      <EvidenceCard locale={locale} domain="基本面与现金流" title="现金流" href={withBase(PUBLIC_ROUTES.cashflow, import.meta.env?.BASE_URL ?? "/")} status={cashflow ? '指数数据已检查' : '数据暂不可用'}
        conclusion={cashflow ? cashflow.longest_completed_underwater_calendar_days == null ? text('cashflowNoRecovery') : `${text('cashflowRecoveryPrefix')} ${dayCount(cashflow.longest_completed_underwater_calendar_days)}${englishLocale() ? '.' : '。'}` : text('cashflowUnavailable')}
        date={cashflow ? `${cashflow.start} ${text('rangeSeparator')} ${cashflow.end}` : text('unavailable')}
        scope={text('cashflowScope')}/>
      <EvidenceCard locale={locale} domain="规模与微盘" title="小微盘" href={withBase(PUBLIC_ROUTES.microcap, import.meta.env?.BASE_URL ?? "/")} status={microcap ? '参考指数可供研究' : '数据暂不可用'}
        conclusion={microcap ? microcap.longest_completed_underwater_calendar_days == null ? text('microcapNoRecovery') : `${text('microcapRecoveryPrefix')} ${dayCount(microcap.longest_completed_underwater_calendar_days)}${englishLocale() ? '.' : '。'}` : text('microcapUnavailable')}
        date={microcap ? `${microcap.start} ${text('rangeSeparator')} ${microcap.end}` : text('unavailable')}
        scope={text('microcapScope')}/>
      <EvidenceCard locale={locale} domain="市场与板块" title="长期风格" href={withBase(PUBLIC_ROUTES.styleFactors, import.meta.env?.BASE_URL ?? "/")} status={styleAvailable ? '历史结果供研究参考' : '数据暂不可用'}
        conclusion={styleAvailable ? `${text('factorsPrefix')} ${history.factor_count} ${text('factorsConclusionSuffix')}` : text('styleUnavailable')}
        date={styleAvailable ? `${text('styleCoveragePrefix')} ${history.coverage_end}` : text('unavailable')}
        scope={text('styleScope')}/>
      <EvidenceCard locale={locale} domain="市场与板块" title={text("indicesTitle")} href={withBase(PUBLIC_ROUTES.indices, import.meta.env?.BASE_URL ?? "/")} status="历史结果供研究参考"
        conclusion={text("indicesConclusion")} date={text("indicesCoverage")} scope={text("indicesScope")} />
      <EvidenceCard locale={locale} domain="因子与风格" title="低换手因子" href={withBase(PUBLIC_ROUTES.lowTurnover, import.meta.env?.BASE_URL ?? "/")} status="探索性研究"
        conclusion={text('lowTurnoverConclusion')}
        date={text('lowTurnoverCoverage')} scope={text('lowTurnoverScope')}/>
      <EvidenceCard locale={locale} domain={englishLocale() ? 'Execution and liquidity' : '交易执行与流动性'}
        title={costCopy.title[englishLocale() ? 0 : 1]} status={costCopy.stage[englishLocale() ? 0 : 1]}
        href={withBase('/research/liquidity/', import.meta.env?.BASE_URL ?? '/')}
        conclusion={costCopy.conclusion[englishLocale() ? 0 : 1]}
        date={costCopy.coverage[englishLocale() ? 0 : 1]}
        scope={costCopy.scope[englishLocale() ? 0 : 1]} />
    </section>
    <div className="fine-print"><span className="section-kicker">{text('readingLabel')}</span><p>{text('readingNote')}</p></div>
  </>;
}

function EvidenceCard({locale, domain, title, href, status, conclusion, date, scope}: {
  locale: 'en-US' | 'zh-CN';
  domain: string; title: string; href: string; status: string; conclusion: string; date: string; scope: string;
}) {
  const text = (key: keyof typeof overviewCopy) => overviewCopy[key][locale === 'en-US' ? 0 : 1];
  const localized = (value: string) => overviewLabels[value] ? text(overviewLabels[value]) : value;
  return <article className="evidence-card"><span className="section-kicker">{localized(domain)}</span><span className="tag warm">{localized(status)}</span><h3>{localized(title)}</h3><p className="evidence-conclusion">{conclusion}</p>
    <dl><dt>{text('coverageLabel')}</dt><dd>{date}</dd><dt>{text('scopeLabel')}</dt><dd>{scope}</dd></dl><a href={href}>{text('openPrefix')}{localized(title)}{text('studySuffix')}</a></article>;
}

// Pair both build-time renderings so dynamic evidence uses the same locale contract
// as Astro text, without shipping a React island or duplicating visible content.
function bilingualOverview(en: ReactNode, zh: ReactNode): ReactNode {
  if (typeof en === 'string' && typeof zh === 'string') {
    return en === zh ? en : <span data-locale-text data-en={en} data-zh={zh}>{en}</span>;
  }
  if (Array.isArray(en) && Array.isArray(zh)) return en.map((node, index) => bilingualOverview(node, zh[index]));
  if (!isValidElement(en) || !isValidElement(zh)) return en;
  const english = en as ReactElement<Record<string, unknown> & {children?: ReactNode; 'aria-label'?: string}>;
  const chinese = zh as ReactElement<Record<string, unknown> & {children?: ReactNode; 'aria-label'?: string}>;
  if (english.type === EvidenceCard && chinese.type === EvidenceCard) {
    return bilingualOverview(EvidenceCard(english.props as Parameters<typeof EvidenceCard>[0]), EvidenceCard(chinese.props as Parameters<typeof EvidenceCard>[0]));
  }
  const attributes: Record<string, unknown> = {};
  const textOnly = (value: ReactNode): string | null => typeof value === 'string' ? value
    : Array.isArray(value) && value.every(node => typeof node === 'string') ? value.join('') : null;
  const englishText = textOnly(english.props.children);
  const chineseText = textOnly(chinese.props.children);
  if (typeof english.props['aria-label'] === 'string' && english.props['aria-label'] !== chinese.props['aria-label']) {
    attributes['data-locale-aria'] = true;
    attributes['data-aria-en'] = english.props['aria-label'];
    attributes['data-aria-zh'] = chinese.props['aria-label'];
  }
  if (englishText !== null && chineseText !== null && englishText !== chineseText) {
    return cloneElement(english, {...attributes, 'data-locale-text': true, 'data-en': englishText, 'data-zh': chineseText}, englishText);
  }
  return cloneElement(english, attributes, bilingualOverview(english.props.children, chinese.props.children));
}
