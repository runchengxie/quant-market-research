import {readFileSync,writeFileSync,readdirSync,mkdirSync} from 'node:fs';
import {resolve,relative,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {chineseProse,proseFindings,tidyChinesePunctuation} from '../src/lib/prose-audit.ts';
import {publicDocs,publicPages} from '../src/content/public-registry.ts';
const repo=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const output=process.argv.find(x=>x.startsWith('--output='))?.slice(9);
if(!output||resolve(output).startsWith(repo+'/'))throw new Error('Supply an external --output= report path');
const files=[];
function walk(dir){for(const item of readdirSync(dir,{withFileTypes:true})){const path=resolve(dir,item.name);if(item.isDirectory())walk(path);else if(/\.(ts|tsx|astro)$/.test(path)&&!path.includes('.test.'))files.push(path);}}
walk(resolve(repo,'web/src'));
for(const doc of publicDocs)files.push(resolve(repo,doc.source));
const findings=[],changes=[];
let spans=0;
for(const file of [...new Set(files)]){
 let source=readFileSync(file,'utf8');const initial=source;const prose=chineseProse(source,file);spans+=prose.length;
 if(process.argv.includes('--fix-punctuation')){
  for(const span of [...prose].reverse())source=source.slice(0,span.start)+tidyChinesePunctuation(span.text)+source.slice(span.end);
  if(source!==initial){writeFileSync(file,source);changes.push(relative(repo,file));}
 }
 for(const span of chineseProse(source,file)){
  const rules=proseFindings(span.text);
  if(rules.length)findings.push({file:relative(repo,file),line:source.slice(0,span.start).split('\n').length,text:span.text,rules:rules.map(x=>x.rule)});
 }
}
const report={scope:{source_files:new Set(files).size,registered_documents:publicDocs.length,registered_pages:publicPages.length,chinese_spans:spans,exclusions:['lookup keys','fenced/inline code','blockquoted source text','sealed research datasets']},changed_files:changes,findings};
mkdirSync(dirname(resolve(output)),{recursive:true});writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({scope:report.scope,changed_files:changes.length,flags:findings.length}));
