export type SearchRecord = { id: string; title: string; kind: 'research' | 'method' | 'factor' | 'data'; href: string; text: string; aliases: readonly string[] };

export function normalizeQuery(value: string): string { return Array.from(String(value ?? '').normalize('NFKC').trim().toLowerCase()).slice(0, 200).join(''); }

export function searchRecords(records: readonly SearchRecord[], query: string): SearchRecord[] {
  const normalized = normalizeQuery(query);
  if (!normalized) return [];
  const terms = normalized.split(/\s+/).filter(Boolean);
  return records.filter((record) => {
    const title = normalizeQuery(record.title);
    const aliases = record.aliases.map(normalizeQuery).join(' ');
    const body = normalizeQuery(`${record.text} ${record.id}`);
    return terms.every((term) => title.includes(term) || aliases.includes(term) || body.includes(term));
  }).sort((a, b) => a.id.localeCompare(b.id));
}
