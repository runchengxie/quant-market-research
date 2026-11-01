import {chromium} from '@playwright/test';
import {readFileSync,writeFileSync,readdirSync,mkdirSync} from 'node:fs';
import {resolve,dirname,relative} from 'node:path';
import {proseFindings} from '../src/lib/prose-audit.ts';
const output=process.argv.find(x=>x.startsWith('--output='))?.slice(9);
const base=process.argv.find(x=>x.startsWith('--base='))?.slice(7)??'http://127.0.0.1:54838/quant-market-research/';
if(!output)throw Error('External --output= required');
const dist=resolve('dist'),paths=[];
function walk(dir){for(const x of readdirSync(dir,{withFileTypes:true})){const p=resolve(dir,x.name);if(x.isDirectory())walk(p);else if(x.name.endsWith('.html'))paths.push(relative(dist,p));}}
walk(dist);mkdirSync(dirname(resolve(output)),{recursive:true});
const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1280,height:900}});
const records=[];
try{
 for(const path of paths.sort())for(const lang of ['en-US','zh-CN']){
  const route=path==='index.html'?'':path.replace(/index\.html$/,'');
  const response=await page.goto(base+route+'?lang='+lang,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(lang=>document.documentElement.lang===lang,lang);
  await page.waitForTimeout(250);
  const paragraphs=await page.locator('main h1,main h2,main h3,main h4,main p,main summary,main label').evaluateAll(elements=>elements.filter(el=>el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden').map(el=>{const clone=el.cloneNode(true);clone.querySelectorAll('code,pre,select,svg').forEach(x=>x.remove());return (clone.textContent??'').trim();}).filter(Boolean));
  const issues=lang==='zh-CN'?paragraphs.flatMap(text=>proseFindings(text).map(x=>({text,...x}))):[];
  records.push({route:path,locale:lang,status:response?.status(),resolved_url:page.url(),paragraphs:paragraphs.length,issues});
  console.log(path,lang,'paragraphs',paragraphs.length,'flags',issues.length);
  writeFileSync(output,JSON.stringify({generated_route_count:paths.length,records},null,2)+'\n');
 }
}finally{await browser.close();}
