import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { sourceNotes, sourceNoteTranslationsForAudit } from './microcap-copy.ts';

const data = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));

test('English micro-cap caveat presentation translates every published source note without changing source records', () => {
  const previousDocument = globalThis.document;
  globalThis.document = {documentElement: {lang: 'en-US'}};
  try {
    const sources = [
      data('../public/data/smallcap_turnover.json').caveats,
      data('../public/data/microcap_repair_summary.json').caveats,
      data('../public/data/index/microcap/summary.json').caveats,
      data('../public/data/index/microcap/reconstructed_summary.json').caveats,
      data('../public/data/microcap_history_2008_2014.json').caveats,
      data('../public/data/microcap_history_2008_2014.json').audit_notes,
    ];
    for (const notes of sources) {
      for (const note of notes) assert.ok(sourceNoteTranslationsForAudit[note], `missing English copy for source note: ${note}`);
      const rendered = sourceNotes(notes);
      assert.doesNotMatch(rendered, /[\u3400-\u9fff]/);
      assert.doesNotMatch(rendered, /untranslated research note/i);
    }
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
  }
});

test('Chinese micro-cap caveat presentation preserves source records and pricing boundaries', () => {
  const previousDocument = globalThis.document;
  globalThis.document = {documentElement: {lang: 'zh-CN'}};
  try {
    const notes = data('../public/data/microcap_repair_summary.json').caveats;
    const original=JSON.stringify(notes);
    const rendered=sourceNotes(notes);
    assert.match(rendered,/strict严格计价/);
    assert.match(rendered,/敏感性比较/);
    assert.match(rendered,/suspend_d/);
    assert.doesNotMatch(rendered,/；/);
    assert.equal(JSON.stringify(notes),original);
  } finally {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
  }
});
