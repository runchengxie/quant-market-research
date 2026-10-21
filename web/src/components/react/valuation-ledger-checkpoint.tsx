import { useState } from 'react';
import { ResourceState, useJson } from './research-shared';
import type { CheckpointEvidence } from '../../lib/valuation-checkpoint';
import { checkpointCopy } from '../../content/valuation-checkpoint-copy';
import { valuationCopy } from '../../content/valuation-groups-copy';

type Evidence = CheckpointEvidence & { source_sha256: Record<string, string>; audits: { filled_orders_checked: number; persisted_max_cash_error: number } };
type Metric = 'pb_parent' | 'pe_deducted_proxy';
type Scenario = 'touch10' | 'close10' | 'touch0' | 'touch30';

export function ValuationLedgerCheckpoint({ english }: { english: boolean }) {
  const resource = useJson<Evidence>('valuation_ledger_checkpoint_draft.json');
  const [metric, setMetric] = useState<Metric>('pb_parent');
  const [scenario, setScenario] = useState<Scenario>('touch10');
  const lang = english ? 0 : 1;
  const t = (key: keyof typeof checkpointCopy) => checkpointCopy[key][lang];
  const v = (key: string) => valuationCopy[key as keyof typeof valuationCopy]?.[lang] ?? key;
  const num = (value: number | null | undefined, percent = false) => value == null || !Number.isFinite(value) ? t('missing') : new Intl.NumberFormat(english ? 'en-US' : 'zh-CN', { maximumFractionDigits: percent ? 2 : 4, ...(percent ? { style: 'percent' as const } : {}) }).format(value);
  if (!resource.data) return <ResourceState loading={!resource.error} error={resource.error} retry={resource.retry} />;
  const data = resource.data;
  const selected = data.portfolios.filter(r => r.metric === metric && r.scenario === scenario);
  const conditions = data.conditions.filter(r => r.metric === metric);
  const strata = data.strata.filter(r => r.metric === metric);
  const industry = data.industries.rows.find(r => r.metric === metric)!;
  return <div className="valuation-checkpoint" data-testid="valuation-checkpoint">
    <section className="panel" id="valuation-ledger" data-testid="valuation-ledger">
      <h2>{t('title')}</h2><p>{t('lead')}</p>
      <div className="callout valuation-coverage-warning" role="note" data-testid="ledger-warning">{t('warning')}</div>
      <p>{t('scope')}</p>
      <p data-testid="ledger-unresolved-scope"><strong>{t('unresolved_scope')}</strong></p>
      <dl className="valuation-stats"><div><dt>{t('portfolios')}</dt><dd>{num(data.scope.portfolios)}</dd></div><div><dt>{t('sessions')}</dt><dd>{num(data.scope.sessions)}</dd></div><div><dt>{t('cash_error')}</dt><dd>{num(data.scope.cash_replay_error)}</dd></div></dl>
      <p className="panel-note" data-testid="ledger-audit-note">{t('audit_note').replace('{fills}', num(data.audits.filled_orders_checked)).replace('{error}', data.audits.persisted_max_cash_error.toExponential(3))}</p>
      <nav className="report-links"><a href="#valuation-persistence">{t('persistence')}</a><a href="#valuation-coverage-audit">{t('coverage')}</a><a href="#valuation-cases">{t('cases')}</a></nav>
      <div className="valuation-controls">
        <label>{t('metric')}<select value={metric} onChange={e => setMetric(e.target.value as Metric)} data-testid="ledger-metric">{(['pb_parent', 'pe_deducted_proxy'] as const).map(m => <option key={m} value={m}>{v(m)}</option>)}</select></label>
        <label>{t('scenario')}<select value={scenario} onChange={e => setScenario(e.target.value as Scenario)} data-testid="ledger-scenario">{(['touch10', 'close10', 'touch0', 'touch30'] as const).map(s => <option key={s} value={s}>{t(s)}</option>)}</select></label>
      </div>
      <h3>{v(metric)} · {t(scenario)}</h3>
      <div className="valuation-table"><table data-testid="ledger-support"><thead><tr>{(['quintile', 'unresolved', 'strict_days', 'delayed', 'max_delay'] as const).map(k => <th key={k}>{t(k)}</th>)}</tr></thead><tbody>{selected.map(r => <tr key={r.quintile}><th>{r.quintile}</th><td>{num(r.unresolved_lots)}</td><td>{num(r.strict_nav_days)} / {data.scope.sessions}</td><td>{num(r.delayed_sales)}</td><td>{num(r.max_exit_delay_sessions)}</td></tr>)}</tbody></table></div>
      <p>{t('policy')}</p><p data-testid="ledger-fill-limits">{t('fill_limit')}</p>
      <details className="valuation-detail" data-testid="ledger-sensitivity"><summary>{t('sensitivity')}</summary><p>{t('impairment_note')}</p>
        <div className="valuation-table"><table data-testid="ledger-sensitivity-table"><thead><tr>{(['quintile', 'impairment_end', 'unresolved', 'strict_end'] as const).map(k => <th key={k}>{t(k)}</th>)}</tr></thead><tbody>{selected.map(r => <tr key={r.quintile}><th>{r.quintile}</th><td>{num(r.zero_unresolved_total_change, true)}</td><td>{num(r.unresolved_lots)}</td><td>{num(r.strict_total_change, true)}</td></tr>)}</tbody></table></div>
      </details>
      <h3>{t('actions')}</h3><p data-testid="ledger-action-gap">{t('action_scope')}</p>
      <dl className="valuation-stats"><div><dt>{t('action_rows')}</dt><dd>{num(data.actions.implemented_window_rows)}</dd></div><div><dt>{t('missing_cash')}</dt><dd>{num(data.actions.missing_cash_field_rows)}</dd></div><div><dt>{t('duplicate_actions')}</dt><dd>{num(data.actions.repeated_symbol_ex_date_rows)}</dd></div></dl>
      <p>{t('action_limits')}</p>
    </section>
    <section className="panel" id="valuation-persistence" data-testid="valuation-persistence"><h2>{t('persistence')}</h2><p>{t('persistence_scope')}</p><h3>{v(metric)}</h3>
      <div className="valuation-table"><table data-testid="persistence-table"><thead><tr>{(['condition', 'stock_months', 'resolved', 'months', 'conditional_mean'] as const).map(k => <th key={k}>{t(k)}</th>)}</tr></thead><tbody>{conditions.map(r => <tr key={r.condition}><th>{t(r.condition as keyof typeof checkpointCopy)}</th><td>{num(r.stock_months)}</td><td>{num(r.endpoint_resolved)} / {num(r.unresolved)}</td><td>{num(r.months)} / {num(r.months_with_at_least_20)}</td><td>{num(r.equal_month_conditional_mean, true)}</td></tr>)}</tbody></table></div>
      <p className="panel-note" data-testid="condition-limit">{t('condition_limit')}</p>
    </section>
    <section className="panel" id="valuation-coverage-audit" data-testid="valuation-coverage-audit"><h2>{t('coverage')}</h2><p>{t('coverage_scope')}</p>
      <div className="valuation-table"><table data-testid="checkpoint-coverage-table"><thead><tr>{(['metric', 'valid', 'nonpositive', 'other_missing', 'common'] as const).map(k => <th key={k}>{t(k)}</th>)}</tr></thead><tbody>{data.coverage.rows.map(r => <tr key={r.metric}><th>{v(r.metric)}</th><td>{num(r.valid)} / {num(r.quoted)}</td><td>{num(r.nonpositive)}</td><td>{num(r.missing_other)}</td><td>{num(r.common_five)}</td></tr>)}</tbody></table></div>
      <details className="valuation-detail"><summary>{t('strata_title')}</summary><h3>{v(metric)}</h3>
        <div className="valuation-table"><table data-testid="checkpoint-strata-table"><thead><tr>{(['stratum', 'valid', 'median', 'p05'] as const).map(k => <th key={k}>{t(k)}</th>)}</tr></thead><tbody>{strata.map(r => <tr key={r.dimension + r.stratum}><th>{t((r.dimension === 'size_bucket' ? `size_${r.stratum}` : r.stratum) as keyof typeof checkpointCopy)}{r.small_sample ? ` · ${t('small')}` : ''}</th><td>{num(r.valid)} / {num(r.quoted)}</td><td>{num(r.median)}</td><td>{num(r.p05)}</td></tr>)}</tbody></table></div>
      </details>
      <p>{t('industry_scope')}</p><p data-testid="checkpoint-industry">{v(metric)} · {t('industry_count')}: {industry.strata} / {industry.usable_strata} / {industry.small_sample_strata}</p>
    </section>
    <section className="panel" id="valuation-cases" data-testid="valuation-cases"><h2>{t('cases')}</h2><ol>{data.cases.map(c => <li key={c.kind}>{t(`case_${c.kind}` as keyof typeof checkpointCopy)}</li>)}</ol><p>{t('cases_limit')}</p>
      <details className="valuation-detail"><summary>{t('source')}</summary><p>{t('source_note')}</p><dl className="valuation-formulas">{Object.entries(data.source_sha256).map(([source, sha]) => <div key={source}><dt>{source}</dt><dd><code>{sha}</code></dd></div>)}</dl></details>
    </section>
  </div>;
}
