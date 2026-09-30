import { useEffect, useMemo, useState } from 'react';
import { searchRecords, type SearchRecord } from '../../lib/search';
import { withBase } from '../../lib/routes';

export default function SearchResults({ initialQuery = '', base = '/' }: { initialQuery?: string; base?: string }) {
  const [query, setQuery] = useState(() => initialQuery || (typeof window === 'undefined' ? '' : new URL(window.location.href).searchParams.get('q') ?? ''));
  const [records, setRecords] = useState<SearchRecord[] | null>(null);
  const [error, setError] = useState('');
  const [locale, setLocale] = useState<'en-US' | 'zh-CN'>('en-US');
  const t = (en: string, zh: string) => locale === 'en-US' ? en : zh;
  useEffect(() => { setLocale(document.documentElement.lang === 'zh-CN' ? 'zh-CN' : 'en-US'); }, []);
  useEffect(() => { fetch(withBase('/search-index.json', base)).then((response) => { if (!response.ok) throw new Error('Search index is temporarily unavailable'); return response.json(); }).then(setRecords).catch((reason) => setError(String(reason.message ?? reason))); }, [base]);
  useEffect(() => { const update = () => setQuery(new URL(window.location.href).searchParams.get('q') ?? ''); window.addEventListener('popstate', update); return () => window.removeEventListener('popstate', update); }, []);
  const matches = useMemo(() => records ? searchRecords(records.filter((record) => !record.locale || record.locale === locale), query).map((record) => locale === 'en-US' ? { ...record, title: record.titleEn ?? record.title, text: record.textEn ?? record.text } : record) : [], [records, query, locale]);
  const submit = (event: React.FormEvent) => { event.preventDefault(); const url = new URL(window.location.href); if (query) url.searchParams.set('q', query); else url.searchParams.delete('q'); window.history.pushState(null, '', url); };
  return <section className="search-results" aria-live="polite"><form onSubmit={submit}><label>{t('Search public research', '搜索公开研究')}<input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t('e.g. quality, low turnover, earnings stability', '例如：quality、低换手、盈利稳定性')} /></label><button type="submit">{t('Search', '搜索')}</button></form>{error && <div role="alert"><p>{error}</p><button type="button" onClick={() => window.location.reload()}>{t('Retry', '重试')}</button></div>}{!records ? !error && <p role="status">{t('Loading search index…', '正在加载搜索索引……')}</p> : !query ? <p role="status">{t('Enter a query to search research, methods, and factor definitions.', '输入关键词，搜索研究、方法与因子定义。')}</p> : <><p className="search-count">{t(`Found ${matches.length}; showing up to ${Math.min(30, matches.length)} results.`, `共找到 ${matches.length} 项，显示前 ${Math.min(30, matches.length)} 项`)}</p>{matches.length === 0 ? <p role="status">{t('No matches found.', '没有匹配内容。')}</p> : <div>{matches.slice(0, 30).map((record) => <article className="search-result" key={record.id}><span>{record.kind}</span><h2><a href={withBase(record.href, base)}>{record.title}</a></h2><p>{record.text.slice(0, 220)}</p></article>)}</div>}</>}</section>;
}
