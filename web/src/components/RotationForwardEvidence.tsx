import { useState } from 'react';
import { extText as t, codeText, percent, decimal, dateText, experimentText } from '../content/rotation-extension-display';
import type { RotationExtension } from '../content/rotation-extension';
import RotationThemeEvidence from './RotationThemeEvidence';
export default function RotationForwardEvidence({ evidence: a }: {
    evidence: Pick<RotationExtension, 'sources' | 'forward' | 'theme'>;
}) {
    const [search, setSearch] = useState('');
    const f = a.forward;
    const symbols = a.sources.symbols.filter(r => r.symbol.includes(search.trim()));
    return <section className="panel rotation-extension" id="rotation-forward"><h2>{t('title')}</h2><p>{t('intro')}</p>
  <section><h3>{t('forward')}</h3><p className="extension-callout">{f.status === 'collecting' ? t('collecting') : t('waiting')}</p>
  <div className="rotation-facts"><div><strong>{f.captured_weeks}</strong>{t('captured')}</div><div><strong>{f.settled_weeks}</strong>{t('settled')}</div></div>
  {f.registration_id && <p>{t('registered')}: <code>{f.registration_id}</code>{f.effective_at && <> · {t('effective')}: {dateText(f.effective_at)}</>}</p>}
  {f.metrics && <p>{t('total_return')}: {percent(f.metrics.total_return)}</p>}
  {f.coverage.length > 0 && <div className="table-scroll"><table><thead><tr><th>{t('configuration')}</th><th>{t('captured')}</th><th>{t('settled')}</th><th>{t('total_return')}</th></tr></thead><tbody>{f.coverage.map(r => <tr key={r.experiment_id}><td>{experimentText(r.experiment_id)}</td><td>{r.captured_weeks}</td><td>{r.settled_weeks}</td><td>{r.metrics ? percent(r.metrics.total_return) : '—'}</td></tr>)}</tbody></table></div>}<p>{t('forwardNote')}</p>
  {f.missed_weeks.length > 0 && <details><summary>{t('missed')} ({f.missed_weeks.length})</summary><ul>{f.missed_weeks.map(r => <li key={r.week}>{dateText(r.week)} · {codeText(r.reason)}</li>)}</ul></details>}</section>
  <section id="rotation-sources"><h3>{t('sources')}</h3><p>{t('sourceNote')}</p><p>{dateText(a.sources.panel_start)} – {dateText(a.sources.panel_end)}</p>
   <label>{t('search')}<input type="search" value={search} onChange={e => setSearch(e.target.value)}/></label>
   <div className="table-scroll"><table><thead><tr><th>{t('symbol')}</th><th>{t('status')}</th><th>{t('reason')}</th></tr></thead><tbody>{symbols.map(r => <tr key={r.symbol}><td>{r.symbol}</td><td>{codeText(r.status)}</td><td>{codeText(r.reason)}</td></tr>)}</tbody></table></div>
   {!symbols.length && <p>{t('empty')}</p>}
   <details><summary>{t('sources')} · {a.sources.panel_count} / {a.sources.admitted_count}</summary><div className="table-scroll"><table><thead><tr><th>{t('symbol')}</th><th>{t('status')}</th><th>{t('median')}</th><th>{t('reason')}</th></tr></thead><tbody>{a.sources.reconciliation.map(r => <tr key={r.symbol}><td>{r.symbol}</td><td>{codeText(r.status)}</td><td>{decimal(r.median_amount)}</td><td>{codeText(r.reason)}</td></tr>)}</tbody></table></div></details>
   <p>{a.sources.recovered_symbols.map(s => <code key={s} style={{ marginRight: '1rem' }}>{s}</code>)}</p>
  </section><section><h3>{t('theme')}</h3><RotationThemeEvidence theme={a.theme}/></section>
 </section>;
}
