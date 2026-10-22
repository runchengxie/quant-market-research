import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import { legacyAnchorMap } from './legacy-anchor-map';
import type { PublicDoc } from './public-registry';
import type { SearchRecord } from '../lib/search';
import { englishCopy } from './locale-copy';
const processor = createMarkdownProcessor();
const plain = (html: string) => html.replace(/<[^>]+>/g,' ').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/\s+/g,' ').trim();
export async function methodSections(meta: PublicDoc, body: string): Promise<SearchRecord[]> {
  const rendered=await (await processor).render(body);
  const headings=[...rendered.code.matchAll(/<h[1-6]\b[^>]*\bid="([^"]+)"[^>]*>([\s\S]*?)<\/h[1-6]>/g)];
  const legacy=legacyAnchorMap[meta.source]??[];
  const locale=meta.id.endsWith('-zh-CN')?'zh-CN':'en-US';
  const title=locale==='en-US'?englishCopy(meta).title:meta.title;
  if(!headings.length)return [{id:meta.id,title,kind:'method',href:meta.route,text:Array.from(plain(rendered.code)).slice(0,240).join(''),locale,aliases:[]}];
  return headings.map((h,i)=>({
    id:`${meta.id}-section-${i}`,title:`${title} · ${plain(h[2])}`,kind:'method',
    href:`${meta.route}#${legacy[i]??h[1]}`,
    text:Array.from(plain(rendered.code.slice(h.index!+h[0].length,headings[i+1]?.index??rendered.code.length))).slice(0,i===0?1200:240).join(''),
    locale,aliases:[],
  }));
}
