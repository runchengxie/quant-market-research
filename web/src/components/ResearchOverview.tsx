import type { Snapshot } from './recovery-data';
import { PUBLIC_ROUTES, withBase } from '../lib/routes';

type BarraEvidence = {legacy_barra_result?: {coverage_start?: string; coverage_end?: string; factor_count?: number}};
const dayCount = (value: number | null) => value == null ? '尚未观察到完整回本区间' : `${value.toLocaleString('zh-CN')} 个自然日`;

export function OverviewContent({recovery, barra}: {recovery: Snapshot | null; barra: BarraEvidence | null}) {
  const available = (group: string) => !recovery?.issues.some(issue => !issue.group || issue.group === group);
  const cashflow = available('cashflow_price') ? recovery?.series.find(row => row.ts_code === '932368.CSI' && row.group === 'cashflow_price') : undefined;
  const microcap = available('microcap_vendor_close') ? recovery?.series.find(row => row.ts_code === '883418.TI' && row.group === 'microcap_vendor_close') : undefined;
  const history = barra?.legacy_barra_result;
  const styleAvailable = typeof history?.coverage_end === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(history.coverage_end)
    && typeof history.factor_count === 'number' && Number.isInteger(history.factor_count) && history.factor_count > 0;
  return <>
    <div className="theme-heading"><div><span className="section-kicker">研究总览</span><h1>从主要发现开始了解这些研究</h1><p>先浏览每项研究的结论和证据范围，再进入专题查看数据、图表与计算方法。</p></div><span className="asof">数据日期按专题分别标注</span></div>
    <section className="featured-study" aria-label="重点研究：18 年 A 股风格因子">
      <div>
        <span className="section-kicker">重点研究 · Barra 风格因子</span>
        <h2>18 年 A 股风格因子动态：收益、稳定性与市场阶段</h2>
        <p>这项研究帮助读者比较不同风格因子在 A 股各个市场阶段的表现。页面汇总历史分组收益、年度变化和因子相关性，IC、样本外验证与统计显著性仍在补充。</p>
        <div className="featured-facts" aria-label="研究范围"><span><strong>18 年</strong>历史样本</span><span><strong>19 个</strong>历史因子</span><span><strong>分年度</strong>和分阶段比较</span></div>
      </div>
      <a href={withBase(PUBLIC_ROUTES.styleFactors, import.meta.env?.BASE_URL ?? "/")}>进入风格因子研究 ↗</a>
    </section>
    <section className="research-library" aria-label="研究目录">
      <div className="theme-heading library-heading"><div><span className="section-kicker">研究目录</span><h2>按关心的问题进入报告</h2><p>每个专题都把结论、证据、图表和限制放在一起，详细方法与数据口径收录在文档区。</p></div></div>
    </section>
    <section className="evidence-grid overview-evidence-grid" aria-label="各专题研究进展">
      <EvidenceCard domain="基本面与现金流" title="现金流" href={withBase(PUBLIC_ROUTES.cashflow, import.meta.env?.BASE_URL ?? "/")} status={cashflow ? '指数数据已检查' : '数据暂不可用'}
        conclusion={cashflow ? cashflow.longest_completed_underwater_calendar_days == null ? '800现金流价格指数在样本内尚无完整的回本记录。' : `800现金流价格指数在样本内，最长一次从高点跌落后等待了 ${dayCount(cashflow.longest_completed_underwater_calendar_days)}才回本。` : '数据恢复后显示回本统计。'}
        date={cashflow ? `${cashflow.start} 至 ${cashflow.end}` : '数据暂不可用'}
        scope="供应商指数表现，价格回报与税前全收益分开比较。"/>
      <EvidenceCard domain="规模与微盘" title="小微盘" href={withBase(PUBLIC_ROUTES.microcap, import.meta.env?.BASE_URL ?? "/")} status={microcap ? '参考指数可供研究' : '数据暂不可用'}
        conclusion={microcap ? microcap.longest_completed_underwater_calendar_days == null ? '同花顺微盘在样本内尚无完整的回本记录。' : `同花顺微盘在样本内，最长一次完整回本等待为 ${dayCount(microcap.longest_completed_underwater_calendar_days)}。` : '数据恢复后显示微盘参考指数统计。'}
        date={microcap ? `${microcap.start} 至 ${microcap.end}` : '数据暂不可用'}
        scope="同花顺微盘用于观察微盘表现，中证2000和国证2000作为小盘对照。"/>
      <EvidenceCard domain="市场与板块" title="长期风格" href={withBase(PUBLIC_ROUTES.indices, import.meta.env?.BASE_URL ?? "/")} status={styleAvailable ? '历史结果供研究参考' : '数据暂不可用'}
        conclusion={styleAvailable ? `已整理 ${history.factor_count} 个因子的历史结果，用于观察不同风格在各阶段的表现。` : '数据恢复后显示长期风格研究范围。'}
        date={styleAvailable ? `Barra 历史研究截至 ${history.coverage_end}` : '数据暂不可用'}
        scope="指数和 ETF 反映市场表现，风格研究观察高分组与低分组的收益差异。"/>
      <EvidenceCard domain="因子与风格" title="低换手因子" href={withBase(PUBLIC_ROUTES.lowTurnover, import.meta.env?.BASE_URL ?? "/")} status="探索性研究"
        conclusion="低换手在控制规模、低波动和现有特征后仍保留历史条件相关性，但尚未证明能稳定转化为净收益。"
        date="共同样本 2019-05 至 2026-06" scope="比较原始换手、低波动、流动性和组合执行之间的关系。"/>
    </section>
    <div className="fine-print"><span className="section-kicker">阅读提示</span><p>各专题的样本时间不同，历史最长等待也会受到样本范围影响。页面保留尚未回本和数据缺失的记录。历史结果仅供研究参考。</p></div>
  </>;
}

function EvidenceCard({domain, title, href, status, conclusion, date, scope}: {
  domain: string; title: string; href: string; status: string; conclusion: string; date: string; scope: string;
}) {
  return <article className="evidence-card"><span className="section-kicker">{domain}</span><span className="tag warm">{status}</span><h3>{title}</h3><p className="evidence-conclusion">{conclusion}</p>
    <dl><dt>数据范围</dt><dd>{date}</dd><dt>观察什么</dt><dd>{scope}</dd></dl><a href={href}>查看{title}专题 ↗</a></article>;
}
