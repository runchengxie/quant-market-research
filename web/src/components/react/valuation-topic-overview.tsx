import { useState } from 'react';
import { ValuationEvidenceDirectory, ValuationRound2, ValuationRound2Findings } from './valuation-round2';
import { ValuationLedgerCheckpoint } from './valuation-ledger-checkpoint';
import { ResourceState, useJson } from './research-shared';
import { annualValuations, positiveSegments, type ValuationDistribution, type TopicEvidence } from '../../lib/valuation-topic';
import { topicCopy } from '../../content/valuation-topic-copy';
import { valuationCopy, valuationFormulas } from '../../content/valuation-groups-copy';
import { withBase } from '../../lib/routes';

type Input = { distributions: ValuationDistribution[]; groups: string[]; metrics: string[] };
const dateText = (value: string) => `${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`;

export function ValuationTopicOverview({ data, english }: { data: Input; english: boolean }) {
  const resource = useJson<TopicEvidence>('low_valuation_topic_reviewed.json');
  const [group, setGroup] = useState('non_st');
  const [metric, setMetric] = useState('pb_parent');
  const [gapMetric, setGapMetric] = useState('pb_parent');
  const lang = english ? 0 : 1;
  const t = (key: keyof typeof topicCopy) => topicCopy[key][lang];
  const v = (key: string) => valuationCopy[key as keyof typeof valuationCopy]?.[lang] ?? key;
  const number = (value: number | null | undefined, percentage = false) => value == null || !Number.isFinite(value) ? v('not_available') : new Intl.NumberFormat(english ? 'en-US' : 'zh-CN', { maximumFractionDigits: percentage ? 2 : 4, ...(percentage ? { style: 'percent' as const } : {}) }).format(value);
  const link = (route: string) => `${withBase(route, import.meta.env.BASE_URL)}?lang=${english ? 'en-US' : 'zh-CN'}`;
  if (!resource.data) return <ResourceState loading={!resource.error} error={resource.error} retry={resource.retry} />;
  const evidence = resource.data;
  const annual = annualValuations(data.distributions, group, metric);
  const values = annual.flatMap(r => [r.minimum, r.p01, r.p05]).filter((x): x is number => x != null && Number.isFinite(x) && x > 0);
  const low = values.length ? Math.log10(Math.min(...values)) : 0;
  const high = values.length ? Math.log10(Math.max(...values)) : 1;
  const x = (i: number) => 65 + i * 530 / Math.max(1, annual.length - 1);
  const y = (value: number) => 175 - (Math.log10(value) - low) * 145 / Math.max(.1, high - low);
  const gap = evidence.gaps.find(g => g.metric === gapMetric)!;
  const gapMax = Math.max(...gap.reasons.map(r => r.count));
  const comparisons = evidence.ranking.pairs.filter(p =>
    (p.first === 'pe_ttm' && ['pe_deducted_proxy', 'pb_parent'].includes(p.second)) || (p.first === 'pb_parent' && p.second === 'pb_ex_intangibles_proxy'));
  return <div className="valuation-topic" data-testid="valuation-topic">
    <section className="panel valuation-conclusions" aria-labelledby="valuation-overview-title">
      <h2 id="valuation-overview-title">{t('overview')}</h2>
      <ol>{['finding_one', 'finding_two', 'finding_three'].map(key => <li key={key}>{t(key as keyof typeof topicCopy)}</li>)}</ol>
      <nav className="report-links"><a href="#valuation-annual">{t('annual')}</a><a href="#valuation-definitions">{t('definitions')}</a><a href="#valuation-evidence">{t('evidence')}</a><a href="#valuation-ledger">{t('checkpoint')}</a><a href="#valuation-distributions">{t('explore')}</a></nav>
    </section>
    <div className="callout" role="note" data-testid="valuation-warning"><strong>{v('draft')}</strong><p>{v('warning')}</p>
      <details className="valuation-detail"><summary>{t('technical_status')}</summary><p>{t('revision_status')}</p><p>{t('terms')}</p></details>
    </div>
    <ValuationEvidenceDirectory english={english} />
    <section className="panel" id="valuation-annual" data-testid="valuation-annual">
      <h2>{t('annual')}</h2><p>{t('annual_scope')}</p>
      <div className="callout valuation-coverage-warning" role="note" data-testid="valuation-early-coverage">{t('early')}</div>
      <div className="valuation-controls">
        <label>{v('group')}<select data-testid="annual-group" value={group} onChange={e => setGroup(e.target.value)}>{data.groups.map(g => <option key={g} value={g}>{v(g)}</option>)}</select></label>
        <label>{v('metric')}<select data-testid="annual-metric" value={metric} onChange={e => setMetric(e.target.value)}>{data.metrics.map(m => <option key={m} value={m}>{v(m)}</option>)}</select></label>
      </div>
      <p className="panel-note">{t('annual_basis')}</p>
      <h3>{t('snapshot')} · {v(group)} · {v(metric)}</h3>
      {values.length ? <figure className="valuation-trend" data-testid="annual-chart"><figcaption>{t('log_chart')}</figcaption>
        <svg viewBox="0 0 640 215" role="img" aria-label={t('log_chart')}>
          <line x1="65" y1="175" x2="595" y2="175" stroke="currentColor" opacity=".3" />
          <text x="4" y="35">{number(10 ** high)}</text><text x="4" y="175">{number(10 ** low)}</text>
          {(['minimum', 'p01', 'p05'] as const).map((key, s) => <g key={key} className={`valuation-series-${s}`}>
            {positiveSegments(annual, key).map((segment, j) => <polyline key={j} points={segment.map(p => `${x(p.index)},${y(p.value)}`).join(' ')} fill="none" stroke="currentColor" strokeWidth="2" />)}
            {annual.map((r, i) => r[key] != null && r[key]! > 0 ? <circle key={r.year} cx={x(i)} cy={y(r[key]!)} r="2.5" fill="currentColor"><title>{dateText(r.formation_date)} · {key}={number(r[key])} · n={r.valid_n}</title></circle> : null)}
          </g>)}
          {annual.filter((_, i) => i === 0 || i === annual.length - 1 || i === Math.floor(annual.length / 2)).map(r => <text key={r.year} x={x(annual.indexOf(r)) - 12} y="205">{r.year}</text>)}
        </svg><div className="valuation-legend">{(['min', 'p1', 'p5'] as const).map((key, i) => <span key={key} className={`valuation-series-${i}`}>● {t(key)}</span>)}</div>
      </figure> : <p>{v('not_available')}</p>}
      <div className="valuation-table"><table data-testid="annual-table"><thead><tr>{['date', 'min', 'p1', 'p5', 'n', 'excluded'].map(k => <th key={k}>{t(k as keyof typeof topicCopy)}</th>)}</tr></thead>
        <tbody>{annual.map(r => <tr key={r.year}><th>{dateText(r.formation_date)}</th><td>{number(r.minimum)}</td><td>{number(r.p01)}</td><td>{number(r.p05)}</td><td>{number(r.valid_n)} / {number(r.total_n)}</td><td>{number(r.nonpositive_denominator_n)} / {number(r.missing_or_invalid_n)}</td></tr>)}</tbody></table></div>
      <details className="valuation-detail"><summary>{t('sample_low')}</summary><p>{t('sample_low_note')}</p>
        <div className="valuation-table"><table data-testid="annual-extremes"><thead><tr><th>{t('year')}</th><th>{t('min')}</th><th>{t('dates')}</th><th>{t('extreme_n')}</th></tr></thead>
          <tbody>{annual.map(r => <tr key={r.year}><th>{r.year}</th><td>{number(r.sampled_minimum)}</td><td>{r.sampled_dates.length ? r.sampled_dates.map(dateText).join(' / ') : v('not_available')}</td><td>{r.sampled_valid_n.length ? r.sampled_valid_n.map(n => number(n)).join(' / ') : v('not_available')}</td></tr>)}</tbody></table></div>
      </details>
    </section>
    <section className="panel" id="valuation-definitions" data-testid="valuation-definitions">
      <h2>{t('definitions')}</h2><p>{t('formula_scope')}</p>
      <dl className="valuation-formulas">{data.metrics.map(m => <div key={m}><dt>{v(m)}</dt><dd><code>{valuationFormulas[m]}</code></dd></div>)}</dl>
      <p>{t('pe_reading')}</p><p>{t('pb_reading')}</p>
      <h3>{t('ranks')}</h3><p>{t('rank_scope')}</p>
      <div className="valuation-table"><table data-testid="valuation-rank-comparison"><thead><tr><th>{t('comparison')}</th><th>{t('rho')}</th><th>{t('jaccard')}</th></tr></thead>
        <tbody>{comparisons.map(r => <tr key={r.first + r.second}><th>{v(r.first)} / {v(r.second)}</th><td>{number(r.spearman)}</td><td>{number(r.bottom_quintile_jaccard, true)}</td></tr>)}</tbody></table></div>
      <a href={link('/docs/research/experiments/valuation-panel-20261018/')}>{t('rank_method')}</a>
    </section>
    <section className="panel" data-testid="valuation-status-support"><h2>{t('states')}</h2><p>{t('state_note')}</p>
      <dl className="valuation-stats">{data.groups.map(g => {
        const r = data.distributions.find(r => r.formation_date === '20261016' && r.sample_basis === 'metric_available' && r.metric === 'pe_deducted_proxy' && r.group === g);
        return <div key={g}><dt>{v(g)}</dt><dd>{number(r?.valid_n)} / {number(r?.total_n)}</dd></div>;
      })}</dl>
    </section>
    <section className="panel" id="valuation-evidence" data-testid="valuation-evidence"><h2>{t('evidence')}</h2><p>{t('evidence_note')}</p>
      <h3>{t('legacy')}</h3><p>{t('legacy_note')}</p>
      <div className="valuation-table"><table data-testid="valuation-legacy"><thead><tr><th>{v('metric')}</th><th>{t('annualized')}</th><th>{t('drawdown')}</th></tr></thead><tbody>{evidence.legacy.factors.map(f => <tr key={f.factor}><th>{t(`legacy_${f.factor}` as keyof typeof topicCopy)}</th><td>{number(f.geometric_annual_ret / 100, true)}</td><td>{number(f.max_drawdown / 100, true)}</td></tr>)}</tbody></table></div>
      <p className="panel-note">{t('legacy_limit')}</p><p>{t('conditional')}</p>
      <a href={link('/research/style-factors-18y/')}>{t('style')}</a>
      <h3>{t('gaps')}</h3><p data-testid="gap-scope">{t('gap_scope')}</p><p>{t('gap_note')}</p>
      <label className="valuation-gap-select">{v('metric')}<select data-testid="gap-metric" value={gapMetric} onChange={e => setGapMetric(e.target.value)}>{evidence.gaps.map(g => <option key={g.metric} value={g.metric}>{v(g.metric)}</option>)}</select></label>
      <p data-testid="gap-total">{t('resolved')}: {number(gap.resolved)} / {number(gap.total)} · {t('unresolved')}: {number(gap.unresolved)}</p>
      <figure className="valuation-gaps" data-testid="valuation-gaps" aria-label={t('gaps')}>{gap.reasons.map(r => <div className="valuation-gap-row" key={r.reason}>
        <span>{t(r.reason as keyof typeof topicCopy)}</span><div className="valuation-gap-track"><div style={{ width: `${r.count / gapMax * 100}%` }} /></div><strong>{number(r.count)}</strong>
      </div>)}</figure><p>{t('gap_rule')}</p>
    </section>
    <ValuationRound2Findings english={english} />
    <ValuationLedgerCheckpoint english={english} />
    <ValuationRound2 english={english} />
    <section className="panel" data-testid="valuation-interpretation"><h2>{t('interpretation')}</h2>
      <div className="valuation-reading-grid">{[['earnings_hypothesis', 'earnings_text'], ['assets_hypothesis', 'assets_text'], ['execution_hypothesis', 'execution_text']].map(([heading, text]) => <article key={heading}><h3>{t(heading as keyof typeof topicCopy)}</h3><p>{t(text as keyof typeof topicCopy)}</p></article>)}</div>
      <p className="panel-note">{t('hypothesis_note')}</p>
      <h3>{t('related')}</h3><nav className="report-links"><a href={link('/research/style-factors-18y/')}>{t('style')}</a><a href={link('/research/microcap/')}>{t('microcap')}</a><a href={link('/research/cashflow/')}>{t('cashflow')}</a></nav>
    </section>
    <h2 className="valuation-explore-heading">{t('explore')}</h2>
  </div>;
}
