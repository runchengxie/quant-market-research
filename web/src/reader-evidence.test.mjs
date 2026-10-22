import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateReaderEvidence } from '../scripts/validate-reader-evidence.mjs';
const source = () => readFileSync(new URL('../public/data/low_turnover_reader.json', import.meta.url));
test('reviewed reader evidence rejects changed bytes before publishing', () => {
  assert.doesNotThrow(() => validateReaderEvidence(source()));
  const data = JSON.parse(source()); data.controls[3].spread = 1.18;
  assert.throws(() => validateReaderEvidence(Buffer.from(JSON.stringify(data))), /reviewed|hash/i);
});
test('reviewed reader evidence rejects the intermediate control under the full-control label', () => {
  const data = JSON.parse(source()); data.controls[3].id = 'plus_beta';
  assert.throws(() => validateReaderEvidence(Buffer.from(JSON.stringify(data))), /reviewed|hash|stage/i);
});
