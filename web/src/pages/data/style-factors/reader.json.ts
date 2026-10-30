import { readStyleFactorReader } from '../../../content/style-factor-reader.server';
export const prerender = true;
export async function GET() {
  return new Response(JSON.stringify(await readStyleFactorReader()), { headers: { 'Content-Type': 'application/json' } });
}
