export type SearchRecord = { id: string; title: string; titleEn?: string; kind: 'research' | 'method' | 'factor' | 'data'; href: string; text: string; textEn?: string; locale?: 'en-US' | 'zh-CN'; aliases: readonly string[] };

function normalizeText(value: string): string { return String(value ?? '').normalize('NFKC').trim().toLowerCase(); }

export function normalizeQuery(value: string): string { return Array.from(normalizeText(value)).slice(0, 200).join(''); }

export function searchRecords(records: readonly SearchRecord[], query: string): SearchRecord[] {
  const normalized = normalizeQuery(query);
  if (!normalized) return [];
  const terms = normalized.split(/\s+/).filter(Boolean);
  return records.filter((record) => {
    const title = normalizeText(`${record.title} ${record.titleEn??''}`);
    const aliases = record.aliases.map(normalizeQuery).join(' ');
    const body = normalizeText(`${record.text} ${record.textEn??''} ${record.id}`);
    return terms.every((term) => title.includes(term) || aliases.includes(term) || body.includes(term));
  }).sort((a, b) => a.id.localeCompare(b.id));
}
