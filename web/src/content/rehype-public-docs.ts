import { publicDocs } from './public-registry';

function basePath(base: string, route: string) { return `${base.replace(/\/$/, '')}${route}`; }

export function resolveDocLink(source: string, href: string, base: string): string {
  if (/^(javascript|data|vbscript):/i.test(href)) throw new Error('unsafe public document link');
  if (/^(https?:|mailto:|tel:)/i.test(href) || href.startsWith('#')) return href;
  const [rawPath, fragment] = href.split('#', 2);
  const target = rawPath || source;
  const sourceDir = source.slice(0, source.lastIndexOf('/') + 1);
  const normalized = target.startsWith('/') ? target.slice(1) : `${sourceDir}${target}`;
  const match = publicDocs.find((doc) => doc.source === normalized.replace(/\.md$/, '.md'));
  if (!match) throw new Error(`public document link outside allowlist: ${href}`);
  return `${basePath(base, match.route)}${fragment ? `#${fragment}` : ''}`;
}

export function publicDocsTransform() {
  return (tree: any, file: any) => {
    const source = String(file.path ?? '').replaceAll('\\', '/').split('/docs/').pop() ? `docs/${String(file.path).replaceAll('\\', '/').split('/docs/').pop()}` : 'docs/index.md';
    const walk = (node: any) => {
      if (!node || typeof node !== 'object') return;
      if (node.type === 'element' && node.tagName === 'a' && typeof node.properties?.href === 'string') node.properties.href = resolveDocLink(source, node.properties.href, '/quant-market-research');
      for (const child of node.children ?? []) walk(child);
    };
    walk(tree);
  };
}
