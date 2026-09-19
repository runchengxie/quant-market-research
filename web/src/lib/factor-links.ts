import { normalizeFactor } from '../content/factors';
import { withBase } from './routes';

export function factorHref(target: string, factor: string | null, base: string, hash = ''): string {
  if (!target.startsWith('/') || target.startsWith('//') || target.includes('?') || target.includes('#')) {
    throw new Error('expected registered internal route');
  }
  const query = new URLSearchParams({ factor: normalizeFactor(factor) });
  return `${withBase(target, base)}?${query}${hash ? `#${encodeURIComponent(hash)}` : ''}`;
}
