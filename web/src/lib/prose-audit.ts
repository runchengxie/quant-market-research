/** Extract reader prose without editing literal keys, formulas or fenced code. */
import ts from 'typescript';
export type ProseSpan={start:number;end:number;text:string};
const chinese=/[\u3400-\u9fff]/;

export function chineseProse(source:string,file:string):ProseSpan[]{
 const spans:ProseSpan[]=[];
 if(/\.mdx?$/.test(file)){
  let offset=0,fenced=false;
  for(const line of source.split(/(?<=\n)/)){
   if(/^\s*(```|~~~)/.test(line)){fenced=!fenced;offset+=line.length;continue;}
   if(!fenced&&!/^\s*>\s*(?:原文|原始引文|引用来源|摘录)/.test(line)&&chinese.test(line))spans.push({start:offset,end:offset+line.length,text:line});
   offset+=line.length;
  }
  return spans;
 }
 const parse=(body:string,offset:number,jsx:boolean)=>{
  const tree=ts.createSourceFile(file,body,ts.ScriptTarget.Latest,true,jsx?ts.ScriptKind.TSX:ts.ScriptKind.TS);
  const visit=(node:ts.Node)=>{
   if(ts.isStringLiteralLike(node)||node.kind===ts.SyntaxKind.TemplateHead||node.kind===ts.SyntaxKind.TemplateMiddle||node.kind===ts.SyntaxKind.TemplateTail){
    const parent=node.parent;
    const key=(ts.isPropertyAssignment(parent)||ts.isPropertySignature(parent)||ts.isPropertyDeclaration(parent))&&parent.name===node;
    if(!key&&!ts.isElementAccessExpression(parent)){
     const raw=node.getText(tree);const tail=node.kind===ts.SyntaxKind.TemplateHead||node.kind===ts.SyntaxKind.TemplateMiddle?2:1;
     const text=raw.slice(1,-tail);const start=offset+node.getStart(tree)+1;
     if(chinese.test(text))spans.push({start,end:start+text.length,text});
    }
   }else if(ts.isJsxText(node)&&chinese.test(node.getText(tree))){
    const ancestor=node.parent;
    const script=ts.isJsxElement(ancestor)&&['script','style'].includes(ancestor.openingElement.tagName.getText(tree));
    if(!script){const text=node.getText(tree);const start=offset+node.getStart(tree);spans.push({start,end:start+text.length,text});}
   }
   ts.forEachChild(node,visit);
  };visit(tree);
 };
 if(file.endsWith('.astro')){
  const front=source.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  let begin=0;
  if(front){const start=source.indexOf(front[1]);parse(front[1],start,false);begin=front[0].length;}
  const body=source.slice(begin);const markup=body.replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/g,block=>block.replace(/[^\n]/g,' '));parse('<>'+markup+'</>',begin-2,true);
  for(const match of body.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)){const start=begin+match.index!+match[0].indexOf(match[1]);parse(match[1],start,false);}
 }else parse(source,0,/\.tsx$/.test(file));
 return spans.sort((a,b)=>a.start-b.start).filter((span,i,all)=>i===0||span.start!==all[i-1].start);
}

export function tidyChinesePunctuation(text:string):string{
 const chunks=text.split(/(`+[^`]*`+)/);
 return chunks.map((piece,index)=>{
  if(index%2)return piece;
  const protectedRanges:[number,number][]=[];
  for(const match of piece.matchAll(/[A-Za-z_$][\w.$]*\(/g)){
   const start=match.index!;let level=1,end=start+match[0].length;
   for(;end<piece.length&&level;end++){if(piece[end]==='(')level++;if(piece[end]===')')level--;}
   if(level===0)protectedRanges.push([start,end]);
  }
  const tokens:string[]=[];
  let masked=piece;
  for(const [start,end] of protectedRanges.filter(([start],i,a)=>!a.some(([lo,hi],j)=>j<i&&start>=lo&&start<hi)).reverse()){
   const token=`\u0001${tokens.length}\u0002`;tokens.push(piece.slice(start,end));masked=masked.slice(0,start)+token+masked.slice(end);
  }
  masked=masked.replace(/^(?:读公式时|回顾性验证|先看结论)：/,'').replace(/：(?=\s*$)/gm,' ').replace(/：/g,masked.length<80?' ':'。').replace(/；/g,'。').replace(/“|”/g,'').replace(/\(([^()\n]*[\u3400-\u9fff][^()\n]*)\)/g,'（$1）').replace(/([\u3400-\u9fff])\(([^()\n]*)\)/g,'$1（$2）');
  return masked.replace(/\u0001(\d+)\u0002/g,(_,n)=>tokens[Number(n)]);
 }).join('');
}

export function proseFindings(text:string){
 const plain=text.replace(/\\n/g,'\n').replace(/`+[^`]*`+/g,'').replace(/^(?:ln|sign|sqrt|log)\([^。]*。/,'');
 const rules:[string,RegExp][]=[
  ['rhetorical_reversal',/不是[^。！？\n]{0,120}而是|不在于[^。！？\n]{0,120}而在于|你以为|表面上[^。！？\n]{0,80}实际上|与其说|不重要[^。！？\n]{0,80}重要的是/],
  ['canned_or_jargon',/说白了|值得注意的是|先说结论|赋能|抓手|闭环|底层逻辑/],
  ['chinese_punctuation',/[；“”：]|——|\([^\n()]*[\u3400-\u9fff][^\n()]*\)/],
 ];
 const out=rules.filter(([,pattern])=>pattern.test(plain)).map(([rule])=>({rule}));
 for(const sentence of plain.split(/[。！？\n|]/)){
  if((sentence.match(/的/g)||[]).length>=4)out.push({rule:'repeated_de'});
  if((sentence.match(/[\u3400-\u9fff]/g)||[]).length>90)out.push({rule:'long_sentence'});
 }
 return out;
}
