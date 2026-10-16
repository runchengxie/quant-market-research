import { buildExclusionSvg } from '../../content/microcap-comparison.server';
import type { APIRoute } from 'astro';
import { buildMicrocapReport, buildWindowSvg, buildCandidateSvg, type ReportLocale } from '../../content/microcap-report.server';
export function getStaticPaths() {
  return (['en-US','zh-CN'] as const).flatMap(locale => [{params:{file:`microcap-research.${locale}.md`},props:{locale,format:'md'}},{params:{file:`microcap-windows.${locale}.svg`},props:{locale,format:'svg'}},{params:{file:`microcap-candidates.${locale}.svg`},props:{locale,format:'candidates'}},{params:{file:`microcap-exclusions.${locale}.svg`},props:{locale,format:'exclusions'}}]);
}
export const GET: APIRoute = async ({props}) => {
  const locale=props.locale as ReportLocale;
  const svg=props.format!=='md';
  const body=svg ? await (props.format==='exclusions'?buildExclusionSvg(locale):props.format==='candidates'?buildCandidateSvg(locale):buildWindowSvg(locale)) : (await buildMicrocapReport(locale)).markdown;
  return new Response(body,{headers:{'Content-Type':svg?'image/svg+xml; charset=utf-8':'text/markdown; charset=utf-8'}});
};
