import { resolve } from 'node:path';
import { publicPages } from './public-registry';
import { englishCopy } from './locale-copy';
import { readPublicDocuments } from './public-docs-loader';
import { readFactorRecords } from './factor-records.server';
import type { SearchRecord } from '../lib/search';
import { methodSections } from './search-sections.server';

export async function buildSearchRecords(): Promise<SearchRecord[]> {
  const root = resolve(process.cwd(), '..');
  const records: SearchRecord[] = publicPages.filter((page) => page.section === 'research' || page.section === 'data').map((page) => { const en = englishCopy(page); return { id: page.id, title: page.title, titleEn: en.title, kind: page.section === 'data' ? 'data' : 'research', href: page.route, text: `${page.summary} ${page.snapshotKeys.join(' ')}`, textEn: `${en.summary} ${page.snapshotKeys.join(' ')}`, aliases: page.aliases }; });
  const documents = await readPublicDocuments(root);
  for (const document of documents) {
    records.push(...await methodSections(document.meta,document.body));
  }
  const factors = await readFactorRecords(root);
  for (const factor of factors.filter((record) => record.model !== 'core-proxy')) records.push({ id: `factor-${factor.key}`, title: factor.name, titleEn: factor.key, kind: 'factor', href: `/research/style-factors-18y/?factor=${factor.factorId}#barra-factor-detail`, text: `${factor.feature} ${factor.calculation} ${factor.direction} ${factor.verification}`, textEn: `${factor.key} ${factor.factorId}`, aliases: [factor.factorId, factor.family] });
  return records;
}
