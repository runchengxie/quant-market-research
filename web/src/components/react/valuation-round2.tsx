import { useState } from 'react';
import { ResourceState, useJson } from './research-shared';
import type { Round2Evidence } from '../../lib/valuation-round2';
import { round2Copy as c } from '../../content/valuation-round2-copy';
import { valuationCopy } from '../../content/valuation-groups-copy';
import { checkpointCopy } from '../../content/valuation-checkpoint-copy';
import { withBase } from '../../lib/routes';

export function ValuationEvidenceDirectory({ english }: { english: boolean }) {
 const lang = english ? 0 : 1;
 const t = (key: keyof typeof c) => c[key][lang];
 const link = (route: string) => withBase(route, import.meta.env.BASE_URL) + '?lang=' + (english ? 'en-US' : 'zh-CN');
 const entries = [
  ['annual','annual_note','checked','#valuation-annual'],
  ['definitions','definitions_note','checked','#valuation-definitions'],
  ['factors','factors_note','exploratory','#valuation-evidence'],
  ['ledger','ledger_note','exploratory','#valuation-ledger'],
  ['persistence','persistence_note','exploratory','#valuation-persistence'],
  ['round2','round2_note','exploratory','#valuation-round2'],
  ['freeze','freeze_note','pending','#valuation-validation'],
 ] as const;
 return <section className="panel" id="valuation-directory" data-testid="valuation-directory">
  <h2>{t('directory')}</h2><p>{t('directory_note')}</p>
  <div className="valuation-evidence-grid">{entries.map(([title,note,status,href]) => <article key={title}>
   <span className={'valuation-stage valuation-stage-' + status}>{t(status)}</span>
   <h3><a href={href}>{t(title)}</a></h3><p>{t(note)}</p>
  </article>)}</div>
  <details className="valuation-detail"><summary>{t('earlier')}</summary><nav className="report-links">
   {[
    ['denominator_link','/docs/research/experiments/valuation-denominators-20261018/'],
    ['panel_link','/docs/research/experiments/valuation-panel-20261018/'],
    ['template_link','/docs/research/experiments/financial-template-coverage-20261019/'],
    ['pbroe_link','/research/factors/pb-roe/'],
    ['style_link','/research/style-factors-18y/'],
   ].map(([label,route]) => <a key={route} href={link(route)}>{t(label as keyof typeof c)}</a>)}
  </nav></details>
 </section>;
}
export function ValuationRound2({ english }: { english: boolean }) {
 const resource = useJson<Round2Evidence>('valuation_round2_draft.json');
 const [metric,setMetric] = useState('pb_parent');
 const [scenario,setScenario] = useState('touch10');
 const [scope,setScope] = useState('A_unpriced_only');
 const [basis,setBasis] = useState('all_frozen');
 const [layer,setLayer] = useState('report_size_profitability');
 const [outcome,setOutcome] = useState('reference_0');
 const lang = english ? 0 : 1;
 const t = (key: keyof typeof c) => c[key][lang];
 const v = (key: string) => valuationCopy[key as keyof typeof valuationCopy]?.[lang] ?? key;
 const num = (n: number | null | undefined, percentage=false) => n == null ? t('missing') : new Intl.NumberFormat(english ? 'en-US' : 'zh-CN', { maximumFractionDigits: percentage ? 2 : 0, ...(percentage ? {style:'percent' as const} : {}) }).format(n);
 if (!resource.data) return <ResourceState loading={!resource.error} error={resource.error} retry={resource.retry} />;
 const data=resource.data;
 const rows=data.sensitivities.filter(r => r.metric===metric && r.scenario===scenario && r.scope===scope);
 const attrRows=data.attribution?.portfolios.filter(r=>r.metric===metric && r.scenario===scenario);
 const attrAnnual=data.attribution?.annual.filter(r=>r.metric===metric && r.scenario===scenario);
 const controlRows=data.controls?.rows.filter(r=>r.metric===metric && r.sample_basis===basis && r.layer===layer && r.outcome===outcome);
 const overlap=controlRows?.find(r=>r.stage==='overlap');
 const sample=(q:number,f:number) => rows.find(r => r.quintile===q && r.reference_fraction===f)!;
 return <div data-testid="valuation-round2">
  <section className="panel" id="valuation-round2">
   <span className="valuation-stage valuation-stage-exploratory">{t('exploratory')}</span>
   <h2>{t('sensitivity')}</h2><p>{t('sensitivity_note')}</p>
   <div className="callout valuation-coverage-warning" role="note" data-testid="round2-warning">{t('warning')}</div>
   <div className="valuation-controls">
    <label>{t('metric')}<select data-testid="round2-metric" value={metric} onChange={e=>setMetric(e.target.value)}>{['pb_parent','pe_deducted_proxy'].map(m=><option key={m} value={m}>{v(m)}</option>)}</select></label>
    <label>{t('scenario')}<select data-testid="round2-scenario" value={scenario} onChange={e=>setScenario(e.target.value)}>{(['touch10','close10','touch0','touch30'] as const).map(s=><option key={s} value={s}>{checkpointCopy[s][lang]}</option>)}</select></label>
    <label>{t('scope')}<select data-testid="round2-scope" value={scope} onChange={e=>setScope(e.target.value)}>{(['A_unpriced_only','B_all_remaining'] as const).map(s=><option key={s} value={s}>{t(s)}</option>)}</select></label>
   </div><p>{t('scope_note')}</p>
   <div className="valuation-table"><table data-testid="round2-sensitivity-table"><thead><tr>{(['q','fraction0','fraction50','fraction100','unresolved','unknown_reference','strict'] as const).map(k=><th key={k}>{t(k)}</th>)}</tr></thead>
   <tbody>{[1,2,3,4,5].map(q=>{const row=sample(q,0);return <tr key={q}><th>{q}</th>{[0,.5,1].map(f=><td key={f}>{num(sample(q,f).total_change,true)}</td>)}<td>{num(row.unresolved_lots)} / {num(row.valued_unexited_lots)}</td><td>{num(row.unknown_reference_lots)}</td><td>{num(row.strict_total_change,true)}</td></tr>})}</tbody></table></div>
  </section>
  <section className="panel" id="valuation-contribution" data-testid="round2-contribution"><span className={'valuation-stage valuation-stage-'+(data.attribution?'checked':'pending')}>{t(data.attribution?'checked':'pending')}</span><h2>{t('accounting')}</h2>
   {attrRows ? <><p>{t('accounting_note')}</p><h3>{v(metric)} · {checkpointCopy[scenario as keyof typeof checkpointCopy][lang]}</h3>
    <div className="valuation-table"><table data-testid="round2-attribution-table"><thead><tr>{(['q','gross','fees','closed','fraction0','fraction50','fraction100','strict','members','cash','opportunity'] as const).map(k=><th key={k}>{t(k)}</th>)}</tr></thead>
     <tbody>{attrRows.map(r=><tr key={r.quintile}><th>{r.quintile}</th><td>{num(r.gross_pnl_initial_0,true)}</td><td>{num(r.buy_fee_fraction_initial,true)} / {num(r.sell_fee_fraction_initial,true)}</td><td>{num(r.closed_lot_contribution_initial,true)} / {num(r.terminal_lot_contribution_initial_0,true)}</td><td>{num(r.contribution_initial_0,true)}</td><td>{num(r.contribution_initial_50,true)}</td><td>{num(r.contribution_initial_100,true)}</td><td>{num(r.contribution_initial_strict,true)}</td><td>{r.filled_buys} / {r.failed_buys} / {r.zero_budget_members}</td><td>{num(r.daily_mean_cash_fraction_initial,true)}</td><td>{num(r.interest_1pct_fraction_initial,true)}</td></tr>)}</tbody></table></div><p>{t('cash_note')}</p>
    <details className="valuation-detail"><summary>{t('annual_accounting')}</summary><p>{t('annual_accounting_note')}</p><div className="valuation-table"><table data-testid="round2-attribution-years"><thead><tr>{(['q','calendar_year','fraction0','strict','fees'] as const).map(k=><th key={k}>{t(k)}</th>)}</tr></thead><tbody>{attrAnnual?.map(r=><tr key={r.quintile+':'+r.calendar_year}><th>{r.quintile}</th><td>{r.calendar_year} · {r.start_date} / {r.end_date}</td><td>{num(r.contribution_initial_0,true)}</td><td>{num(r.contribution_initial_strict,true)}</td><td>{num(r.buy_fee_fraction_initial,true)} / {num(r.sell_fee_fraction_initial,true)}</td></tr>)}</tbody></table></div></details>
    </> : <p>{t('waiting')}</p>}
  </section>
  <section className="panel" id="valuation-controls" data-testid="round2-controls"><span className="valuation-stage valuation-stage-exploratory">{t('exploratory')}</span><h2>{t('controls')}</h2><p>{t('controls_note')}</p>
   {controlRows ? <><div className="valuation-controls">
    <label>{t('sample_basis')}<select value={basis} onChange={e=>setBasis(e.target.value)} data-testid="round2-control-basis">{(['all_frozen','common_five'] as const).map(k=><option key={k} value={k}>{t(k)}</option>)}</select></label>
    <label>{t('layer')}<select value={layer} onChange={e=>setLayer(e.target.value)} data-testid="round2-control-layer">{(['report_size','report_size_profitability','secondary_quality','secondary_leverage'] as const).map(k=><option key={k} value={k}>{t(k)}</option>)}</select></label>
    <label>{t('outcome')}<select value={outcome} onChange={e=>setOutcome(e.target.value)} data-testid="round2-control-outcome">{(['strict','reference_0','reference_50','reference_100'] as const).map(k=><option key={k} value={k}>{t(k)}</option>)}</select></label>
   </div><h3>{v(metric)} Q1 − Q{metric==='pb_parent'?2:3} · touch10</h3>
   <div className="valuation-table"><table data-testid="round2-controls-table"><thead><tr>{(['stage','months','missing_months','member_support','unknown_slots','retention','full_mean','supported_mean','positive'] as const).map(k=><th key={k}>{t(k)}</th>)}</tr></thead><tbody>{controlRows.map(r=><tr key={r.stage}><th>{t(r.stage as keyof typeof c)}</th><td>{r.supported_months} / {r.scheduled_months}</td><td>{r.missing_month_count}</td><td>{num(r.q1_member_slots)} / {num(r.comparison_member_slots)}</td><td>{num(r.q1_unknown_slots)} / {num(r.comparison_unknown_slots)}</td><td>{num(r.mean_q1_retention,true)} / {num(r.mean_comparison_retention,true)}</td><td data-testid="control-full-mean">{num(r.full_schedule_mean_contrast,true)}</td><td data-testid="control-supported-mean">{num(r.supported_month_mean_contrast,true)}</td><td>{num(r.supported_month_positive_share,true)}</td></tr>)}</tbody></table></div>
   {overlap && <><h3>{t('annual_controls')}</h3><p>{t('formation_year_note')}</p><div className="valuation-table"><table data-testid="round2-controls-years"><thead><tr>{(['year','months','missing_months','full_mean','supported_mean','positive'] as const).map(k=><th key={k}>{t(k)}</th>)}</tr></thead><tbody>{overlap.yearly.map(y=><tr key={y.formation_year}><th>{y.formation_year}</th><td>{y.supported_months} / {y.scheduled_months}</td><td>{y.missing_month_count}</td><td>{num(y.full_schedule_mean_contrast,true)}</td><td>{num(y.supported_month_mean_contrast,true)}</td><td>{num(y.supported_month_positive_share,true)}</td></tr>)}</tbody></table></div><p><strong>{t('bootstrap')}</strong> {num(overlap.bootstrap.low,true)} / {num(overlap.bootstrap.high,true)}</p><p>{t('bootstrap_note')}</p></>}
   </> : <p>{t('waiting')}</p>}{data.controls?.audit && <details className="valuation-detail" data-testid="control-audit"><summary>{t('audit_status')}</summary><p>{t('audit_note')}</p><p>{t(data.controls.audit.recovered_seal?'seal_recovered':'seal_complete')}</p><p>{data.controls.audit.bucket_aggregate_rows.toLocaleString(english?'en-US':'zh-CN')} · {t('checked')}</p></details>}<p>{t('coverage_selection')}</p><p>{t('strict_batch_note')}</p><p>{t('controls_limit')}</p>
  </section>
  <section className="panel" id="valuation-case-progress" data-testid="round2-case-progress"><span className={'valuation-stage valuation-stage-'+(data.case_progress?'checked':'pending')}>{t(data.case_progress?'checked':'pending')}</span><h2>{t('cases')}</h2><p>{t('cases_note')}</p>
   {data.case_progress ? <><p>{t('case_amount_note')}</p><div className="callout valuation-coverage-warning" role="note" data-testid="case-revision-warning">{t('case_revision_warning')}</div>
    <div className="valuation-evidence-grid">{data.case_progress.cases.map(row=><article key={row.case_key} data-testid={'case-'+row.case_key}>
     <h3>{row.company_label[lang]}</h3><p>{row.facts[0][lang]}</p>
     {row.case_key==='pe_unresolved_reference' && <p className="callout valuation-coverage-warning">{row.facts[2][lang]}</p>}
     <dl className="valuation-formulas"><div><dt>{t('case_gap')}</dt><dd>{num(row.gap_contribution_initial,true)}</dd></div><div><dt>{t('case_reference')}</dt><dd>{num(row.unresolved_reference_initial,true)}</dd></div><div><dt>{t('focal_dates')}</dt><dd>{row.formation_date} / {row.entry_date} / {row.exit_date??t('no_exit')}</dd></div></dl>
     <details className="valuation-detail"><summary>{t('case_detail')}</summary>{row.facts.slice(1).map((fact,i)=><p key={i}>{fact[lang]}</p>)}
      <p>{t('report_dates')} · {row.financial_report_period} / {row.official_publication_date}</p><p>{t('historical_ticker')} · {row.historical_ticker}</p>
      <h4>{t('open_gaps')}</h4>{row.gaps.map((gap,i)=><p key={i}>{gap[lang]}</p>)}<h4>{t('primary_sources')}</h4><ul>{row.sources.map(source=><li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{english?t(source.evidence_role as keyof typeof c):source.title_zh}</a> · {source.publication_date}</li>)}</ul>
     </details>
    </article>)}</div></> : <p>{t('waiting')}</p>}
  </section>
  <section className="panel" id="valuation-validation" data-testid="valuation-validation"><span className="valuation-stage valuation-stage-pending">{t('pending')}</span>
   <h2>{t('validation')}</h2><p>{t('retrospective')}</p>
   <dl className="valuation-formulas"><div><dt>{t('freeze_time')}</dt><dd>{data.freeze.frozen_at_utc}</dd></div><div><dt>{t('primary')}</dt><dd>{data.freeze.primary_contrasts.map(r=>v(r.metric)+' Q'+r.first+' − Q'+r.comparator).join(' / ')} · touch10</dd></div></dl><p data-testid="round2-forward">{t('forward')}</p>
   <details className="valuation-detail"><summary>{t('source')}</summary><dl className="valuation-formulas">{Object.entries(data.source_sha256).map(([key,hash])=><div key={key}><dt>{key}</dt><dd><code>{hash}</code></dd></div>)}</dl></details>
   <a href={withBase('/data/valuation_round2_draft.json',import.meta.env.BASE_URL)}>{t('download')}</a>
  </section>
 </div>;
}

export function ValuationRound2Findings({english}:{english:boolean}) {
 const resource=useJson<Round2Evidence>('valuation_round2_draft.json');
 const data=resource.data?.attribution;
 if(!data) return null;
 const lang=english?0:1,t=(key:keyof typeof c)=>c[key][lang];
 const pp=(value:number)=>new Intl.NumberFormat(english?'en-US':'zh-CN',{minimumFractionDigits:2,maximumFractionDigits:2,signDisplay:'always'}).format(value*100);
 const contrasts=(['pb_parent','pe_deducted_proxy'] as const).map(metric=>{
  const first=data.portfolios.find(r=>r.metric===metric&&r.scenario==='touch10'&&r.quintile===1)!;
  const other=data.portfolios.find(r=>r.metric===metric&&r.scenario==='touch10'&&r.quintile===(metric==='pb_parent'?2:3))!;
  return {metric,total:first.contribution_initial_0!-other.contribution_initial_0!,closed:first.closed_lot_contribution_initial-other.closed_lot_contribution_initial,
   terminal:first.terminal_lot_contribution_initial_0-other.terminal_lot_contribution_initial_0,
   interest:first.interest_1pct_fraction_initial-other.interest_1pct_fraction_initial};
 });
 return <section className="panel valuation-conclusions" data-testid="round2-findings"><span className="valuation-stage valuation-stage-exploratory">{t('exploratory')}</span><h2>{t('current')}</h2><p>{t('current_note')}</p>
  <div className="valuation-evidence-grid">{contrasts.map(r=><article key={r.metric}><h3>{t(r.metric==='pb_parent'?'gap_pb':'gap_pe')}</h3><dl className="valuation-formulas"><div><dt>{t('gap_total')}</dt><dd>{pp(r.total)}</dd></div><div><dt>{t('gap_closed')}</dt><dd>{pp(r.closed)}</dd></div><div><dt>{t('gap_terminal')}</dt><dd>{pp(r.terminal)}</dd></div></dl><p>{t(r.metric==='pb_parent'?'gap_pb_note':'gap_pe_note')}</p></article>)}</div>
  <p>{t('cash_gap_note').replace('{pb}',pp(contrasts[0].interest)).replace('{pe}',pp(contrasts[1].interest))}</p><a href="#valuation-contribution">{t('accounting')}</a>
 </section>;
}
