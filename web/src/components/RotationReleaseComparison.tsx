import { useState } from 'react';
import { isEnglish as englishLocale } from '../content/rotation-extension-display';
import { extensionCopy as c, codeCopy } from '../content/rotation-extension-copy';
import { loadIndexedRelease, type ReleaseIndex } from '../content/rotation-extension';
import { compareRotationReleases } from '../content/rotation-release-comparison';
const t = (k: keyof typeof c) => c[k][englishLocale() ? 0 : 1];
const reason = (code: string) => codeCopy[code]?.[englishLocale() ? 0 : 1] ?? t('unavailable');
export default function RotationReleaseComparison({ index, dataBase }: {
    index: ReleaseIndex;
    dataBase: string;
}) {
    const [left, setLeft] = useState(index.releases[0].release_id), [right, setRight] = useState(index.current_release_id);
    const [result, setResult] = useState<ReturnType<typeof compareRotationReleases> | null>(null), [state, setState] = useState('');
    const [limit, setLimit] = useState(30);
    async function compare() {
        setState('loading');
        setResult(null);
        try {
            const [a, b] = await Promise.all([left, right].map(id => loadIndexedRelease(index.releases.find(r => r.release_id === id)!, new URL(dataBase, location.href).href)));
            setResult(compareRotationReleases(a, b));
            setState('');
            setLimit(30);
        }
        catch {
            setState('error');
        }
    }
    return <section id="rotation-versions" className="panel rotation-extension"><h2>{t('versions')}</h2>
  <div className="extension-controls"><label>{t('left')}<select aria-label={t('left')} value={left} onChange={e => { setLeft(e.target.value); setResult(null); }}>{index.releases.map(r => <option key={r.release_id}>{r.release_id}</option>)}</select></label>
  <label>{t('right')}<select aria-label={t('right')} value={right} onChange={e => { setRight(e.target.value); setResult(null); }}>{index.releases.map(r => <option key={r.release_id}>{r.release_id}</option>)}</select></label>
  <button onClick={compare} disabled={state === 'loading'}>{t('compare')}</button></div>
  <p aria-live="polite">{state === 'loading' ? t('loading') : state === 'error' ? t('error') : ''}</p>
  {result && <><h3>{t('changes')}</h3><ul>{result.changes.map(code => <li key={code}>{reason(code)}</li>)}</ul>
   {result.status === 'incompatible' ? <p>{t('incompatible')}</p> : <div className="table-scroll"><table><thead><tr><th>{t('configuration')}</th><th>{t('status')}</th><th>{t('delta')}</th></tr></thead><tbody>{result.rows.slice(0, limit).map(r => <tr key={r.id}><td><code>{r.id}</code></td><td>{r.status === 'compatible' ? t('compatible') : r.status === 'incompatible' ? t('incompatible') : r.status === 'added' ? t('added') : t('removed')}</td><td>{r.cagr_delta === null ? '—' : new Intl.NumberFormat(englishLocale() ? 'en-US' : 'zh-CN', { maximumFractionDigits: 3, signDisplay: 'exceptZero' }).format(r.cagr_delta * 100)}</td></tr>)}</tbody></table></div>}
   {result.rows.length > limit && <button onClick={() => setLimit(limit + 30)}>{t('more')}</button>}</>}
 </section>;
}
