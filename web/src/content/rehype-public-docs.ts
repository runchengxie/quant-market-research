import { publicDocs } from './public-registry';

const publicLocaleCompanions = new Set([
  'docs/index.zh-CN.md',
  'docs/research-closeout-status.zh-CN.md',
  'docs/research/factors/low-turnover.zh-CN.md',
  'docs/research/factors/pb-roe.zh-CN.md',
  'docs/research/factors/microcap.zh-CN.md',
  'docs/research/experiments/microcap-execution-diagnostic-20260928.zh-CN.md',
  'docs/research/factors/smallcap-turnover-history.zh-CN.md',
  'docs/research/factors/barra-factor-dictionary.zh-CN.md',
  'docs/research/factors/barra-source-inventory.zh-CN.md',
]);

function basePath(base: string, route: string) { return `${base.replace(/\/$/, '')}${route}`; }

export function resolveDocLink(source: string, href: string, base: string): string {
  if (/^(javascript|data|vbscript):/i.test(href)) throw new Error('unsafe public document link');
  if (/^(https?:|mailto:|tel:)/i.test(href) || href.startsWith('#')) return href;
  const [rawPath, fragment] = href.split('#', 2);
  const target = rawPath || source;
  const sourceDir = source.slice(0, source.lastIndexOf('/') + 1);
  const candidate = target.startsWith('/') ? target.slice(1) : `${sourceDir}${target}`;
  const parts: string[] = [];
  for (const part of candidate.split('/')) {
    if (!part || part === '.') continue;
    if (part === '..') {
      if (!parts.length) throw new Error(`public document link outside allowlist: ${href}`);
      parts.pop();
    } else parts.push(part);
  }
  const normalized = parts.join('/');
  const match = publicDocs.find((doc) => doc.source === normalized);
  if (match) return `${basePath(base, match.route)}${fragment ? `#${fragment}` : ''}`;
  if (publicLocaleCompanions.has(normalized)) {
    const slug = normalized.slice('docs/'.length).replace(/\.md$/, '');
    return `${basePath(base, `/docs/${slug}/`)}${fragment ? `#${fragment}` : ''}`;
  }
  throw new Error(`public document link outside allowlist: ${href}`);
}

export function publicDocsTransform(base = '/quant-market-research') {
  return (tree: any, file: any) => {
    const source = String(file.path ?? '').replaceAll('\\', '/').split('/docs/').pop() ? `docs/${String(file.path).replaceAll('\\', '/').split('/docs/').pop()}` : 'docs/index.md';
    const walk = (node: any) => {
      if (!node || typeof node !== 'object') return;
      if (node.type === 'element' && node.tagName === 'a' && typeof node.properties?.href === 'string') node.properties.href = resolveDocLink(source, node.properties.href, base);
      for (const child of node.children ?? []) walk(child);
    };
    walk(tree);
  };
}
