import { useEffect, useState } from 'react';
import { englishLocale, ResourceState, useJson } from './research-shared';
import { valuationCopy, valuationFormulas, type ValuationCopyKey } from '../../content/valuation-groups-copy';
import { ValuationTopicOverview } from './valuation-topic-overview';

type Distribution = {
  formation_date: string; group: string; metric: string; sample_basis: string;
  total_n: number; valid_n: number; equal_weight_mean: number | null; ratio_of_totals: number | null;
  median: number | null; minimum: number | null; p01: number | null; p05: number | null; p25: number | null;
  nonpositive_denominator_n: number; missing_or_invalid_n: number;
  p75: number | null; p99: number | null; risk_flags: string[];
};
type Cost = { months: number; mean_monthly_return: number | null };
type Factor = { group: string; metric: string; attempted_months: number; ic_months: number;
  mean_rank_ic: number | null; paired_tail_months: number; mean_cheap_minus_expensive: number | null;
  quintiles: { quintile: number; complete_months: number; mean_gross_monthly_return: number | null;
    mean_traded_notional: number | null; cost_sensitivity: Record<string, Cost> }[];
};
type Study = { groups: string[]; metrics: string[]; coverage: { formation_date: string; unknown_n: number; quoted_n: number }[];
  distributions: Distribution[]; factor_summaries: Factor[] };

export function ValuationGroupsPage() {
  const resource = useJson<Study>('grouped_valuation_draft.json');
  const [english, setEnglish] = useState(true);
  const [date, setDate] = useState('20261016');
  const [group, setGroup] = useState('all_market');
  const [metric, setMetric] = useState('pe_deducted_proxy');
  const [basis, setBasis] = useState('metric_available');
  useEffect(() => {
    const update = () => setEnglish(englishLocale());
    update();
    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
    return () => observer.disconnect();
  }, []);
  const t = (key: string) => valuationCopy[key as ValuationCopyKey]?.[english ? 0 : 1] ?? key;
  const num = (value: number | null | undefined, percent = false) => value == null || !Number.isFinite(value)
    ? t('not_available') : new Intl.NumberFormat(english ? 'en-US' : 'zh-CN', {
      maximumFractionDigits: percent ? 2 : 4, ...(percent ? { style: 'percent' as const } : {}),
    }).format(value);
  if (!resource.data) return <ResourceState loading={!resource.error} error={resource.error} retry={resource.retry} />;
  const data = resource.data;
  const row = data.distributions.find(r => r.formation_date === date && r.group === group && r.metric === metric && r.sample_basis === basis);
  const factor = data.factor_summaries.find(r => r.group === group && r.metric === metric);
  const coverage = data.coverage.find(r => r.formation_date === date);
  const history = data.distributions.filter(r => r.group === group && r.metric === metric && r.sample_basis === basis && r.median != null && r.median > 0);
  const logs = history.map(r => Math.log10(r.median!));
  const lo = logs.length ? Math.min(...logs) : 0;
  const hi = logs.length ? Math.max(...logs) : 1;
  const dates = data.coverage.map(r => r.formation_date);
  const x = (date: string) => 70 + dates.indexOf(date) * 530 / Math.max(dates.length - 1, 1);
  const y = (value: number) => 175 - (Math.log10(value) - lo) / Math.max(hi - lo, .1) * 145;
  return <div className="valuation-study">
    <div className="callout" role="note" data-testid="valuation-warning"><strong>{t('draft')}</strong><p>{t('warning')}</p></div>
    <ValuationTopicOverview data={data} english={english} />
    <div className="valuation-controls">
      <label>{t('date')}<select data-testid="valuation-date" value={date} onChange={e => setDate(e.target.value)}>{[...dates].reverse().map(d => <option key={d}>{d}</option>)}</select></label>
      <label>{t('group')}<select data-testid="valuation-group" value={group} onChange={e => setGroup(e.target.value)}>{data.groups.map(g => <option key={g} value={g}>{t(g)}</option>)}</select></label>
      <label>{t('metric')}<select data-testid="valuation-metric" value={metric} onChange={e => setMetric(e.target.value)}>{data.metrics.map(m => <option key={m} value={m}>{t(m)}</option>)}</select></label>
      <label>{t('basis')}<select data-testid="valuation-basis" value={basis} onChange={e => setBasis(e.target.value)}>{['metric_available', 'common_five'].map(b => <option key={b} value={b}>{t(b)}</option>)}</select></label>
    </div>
    <section className="panel" id="valuation-distributions" data-testid="valuation-distribution">
      <h2>{t('distribution')}</h2><p data-testid="valuation-summary">{date} · {t(group)} · {t(metric)} · {t(basis)}</p>
      <p className="panel-note">{t('formula')} <code>{valuationFormulas[metric]}</code></p>
      <dl className="valuation-stats">
        <div><dt>{t('supported')}</dt><dd>{num(row?.valid_n)} / {num(row?.total_n)}</dd></div>
        <div><dt>{t('equal_mean')}</dt><dd>{num(row?.equal_weight_mean)}</dd></div>
        <div><dt>{t('totals')}</dt><dd>{num(row?.ratio_of_totals)}</dd></div>
        <div><dt>{t('median')}</dt><dd>{num(row?.median)}</dd></div>
        <div><dt>{t('minimum')}</dt><dd>{num(row?.minimum)}</dd></div>
        <div><dt>{t('range')}</dt><dd>{[row?.p01, row?.p25, row?.p75, row?.p99].map(v => num(v)).join(' / ')}</dd></div>
      </dl>
      <p>{t('aggregation')}</p><p>{t('minimum_note')}</p><p className="panel-note">{t('proxy_note')}</p>
      <figure className="valuation-trend"><figcaption>{t('trend')} · {t(metric)}</figcaption>
        <svg viewBox="0 0 640 215" role="img" aria-label={t('trend')}>
          <line x1="70" y1="175" x2="600" y2="175" stroke="currentColor" opacity=".3" />
          <text x="4" y="35">{num(10 ** hi)}</text><text x="4" y="175">{num(10 ** lo)}</text>
          {history.map((point, i) => {
            const previous = history[i - 1];
            const adjacent = previous && dates.indexOf(point.formation_date) === dates.indexOf(previous.formation_date) + 1;
            return <g key={point.formation_date}>
              {adjacent && <line x1={x(previous.formation_date)} y1={y(previous.median!)} x2={x(point.formation_date)} y2={y(point.median!)} stroke="var(--accent)" strokeWidth="2" />}
              <circle cx={x(point.formation_date)} cy={y(point.median!)} r="2" fill="var(--accent)"><title>{point.formation_date} · {num(point.median)} · n={point.valid_n}</title></circle>
            </g>;
          })}
          <text x="70" y="205">{dates[0]}</text><text x="525" y="205">{dates.at(-1)}</text>
        </svg>
      </figure>
      <p className="panel-note">{t('unknown')} {num(coverage?.unknown_n)} / {num(coverage?.quoted_n)}. {t('coverage')}</p>
    </section>
    <section className="panel" data-testid="valuation-factor"><h2>{t('factor')}</h2>
      <p data-testid="valuation-factor-basis">{t('factor_basis')}</p>
      <p>{t('factor_note')}</p>
      {factor ? <>
        <p><strong>{t('ic')}</strong> {num(factor.mean_rank_ic)} / {factor.ic_months} ({factor.attempted_months})</p>
        <p><strong>{t('tails')}</strong> {num(factor.mean_cheap_minus_expensive, true)} / {factor.paired_tail_months}</p>
        <div className="valuation-table"><table><thead><tr>{['q', 'gross', 'turnover', 'cost0', 'cost10', 'cost30'].map(k => <th key={k}>{t(k)}</th>)}</tr></thead>
          <tbody>{factor.quintiles.map(q => <tr key={q.quintile}><th>{q.quintile}</th><td>{num(q.mean_gross_monthly_return, true)} / {q.complete_months}</td><td>{num(q.mean_traded_notional)} / {q.cost_sensitivity['0'].months}</td>
            <td>{num(q.cost_sensitivity['0'].mean_monthly_return, true)} / {q.cost_sensitivity['0'].months}</td>
            <td>{num(q.cost_sensitivity['10'].mean_monthly_return, true)} / {q.cost_sensitivity['10'].months}</td><td>{num(q.cost_sensitivity['30'].mean_monthly_return, true)} / {q.cost_sensitivity['30'].months}</td></tr>)}</tbody></table></div>
      </> : <p>{t('unknown_factor')}</p>}
      <p className="panel-note">{t('support')}</p><p className="panel-note">{t('execution')}</p>
    </section>
  </div>;
}
