import { buildFailureSvg, buildSizeSvg } from '../../content/microcap-agenda';
import { buildFollowupSvg } from '../../content/microcap-followup';
import { buildExclusionSvg } from '../../content/microcap-comparison.server';
import type { APIRoute } from 'astro';
import { buildMicrocapReport, buildWindowSvg, buildCandidateSvg, type ReportLocale } from '../../content/microcap-report.server';
export function getStaticPaths() {
  return (['en-US','zh-CN'] as const).flatMap(locale => [{params:{file:`microcap-research.${locale}.md`},props:{locale,format:'md'}},{params:{file:`microcap-windows.${locale}.svg`},props:{locale,format:'svg'}},{params:{file:`microcap-candidates.${locale}.svg`},props:{locale,format:'candidates'}},{params:{file:`microcap-exclusions.${locale}.svg`},props:{locale,format:'exclusions'}},{params:{file:`microcap-execution-followup.${locale}.svg`},props:{locale,format:'followup'}},{params:{file:`microcap-failure-atlas.${locale}.svg`},props:{locale,format:'failure'}},{params:{file:`microcap-size-liquidity.${locale}.svg`},props:{locale,format:'size'}}]);
}
export const GET: APIRoute = async ({props}) => {
  const locale=props.locale as ReportLocale;
  const svg=props.format!=='md';
  const body=svg ? await (props.format==='failure'?buildFailureSvg(locale):props.format==='size'?buildSizeSvg(locale):props.format==='followup'?buildFollowupSvg(locale):props.format==='exclusions'?buildExclusionSvg(locale):props.format==='candidates'?buildCandidateSvg(locale):buildWindowSvg(locale)) : (await buildMicrocapReport(locale)).markdown;
  return new Response(body,{headers:{'Content-Type':svg?'image/svg+xml; charset=utf-8':'text/markdown; charset=utf-8'}});
};
