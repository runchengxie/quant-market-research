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
    <div className="theme-heading"><div><span className="section-kicker">研究总览</span><h2>研究到了哪一步，有哪些发现？</h2><p>先看结论和待解决的问题，再到专题里查看数据、图表与计算方法。</p></div><span className="asof">数据日期按专题分别标注</span></div>
    <section className="featured-study" aria-label="Featured Quant Research study">
      <div>
        <span className="section-kicker">Featured Quant Research</span>
        <h2>18 年 A 股风格因子动态：收益、稳定性与市场阶段</h2>
        <p>这些风格因子在不同 A 股市场阶段是否持续存在？研究使用历史分组收益、年度阶段和相关性来回答这个问题；IC、样本外验证和统计显著性仍待补充。</p>
      </div>
      <a href={withBase(PUBLIC_ROUTES.styleFactors, import.meta.env?.BASE_URL ?? "/")}>阅读旗舰研究 ↗</a>
    </section>
    <section className="research-library" aria-label="研究目录">
      <div className="theme-heading library-heading"><div><span className="section-kicker">研究目录</span><h2>按问题进入报告</h2><p>每个专题把结论、证据、图表和限制放在同一页。方法附录仍保留在文档区。</p></div></div>
      <div className="domain-grid">
        <span className="domain-label">基本面与现金流</span><span className="domain-label">规模与微盘</span><span className="domain-label">因子与风格</span><span className="domain-label">市场与板块</span>
      </div>
    </section>
    <section className="evidence-grid" aria-label="各专题研究进展">
      <EvidenceCard title="现金流" href={withBase(PUBLIC_ROUTES.cashflow, import.meta.env?.BASE_URL ?? "/")} status={cashflow ? '指数数据已检查' : '数据暂不可用'}
        conclusion={cashflow ? cashflow.longest_completed_underwater_calendar_days == null ? '800现金流价格指数在样本内尚无完整的回本记录。' : `800现金流价格指数在样本内，最长一次从高点跌落后等待了 ${dayCount(cashflow.longest_completed_underwater_calendar_days)}才回本。` : '数据恢复后显示回本统计。'}
        date={cashflow ? `${cashflow.start} 至 ${cashflow.end}` : '数据暂不可用'}
        scope="供应商指数表现，价格回报与税前全收益分开比较。"
        limitation="自行复刻的成分股、权重和财务数据时点仍需验证。"
        next="继续核对官方规则与本地复刻结果。"/>
      <EvidenceCard title="小微盘" href={withBase(PUBLIC_ROUTES.microcap, import.meta.env?.BASE_URL ?? "/")} status={microcap ? '参考指数可供研究' : '数据暂不可用'}
        conclusion={microcap ? microcap.longest_completed_underwater_calendar_days == null ? '同花顺微盘在样本内尚无完整的回本记录。' : `同花顺微盘在样本内，最长一次完整回本等待为 ${dayCount(microcap.longest_completed_underwater_calendar_days)}。` : '数据恢复后显示微盘参考指数统计。'}
        date={microcap ? `${microcap.start} 至 ${microcap.end}` : '数据暂不可用'}
        scope="同花顺微盘用于观察微盘表现，中证2000和国证2000作为小盘对照。"
        limitation="自制400股版本有持仓缺报价的问题，收益需要重算。参考指数的分红处理也需核对。"
        next="先补齐估值，再检查停牌、退市与买卖成本。"/>
      <EvidenceCard title="长期风格" href={withBase(PUBLIC_ROUTES.indices, import.meta.env?.BASE_URL ?? "/")} status={styleAvailable ? '历史结果供研究参考' : '数据暂不可用'}
        conclusion={styleAvailable ? `已整理 ${history.factor_count} 个因子的历史结果，用于观察不同风格在各阶段的表现。` : '数据恢复后显示长期风格研究范围。'}
        date={styleAvailable ? `Barra 历史研究截至 ${history.coverage_end}` : '数据暂不可用'}
        scope="指数和ETF反映市场表现。Barra 多空研究观察高分组与低分组的收益差异。"
        limitation="信号在新数据中是否有效，以及借券、费用和保证金条件仍需验证。"
        next="分别阅读市场走势与因子结果，保留各自的数据口径。"/>
      <EvidenceCard title="低换手因子" href={withBase(PUBLIC_ROUTES.lowTurnover, import.meta.env?.BASE_URL ?? "/")} status="探索性研究"
        conclusion="低换手在控制规模、低波动和现有特征后仍保留历史条件相关性，但尚未证明能稳定转化为净收益。"
        date="共同样本 2019-05 至 2026-06" scope="比较原始换手、低波动、流动性和组合执行之间的关系。"
        limitation="正市盈率样本、未来缺价处理和交易成本仍需统一核验。"
        next="先比较避开高换手与主动买入低换手，再登记新的前瞻检验。"/>
    </section>
    <section className="featured-study study-intro" aria-label="后续探索执行协议">
      <div><span className="section-kicker">研究方法与下一步</span><h2>每项研究都有明确的证据状态和停止条件</h2><p>前瞻检验、微盘审计、Quality 重跑和 ETF 探索都记录输入快照、数据边界和结果状态。缺少必要数据时保留阻塞记录，不用估算值填补空白。</p></div>
      <a href={withBase("/docs/next-explorations/", import.meta.env?.BASE_URL ?? "/")}>查看后续探索协议 ↗</a>
    </section>
    <div className="fine-print"><span className="section-kicker">阅读提示</span><p>各专题的样本时间不同，历史最长等待也会受到样本范围影响。页面保留尚未回本和数据缺失的记录。历史结果仅供研究参考。</p></div>
  </>;
}

function EvidenceCard({title, href, status, conclusion, date, scope, limitation, next}: {
  title: string; href: string; status: string; conclusion: string; date: string; scope: string; limitation: string; next: string;
}) {
  return <article className="evidence-card"><span className="tag warm">{status}</span><h3>{title}</h3><p className="evidence-conclusion">{conclusion}</p>
    <dl><dt>数据范围</dt><dd>{date}</dd><dt>观察什么</dt><dd>{scope}</dd><dt>仍需验证</dt><dd>{limitation}</dd><dt>下一步</dt><dd>{next}</dd></dl><a href={href}>查看{title}专题 ↗</a></article>;
}
