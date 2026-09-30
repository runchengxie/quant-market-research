import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { snapshotCards, localizeSnapshotCard } from './lib/data-catalog.ts';

test('catalog keeps missing coverage dates null and preserves status', () => {
  const cards = snapshotCards({ snapshots: { x: { generated_at: '2026-01-01', source: 'test', quality_status: 'pending', caveats: [] } } });
  assert.deepEqual(cards[0], { id: 'x', generatedAt: '2026-01-01', coverageStart: null, coverageEnd: null, status: 'pending', source: 'test', caveats: [] });
});

test('catalog rejects malformed manifests', () => {
  assert.throws(() => snapshotCards(null), /manifest/i);
  assert.throws(() => snapshotCards({ snapshots: [] }), /snapshots/i);
});

test('English snapshot presentation translates all published sources and caveats', async () => {
  const manifest = JSON.parse(await readFile(new URL('../public/data/manifest.json', import.meta.url), 'utf8'));
  const cards = snapshotCards(manifest).map((card) => localizeSnapshotCard(card, 'en-US'));
  for (const card of cards) {
    assert.doesNotMatch(card.source, /[\u4e00-\u9fff]/, `${card.id} source`);
    for (const caveat of card.caveats) assert.doesNotMatch(caveat, /[\u4e00-\u9fff]/, `${card.id} caveat`);
  }
});
