import { realpath } from 'node:fs/promises';
import { readFile } from 'node:fs/promises';
import { resolve, relative } from 'node:path';
import { publicDocs, type PublicDoc } from './public-registry';

export async function readPublicDocuments(repoRoot: string): Promise<Array<{ meta: PublicDoc; body: string }>> {
  const docsRoot = await realpath(resolve(repoRoot, 'docs'));
  const documents = [];
  for (const meta of publicDocs) {
    const file = resolve(repoRoot, meta.source);
    const actual = await realpath(file).catch(() => { throw new Error(`public document is missing: ${meta.source}`); });
    const rel = relative(docsRoot, actual);
    if (rel.startsWith('..') || rel.includes('..' + '\\') || rel.includes('..' + '/')) throw new Error(`public document escapes docs: ${meta.source}`);
    documents.push({ meta, body: await readFile(actual, 'utf8') });
  }
  return documents;
}

export function publicDocsLoader() {
  return { name: 'reviewed-public-documents', load: async () => { throw new Error('Use readPublicDocuments through the Astro page adapter.'); } };
}
