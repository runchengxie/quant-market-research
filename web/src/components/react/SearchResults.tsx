import { useEffect, useMemo, useState } from 'react';
import { searchRecords, type SearchRecord } from '../../lib/search';

export default function SearchResults({ initialQuery = '' }: { initialQuery?: string }) {
  const [query, setQuery] = useState(() => initialQuery || (typeof window === 'undefined' ? '' : new URL(window.location.href).searchParams.get('q') ?? ''));
  const [records, setRecords] = useState<SearchRecord[] | null>(null);
  const [error, setError] = useState('');
  useEffect(() => { fetch('/quant-market-research/search-index.json').then((response) => { if (!response.ok) throw new Error('搜索索引暂时不可用'); return response.json(); }).then(setRecords).catch((reason) => setError(String(reason.message ?? reason))); }, []);
  useEffect(() => { const update = () => setQuery(new URL(window.location.href).searchParams.get('q') ?? ''); window.addEventListener('popstate', update); return () => window.removeEventListener('popstate', update); }, []);
  const matches = useMemo(() => records ? searchRecords(records, query) : [], [records, query]);
  const submit = (event: React.FormEvent) => { event.preventDefault(); const url = new URL(window.location.href); if (query) url.searchParams.set('q', query); else url.searchParams.delete('q'); window.history.pushState(null, '', url); };
  return <section className="search-results" aria-live="polite"><form onSubmit={submit}><label>搜索公开研究<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="例如：quality、低换手、盈利稳定性" /></label><button type="submit">搜索</button></form>{error && <div role="alert"><p>{error}</p><button type="button" onClick={() => window.location.reload()}>重试</button></div>}{!records ? !error && <p role="status">正在加载搜索索引……</p> : !query ? <p role="status">输入关键词，搜索研究、方法与因子定义。</p> : <><p className="search-count">共找到 {matches.length} 项，显示前 {Math.min(30, matches.length)} 项</p>{matches.length === 0 ? <p role="status">没有匹配内容。</p> : <div>{matches.slice(0, 30).map((record) => <article className="search-result"><span>{record.kind}</span><h2><a href={record.href}>{record.title}</a></h2><p>{record.text.slice(0, 220)}</p></article>)}</div>}</>}</section>;
}
