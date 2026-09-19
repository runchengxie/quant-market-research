import { resolve } from 'node:path';
import { publicPages } from './public-registry';
import { readPublicDocuments } from './public-docs-loader';
import { readFactorRecords } from './factor-records.server';
import type { SearchRecord } from '../lib/search';

export async function buildSearchRecords(): Promise<SearchRecord[]> {
  const root = resolve(process.cwd(), '..');
  const records: SearchRecord[] = publicPages.filter((page) => page.section === 'research' || page.section === 'data').map((page) => ({ id: page.id, title: page.title, kind: page.section === 'data' ? 'data' : 'research', href: `/quant-market-research${page.route}`, text: `${page.summary} ${page.snapshotKeys.join(' ')}`, aliases: page.aliases }));
  const documents = await readPublicDocuments(root);
  for (const document of documents) records.push({ id: document.meta.id, title: document.meta.title, kind: 'method', href: `/quant-market-research${document.meta.route}`, text: document.body, aliases: document.meta.aliases });
  const factors = await readFactorRecords(root);
  for (const factor of factors.filter((record) => record.model !== 'core-proxy')) records.push({ id: `factor-${factor.key}`, title: factor.name, kind: 'factor', href: `/quant-market-research/research/style-factors-18y/?factor=${factor.factorId}#barra-factor-detail`, text: `${factor.feature} ${factor.calculation} ${factor.direction} ${factor.verification}`, aliases: [factor.factorId, factor.family] });
  return records;
}
