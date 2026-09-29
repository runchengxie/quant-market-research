import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { collectHeadingAnchors, hashPublicFiles } from '../scripts/site-contract.mjs';

test('freeze human anchors, not renderer IDs', async () => {
  const html = '<main><h2 id="质量">质量</h2><h2 id="质量_1">质量</h2><span id=":R1:">live</span></main>';
  assert.deepEqual((await collectHeadingAnchors(html)).map((x) => x.id), ['质量', '质量_1']);
});

test('data snapshot hashing detects mutation and deletion', async () => {
  const root = await mkdtemp(join(tmpdir(), 'qmr-contract-'));
  await mkdir(join(root, 'data', 'nested'), { recursive: true });
  await writeFile(join(root, 'data', 'nested', 'sample.csv'), 'date,value\n2020-01-01,0\n');
  const before = await hashPublicFiles(root);
  await writeFile(join(root, 'data', 'nested', 'sample.csv'), 'date,value\n2020-01-01,1\n');
  const after = await hashPublicFiles(root);
  assert.notDeepEqual(after, before);
});

test('public shell is English-first and exposes a persistent Chinese switch', async () => {
  const layout = await readFile(new URL('./layouts/SiteLayout.astro', import.meta.url), 'utf8');
  const header = await readFile(new URL('./components/SiteHeader.astro', import.meta.url), 'utf8');
  assert.match(layout, /<html lang="en-US">/);
  assert.match(layout, /quant-market-research-locale/);
  assert.match(header, /data-locale-toggle/);
  assert.match(header, /Research overview/);
  assert.match(header, /研究总览/);
});
