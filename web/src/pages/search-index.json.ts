import { buildSearchRecords } from '../content/search-records.server';
export async function GET() {
  const body = JSON.stringify(await buildSearchRecords());
  if (Buffer.byteLength(body, 'utf8') > 250 * 1024) throw new Error('search index exceeds 250 KiB');
  return new Response(body, { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
}
