import type { APIRoute } from 'astro';
import { buildMicrocapReport, buildWindowSvg, type ReportLocale } from '../../content/microcap-report.server';
export function getStaticPaths() {
  return (['en-US','zh-CN'] as const).flatMap(locale => [{params:{file:`microcap-research.${locale}.md`},props:{locale,format:'md'}},{params:{file:`microcap-windows.${locale}.svg`},props:{locale,format:'svg'}}]);
}
export const GET: APIRoute = async ({props}) => {
  const locale=props.locale as ReportLocale;
  const svg=props.format==='svg';
  const body=svg ? await buildWindowSvg(locale) : (await buildMicrocapReport(locale)).markdown;
  return new Response(body,{headers:{'Content-Type':svg?'image/svg+xml; charset=utf-8':'text/markdown; charset=utf-8'}});
};
