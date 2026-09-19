import test from 'node:test';
import assert from 'node:assert/strict';
import { visibleSections } from './lib/topic-sections.ts';

test('topic navigation excludes unavailable sections', () => {
  assert.deepEqual(visibleSections([{ id: 'a', label: 'A', available: true }, { id: 'b', label: 'B', available: false }, { id: '', label: 'C', available: true }]), [{ id: 'a', label: 'A', available: true }]);
});
