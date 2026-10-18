import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {buildMicrocapReport} from './content/microcap-report.server.ts';
import {windowRecheck,windowReviewMarkdown} from './content/microcap-window-review.ts';
for (const locale of ['en-US','zh-CN']) {
 test(`frozen ${locale} editions preserve the current report and prior bytes`,async()=>{
  const frozen=await readFile(`public/downloads/archive/microcap-research.v1.0.7.${locale}.md`,'utf8');
  const previous=await readFile(`public/downloads/archive/microcap-research.v1.0.6.${locale}.md`,'utf8');
  assert.equal(frozen,(await buildMicrocapReport(locale)).markdown);
  const prior=await readFile(`public/downloads/archive/microcap-research.pre-v1.0.0.3966176.${locale}.md`);
  assert.equal(createHash('sha256').update(prior).digest('hex'),locale==='en-US'?'73e508cc2fbfc9c4a4e5e65fd3f77bdcdc133d2621f99ef0b351a7d78cf9a066':'6e86b33badfc4c82fe780d80bbc77ebdf1e54997b3aa40e226a3c6a39a9dd539');
  assert.match(frozen,/1\.0\.7/);
  assert.match(previous,/1\.0\.6/);
  assert.ok(frozen.includes(windowReviewMarkdown(locale)));
 });
}
test('window recheck retains discrepancies rather than replacing history',()=>{
 for (const r of windowRecheck.slice(0,2)) r.fresh.forEach((v,i)=>assert.equal(v.toFixed(6),r.old[i].toFixed(6)));
 assert.ok(windowRecheck[2].old[0]-windowRecheck[2].fresh[0]>3);
 assert.ok(windowRecheck[2].fresh[0]<windowRecheck[1].fresh[0]);
 assert.equal(windowRecheck[2].sensitivity?.[0].toFixed(6),'6.255876');
 for(const locale of ['en-US','zh-CN']) {
  assert.match(windowReviewMarkdown(locale),/4\.224513/);
  assert.match(windowReviewMarkdown(locale),/6\.255876/);
 }
});

test('every earlier fixed edition retains its original bytes',async()=>{
 const hashes=JSON.parse(await readFile('tests/fixtures/microcap-archive-sha256.json','utf8'));
 for(const [name,expected] of Object.entries(hashes)){
  const bytes=await readFile(`public/downloads/archive/${name}`);
  assert.equal(createHash('sha256').update(bytes).digest('hex'),expected,name);
 }
});
