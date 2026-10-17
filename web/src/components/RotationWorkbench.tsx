import { useState } from 'react';
import { ResearchBarChart } from './ResearchCharts';
import { englishLocale, SortableTable } from './react/research-shared';
import { experimentCards, groupLabels, groupNotes, selectWeeklyRows, workbenchCopy, type Copy, type Group } from '../content/rotation-research';
const text = (value: Copy) => value[englishLocale() ? 0 : 1];
const ui = (key: keyof typeof workbenchCopy) => text(workbenchCopy[key]);
const pct = (value: number) => `${value.toFixed(2)}%`;
export function ExperimentExplorer() {
  const [family, setFamily] = useState('all');
  const cards = experimentCards.filter(card => family === 'all' || card.family === family);
  return <section className="panel" id="experiments" aria-labelledby="experiment-heading">
    <h2 id="experiment-heading">{ui('exploreTheResearchBranches')}</h2>
    <label className="rotation-control">{ui('researchBranch')} <select aria-label={ui('researchBranch')} value={family} onChange={event => setFamily(event.target.value)}>
      <option value="all">{ui('allBranches')}</option><option value="etf">{ui('etfSelectionAndAllocation')}</option><option value="hotspot">{ui('hotspotStockEvidence')}</option><option value="bridge">{ui('themeToETFValidationGap')}</option>
    </select></label>
    <p role="status">{text(workbenchCopy.branchCount).replace('{count}', new Intl.NumberFormat(englishLocale() ? 'en-US' : 'zh-CN').format(cards.length)).replace('{branches}', cards.length === 1 ? 'branch' : 'branches')}</p>
    <div className="rotation-card-grid">{cards.map(card => <article className="rotation-card" key={card.title[0]}>
      <span className="section-kicker">{ui(card.family === 'bridge' ? 'researchProposal' : 'historicalDiagnostic')}</span>
      <h3>{text(card.title)}</h3><p>{text(card.observation)}</p><p className="panel-note">{text(card.scope)}</p>
      <details><summary>{ui('whatRemainsToTest')}</summary><p>{text(card.next)}</p></details>
      <a href={`#${card.anchor}`}>{ui('readEvidenceAndLimitations')}</a>
    </article>)}</div>
  </section>;
}
export function WeeklyExperimentCharts() {
  const [group, setGroup] = useState<Group>('risk');
  const [measure, setMeasure] = useState<'cagr' | 'sharpe' | 'drawdown'>('drawdown');
  const rows = selectWeeklyRows(group);
  const metricLabels = { cagr: ui('annualizedReturn'), sharpe: ui('sharpeRatio'), drawdown: ui('maximumDrawdown') };
  const format = (value: number) => measure === 'sharpe' ? value.toFixed(3) : pct(value);
  return <section className="panel" aria-labelledby="weekly-chart-title">
    <h3 id="weekly-chart-title">{ui('compareOneExperimentFamilyAtATime')}</h3>
    <div className="rotation-controls"><label className="rotation-control">{ui('experimentGroup')} <select aria-label={ui('experimentGroup')} value={group} onChange={event => setGroup(event.target.value as Group)}>
      {(Object.keys(groupLabels) as Group[]).map(key => <option value={key} key={key}>{text(groupLabels[key])}</option>)}
    </select></label>
    <label className="rotation-control">{ui('chartMeasure')} <select aria-label={ui('chartMeasure')} value={measure} onChange={event => setMeasure(event.target.value as typeof measure)}>
      {Object.entries(metricLabels).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
    </select></label></div>
    <p role="status">{text(groupLabels[group])} · {metricLabels[measure]} · {rows.length} {ui('configurations')}</p>
    <ResearchBarChart rows={rows.map(row => ({ name: text(row.label), value: String(row[measure]) }))} labelKey="name" valueKey="value" formatter={format} />
    <p className="panel-note">{text(groupNotes[group])}</p>
    <details open className="chart-data"><summary>{ui('inspectAndSortAllMetrics')}</summary>
      <SortableTable key={group} rows={rows.map(row => ({ name: text(row.label), cagr: row.cagr.toFixed(2), sharpe: row.sharpe.toFixed(3), drawdown: row.drawdown.toFixed(2), fallback: row.fallback == null ? '' : row.fallback.toFixed(2), executions: row.executions == null ? ui('notReported') : String(row.executions) }))} columns={[
        ['name', ui('configuration')], ['cagr', `${metricLabels.cagr} (%)`], ['sharpe', metricLabels.sharpe], ['drawdown', `${metricLabels.drawdown} (%)`], ['fallback', ui('averageBondFallbackWeight')], ['executions', ui('executedRebalances')],
      ]} />
    </details>
    <p className="panel-note">{ui('missingCellsMeanTheSourceNoteDid')}</p>
  </section>;
}
