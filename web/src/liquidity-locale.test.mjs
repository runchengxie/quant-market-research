import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { liquidityCaveats, liquidityCaveatTranslations } from './liquidity-copy.ts';

const summary = JSON.parse(readFileSync(new URL('../public/data/liquidity/summary.json', import.meta.url), 'utf8'));

test('English liquidity caveats have complete translations and do not mutate source data', () => {
  for (const note of summary.caveats) assert.ok(liquidityCaveatTranslations[note], `missing English copy for caveat: ${note}`);
  const original = [...summary.caveats];
  const rendered = liquidityCaveats(summary.caveats, 'en-US');
  assert.doesNotMatch(rendered, /[\u3400-\u9fff]/);
  assert.deepEqual(summary.caveats, original);
});

test('Chinese liquidity caveats preserve the source wording', () => {
  assert.equal(liquidityCaveats(summary.caveats, 'zh-CN'), summary.caveats.join(' '));
});
