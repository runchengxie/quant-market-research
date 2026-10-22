import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
test('home and directory share a static reading component without client-side data fetching',async()=>{
 const home=await readFile(new URL('./pages/index.astro',import.meta.url),'utf8');
 const directory=await readFile(new URL('./pages/research/index.astro',import.meta.url),'utf8');
 for(const page of [home,directory]){assert.match(page,/<ResearchDirectory/);assert.doesNotMatch(page,/client:(load|visible|idle)/);}
});
