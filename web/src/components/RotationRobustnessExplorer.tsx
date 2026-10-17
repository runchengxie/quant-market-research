import { useEffect, useState } from 'react';
import { ResearchBarChart } from './ResearchCharts';
import { extText as t, codeText, percent, decimal, experimentText, windowText, dateText } from '../content/rotation-extension-display';
import { loadIndexedRelease, type RotationExtension, type ReleaseEntry } from '../content/rotation-extension';
type Measure = 'cagr' | 'total_return' | 'max_drawdown' | 'volatility' | 'cost_drag' | 'avg_bond_weight';
type Query = {
    group: string;
    allocator: string;
    cost: string;
    delay: string;
    window: string;
    metric: Measure;
};
const measures: Measure[] = ['cagr', 'total_return', 'max_drawdown', 'volatility', 'cost_drag', 'avg_bond_weight'];
function initial(): Query { const p = new URLSearchParams(typeof location === 'undefined' ? '' : location.search); return { group: p.get('robustGroup') ?? 'risk', allocator: p.get('robustAllocator') ?? 'fixed_slots', cost: p.get('robustCost') ?? '5', delay: p.get('robustDelay') ?? '1', window: p.get('robustWindow') ?? 'common', metric: measures.includes(p.get('robustMetric') as Measure) ? p.get('robustMetric') as Measure : 'max_drawdown' }; }
export default function RotationRobustnessExplorer({ evidence: seed, releaseEntry, dataBase }: {
    evidence: Pick<RotationExtension, 'robustness'>;
    releaseEntry: ReleaseEntry;
    dataBase: string;
}) {
    const [full, setFull] = useState<RotationExtension | null>(null), [loading, setLoading] = useState(false), [error, setError] = useState(false);
    const a = full ?? seed;
    async function loadRolling() { setLoading(true); setError(false); try {
        const value = await loadIndexedRelease(releaseEntry, new URL(dataBase, location.href).href);
        if (value.schema_version !== 'research.rotation_extension.v1')
            throw Error('Invalid schema');
        setFull(value as RotationExtension);
    }
    catch {
        setError(true);
    }
    finally {
        setLoading(false);
    } }
    const [q, setQ] = useState<Query>(initial), [ascending, setAscending] = useState(false);
    useEffect(() => { if (q.window.startsWith('rolling_') && !full && !loading && !error)
        void loadRolling(); }, [q.window, full, loading, error]);
    useEffect(() => { const pop = () => setQ(initial()); window.addEventListener('popstate', pop); return () => window.removeEventListener('popstate', pop); }, []);
    const groups = [...new Set(a.robustness.rows.map(r => r.group_id))];
    const group = groups.includes(q.group) ? q.group : groups[0];
    const allocators = [...new Set(a.robustness.rows.filter(r => r.group_id === group).map(r => r.allocator))];
    const allocator = allocators.includes(q.allocator) ? q.allocator : allocators[0];
    const windowIds = [...new Set(a.robustness.rows.filter(r => r.group_id === group && r.allocator === allocator).map(r => r.window_id))];
    const win = windowIds.includes(q.window) ? q.window : 'common';
    const cost = ['0', '5', '10'].includes(q.cost) ? Number(q.cost) : 5, delay = q.delay === '2' ? 2 : 1;
    const rows = a.robustness.rows.filter(r => r.group_id === group && r.allocator === allocator && r.window_id === win && r.cost_bps === cost && r.delay_sessions === delay).sort((x, y) => ((x.metrics?.[q.metric] ?? -Infinity) - (y.metrics?.[q.metric] ?? -Infinity)) * (ascending ? 1 : -1));
    function update(change: Partial<Query>) { const next = { ...q, ...change }; setQ(next); const url = new URL(location.href); for (const [k, v] of Object.entries(next))
        url.searchParams.set(`robust${k[0].toUpperCase()}${k.slice(1)}`, v); history.pushState(null, '', url); }
    const benchmarks = a.robustness.benchmarks.filter(r => r.group_id === group && r.allocator === allocator && r.cost_bps === cost && r.window_id === win);
    return <section id="rotation-robustness" className="panel rotation-extension"><h2>{t('robust')}</h2><p>{t('robustNote')}</p>
  {!full && <button onClick={loadRolling} disabled={loading}>{loading ? t('loading') : t('loadRolling')}</button>}{error && <p role="alert">{t('error')}</p>}
  <div className="extension-controls"><label>{t('group')}<select aria-label={t('group')} value={group} onChange={e => update({ group: e.target.value, window: 'common' })}>{groups.map(g => <option key={g} value={g}>{codeText(g)}</option>)}</select></label>
  <label>{t('allocator')}<select aria-label={t('allocator')} value={allocator} onChange={e => update({ allocator: e.target.value })}>{allocators.map(g => <option key={g} value={g}>{codeText(g)}</option>)}</select></label>
  <label>{t('cost')}<select aria-label={t('cost')} value={cost} onChange={e => update({ cost: e.target.value })}>{[0, 5, 10].map(n => <option key={n}>{n}</option>)}</select></label>
  <label>{t('delay')}<select aria-label={t('delay')} value={delay} onChange={e => update({ delay: e.target.value })}>{[1, 2].map(n => <option key={n}>{n}</option>)}</select></label>
  <label>{t('window')}<select aria-label={t('window')} value={win} onChange={e => update({ window: e.target.value })}>{windowIds.map(id => <option key={id} value={id}>{windowText(id)}</option>)}</select></label>
  <label>{t('metric')}<select aria-label={t('metric')} value={q.metric} onChange={e => update({ metric: e.target.value as Measure })}>{measures.map(m => <option key={m} value={m}>{t(m)}</option>)}</select></label></div>
  <p role="status" data-testid="robustness-period">{rows[0]?.period ? `${dateText(rows[0].period.start)} – ${dateText(rows[0].period.end)} · ${rows[0].period.sessions} ${t('sessions')}` : t('unavailable')}</p>
  {rows.some(r => r.metrics) && <ResearchBarChart rows={rows.filter(r => r.metrics).map(r => ({ name: experimentText(r.experiment_id), value: String(r.metrics![q.metric]) }))} labelKey="name" valueKey="value" formatter={percent}/>}
  <div className="table-scroll"><table><thead><tr><th>{t('configuration')}</th><th><button onClick={() => setAscending(!ascending)}>{t(q.metric)} {ascending ? '↑' : '↓'}</button></th><th>{t('cagr')}</th><th>{t('max_drawdown')}</th><th>{t('avg_bond_weight')}</th><th>{t('turnover')}</th></tr></thead><tbody>{rows.map(r => <tr key={r.id}><td>{experimentText(r.experiment_id)}</td><td>{r.metrics ? percent(r.metrics[q.metric]) : t('unavailable')}</td><td>{r.metrics ? percent(r.metrics.cagr) : '—'}</td><td>{r.metrics ? percent(r.metrics.max_drawdown) : '—'}</td><td>{r.metrics ? percent(r.metrics.avg_bond_weight) : '—'}</td><td>{decimal(r.turnover)}</td></tr>)}</tbody></table></div>
  {!rows.length && <p>{t('empty')}</p>}
  {benchmarks.length > 0 && <section><h3>{t('benchmarks')}</h3><p>{t('benchmarkNote')}</p><div className="table-scroll"><table><thead><tr><th>{t('configuration')}</th><th>{t('cagr')}</th><th>{t('max_drawdown')}</th><th>{t('period')}</th></tr></thead><tbody>{benchmarks.map(b => <tr key={b.benchmark_id}><td>{codeText(b.benchmark_id)}</td><td>{b.metrics ? percent(b.metrics.cagr) : t('unavailable')}</td><td>{b.metrics ? percent(b.metrics.max_drawdown) : '—'}</td><td>{b.period ? `${dateText(b.period.start)} – ${dateText(b.period.end)}` : t('unavailable')}</td></tr>)}</tbody></table></div></section>}
 </section>;
}
