import { useEffect, useState } from "react";
import { publicDataUrl } from "../lib/public-data";
import { formatPercent, formatNumber } from "../lib/format";

type Candidate = { candidate: string; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Capacity = { capital: number; net_annual_return: number; net_sharpe: number; max_drawdown: number; fill_ratio: number; avg_cash_weight: number };
type Window = { window_days: number; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Joint = { turnover_definition: string; rebalance_frequency: string; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Snapshot = { coverage: { start: string; end: string }; window_sensitivity: Window[]; candidates: Candidate[]; capacity: Capacity[]; joint_matrix: Joint[]; caveats: string[] };

const labels: Record<string, string> = { low_turnover: "低换手", small_cap: "小市值", composite: "复合信号", large_cap_control: "大市值对照", low_turnover_residual: "低换手残差" };
const pct = (value: number) => formatPercent(value / 100);

export default function LowTurnoverExecutionEvidence() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  useEffect(() => {
    fetch(publicDataUrl("low_turnover_exploration.json", import.meta.env?.BASE_URL ?? "/"))
      .then((response) => response.ok ? response.json() : null)
      .then(setSnapshot)
      .catch(() => setSnapshot(null));
  }, []);
  if (!snapshot) return null;

  const preferred = snapshot.candidates.filter((row) => ["low_turnover", "small_cap", "composite", "low_turnover_residual"].includes(row.candidate));
  const capacity = snapshot.capacity.filter((row) => row.capital >= 1_000_000);
  const joint = snapshot.joint_matrix;
  const windowScale = Math.max(2, Math.ceil(Math.max(0, ...snapshot.window_sensitivity.map((row) => row.net_annual_return)) / 2) * 2);

  return <section className="report-section" aria-label="低换手执行验证">
    <span className="section-kicker">新增执行验证</span>
    <h3>统一账本下，低换手的优势会被成交约束削弱</h3>
    <p>这次探索覆盖 {snapshot.coverage.start} 至 {snapshot.coverage.end}。下表使用同一份额账本、停牌和参与率规则比较候选组合，收益仍属于探索性结果。</p>
    <div className="table-scroll"><table><thead><tr><th>候选</th><th>净年化</th><th>净夏普</th><th>最大回撤</th><th>年化换手</th></tr></thead><tbody>{preferred.map((row) => <tr key={row.candidate}><td>{labels[row.candidate] ?? row.candidate}</td><td>{pct(row.net_annual_return)}</td><td>{formatNumber(row.net_sharpe)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} 倍</td></tr>)}</tbody></table></div>

    <p className="panel-note">容量情景使用前一交易日成交额的 5% 参与率。资本达到 100 万元后，成交率仍低于完整成交，现金权重和延迟成交会影响结果。</p>
    <figure className="evidence-figure" aria-labelledby="capacity-chart-title"><figcaption id="capacity-chart-title">不同资金规模的模拟成交率 · 0–100%</figcaption><div className="evidence-chart-rows">{capacity.map((row) => <div className="evidence-chart-row" key={row.capital}><span className="evidence-chart-label">{formatNumber(row.capital)} 元</span><div className="evidence-chart-measure"><div className="evidence-bar-track"><span className="evidence-bar-fill" style={{ width: `${Math.max(0, Math.min(row.fill_ratio * 100, 100))}%` }} /></div><strong>{pct(row.fill_ratio * 100)}</strong></div><small>平均现金 {pct(row.avg_cash_weight * 100)}</small></div>)}</div><p className="evidence-figure-note">柱长按成交率百分比绘制。模拟成交率和现金权重反映执行约束，不代表真实订单回报。</p></figure>
    <div className="table-scroll"><table><thead><tr><th>资金规模</th><th>净年化</th><th>成交率</th><th>现金权重</th><th>最大回撤</th></tr></thead><tbody>{capacity.map((row) => <tr key={row.capital}><td>{formatNumber(row.capital)} 元</td><td>{pct(row.net_annual_return)}</td><td>{pct(row.fill_ratio * 100)}</td><td>{pct(row.avg_cash_weight * 100)}</td><td>{pct(row.max_drawdown)}</td></tr>)}</tbody></table></div>
    <p className="panel-note">这些数据使用成交额代理和模型化冲击，不能代替真实成交回报。完整字段见 <a href={publicDataUrl("low_turnover_exploration.json", import.meta.env?.BASE_URL ?? "/")}>公开快照</a>。</p>

    <h4>换手窗口与调仓频率</h4>
    <p className="panel-note">在月频账本中，较长的换手观察窗口同时降低换手和回撤。窗口变化也会改变持仓名单，因此只能作为稳健性比较。</p>
    <figure className="evidence-figure" aria-labelledby="window-chart-title"><figcaption id="window-chart-title">月频账本的换手观察窗口 · 净年化收益 0–{windowScale}%</figcaption><div className="evidence-chart-rows">{snapshot.window_sensitivity.map((row) => <div className="evidence-chart-row" key={row.window_days}><span className="evidence-chart-label">{row.window_days} 日平均</span><div className="evidence-chart-measure"><div className="evidence-bar-track"><span className="evidence-bar-fill" style={{ width: `${Math.max(0, Math.min(row.net_annual_return / windowScale * 100, 100))}%` }} /></div><strong>{pct(row.net_annual_return)}</strong></div><small>回撤 {pct(row.net_max_drawdown)} · 年化换手 {formatNumber(row.annualized_turnover)} 倍</small></div>)}</div><p className="evidence-figure-note">柱长为同一月频模拟账本的净年化收益；回撤和换手一同列出，不能由收益柱长判断风险大小。</p></figure>
    <div className="table-scroll"><table><thead><tr><th>平均换手窗口</th><th>净年化</th><th>净夏普</th><th>最大回撤</th><th>年化换手</th></tr></thead><tbody>{snapshot.window_sensitivity.map((row) => <tr key={row.window_days}><td>{row.window_days} 日</td><td>{pct(row.net_annual_return)}</td><td>{formatNumber(row.net_sharpe)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} 倍</td></tr>)}</tbody></table></div>
    <p className="panel-note">联合网格显示，调仓频率对结果的影响大于均值和中位数的细微差别。双周调仓的净年化约 17%–21%，月度约 8%–14%，但回撤仍约 -59% 至 -69%。</p>
    <div className="table-scroll"><table><thead><tr><th>换手窗口</th><th>调仓频率</th><th>净年化</th><th>最大回撤</th><th>年化换手</th></tr></thead><tbody>{joint.map((row) => <tr key={`${row.turnover_definition}-${row.rebalance_frequency}`}><td>{row.turnover_definition}</td><td>{row.rebalance_frequency}</td><td>{pct(row.net_annual_return)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} 倍</td></tr>)}</tbody></table></div>
  </section>;
}
