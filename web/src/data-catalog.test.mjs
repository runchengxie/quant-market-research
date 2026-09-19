import test from 'node:test';
import assert from 'node:assert/strict';
import { snapshotCards } from './lib/data-catalog.ts';

test('catalog keeps missing coverage dates null and preserves status', () => {
  const cards = snapshotCards({ snapshots: { x: { generated_at: '2026-01-01', source: 'test', quality_status: 'pending', caveats: [] } } });
  assert.deepEqual(cards[0], { id: 'x', generatedAt: '2026-01-01', coverageStart: null, coverageEnd: null, status: 'pending', source: 'test', caveats: [] });
});

test('catalog rejects malformed manifests', () => {
  assert.throws(() => snapshotCards(null), /manifest/i);
  assert.throws(() => snapshotCards({ snapshots: [] }), /snapshots/i);
});
