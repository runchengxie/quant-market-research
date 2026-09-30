import { resolve } from 'node:path';
import { publicPages } from './public-registry';
import { englishCopy } from './locale-copy';
import { readPublicDocuments } from './public-docs-loader';
import { readFactorRecords } from './factor-records.server';
import type { SearchRecord } from '../lib/search';

export async function buildSearchRecords(): Promise<SearchRecord[]> {
  const root = resolve(process.cwd(), '..');
  const records: SearchRecord[] = publicPages.filter((page) => page.section === 'research' || page.section === 'data').map((page) => { const en = englishCopy(page); return { id: page.id, title: page.title, titleEn: en.title, kind: page.section === 'data' ? 'data' : 'research', href: page.route, text: `${page.summary} ${page.snapshotKeys.join(' ')}`, textEn: `${en.summary} ${page.snapshotKeys.join(' ')}`, locale: 'en-US', aliases: page.aliases }; });
  const documents = await readPublicDocuments(root);
  for (const document of documents) {
    const chinese = document.meta.id.endsWith('-zh-CN');
    const en = englishCopy(document.meta);
    records.push({ id: document.meta.id, title: document.meta.title, titleEn: en.title, kind: 'method', href: document.meta.route, text: document.body, textEn: chinese ? undefined : document.body, locale: chinese ? 'zh-CN' : 'en-US', aliases: document.meta.aliases });
  }
  const factors = await readFactorRecords(root);
  for (const factor of factors.filter((record) => record.model !== 'core-proxy')) records.push({ id: `factor-${factor.key}`, title: factor.name, titleEn: factor.key, kind: 'factor', href: `/research/style-factors-18y/?factor=${factor.factorId}#barra-factor-detail`, text: `${factor.feature} ${factor.calculation} ${factor.direction} ${factor.verification}`, textEn: `${factor.key} ${factor.factorId}`, aliases: [factor.factorId, factor.family] });
  return records;
}
