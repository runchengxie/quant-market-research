import { useEffect, useState } from "react";
import { publicDataUrl } from "../lib/public-data";
import { formatPercent, formatNumber } from "../lib/format";

type Candidate = { candidate: string; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Capacity = { capital: number; net_annual_return: number; net_sharpe: number; max_drawdown: number; fill_ratio: number; avg_cash_weight: number };
type Snapshot = { coverage: { start: string; end: string }; candidates: Candidate[]; capacity: Capacity[]; caveats: string[] };

const labels: Record<string, string> = { low_turnover: "低换手", small_cap: "小市值", composite: "复合信号", large_cap_control: "大市值对照", low_turnover_residual: "低换手残差" };
const pct = (value: number) => formatPercent(value / 100);

export default function LowTurnoverExecutionEvidence() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  useEffect(() => { fetch(publicDataUrl("low_turnover_exploration.json", import.meta.env?.BASE_URL ?? "/")).then((response) => response.ok ? response.json() : null).then(setSnapshot).catch(() => setSnapshot(null)); }, []);
  if (!snapshot) return null;
  const preferred = snapshot.candidates.filter((row) => ["low_turnover", "small_cap", "composite", "low_turnover_residual"].includes(row.candidate));
  const capacity = snapshot.capacity.filter((row) => row.capital >= 1_000_000);
  return <section className="report-section" aria-label="低换手执行验证"><span className="section-kicker">新增执行验证</span><h3>统一账本下，低换手的优势会被成交约束削弱</h3><p>这次探索覆盖 {snapshot.coverage.start} 至 {snapshot.coverage.end}。下表使用同一份额账本、停牌和参与率规则比较候选组合，收益仍属于探索性结果。</p><div className="table-scroll"><table><thead><tr><th>候选</th><th>净年化</th><th>净夏普</th><th>最大回撤</th><th>年化换手</th></tr></thead><tbody>{preferred.map((row) => <tr key={row.candidate}><td>{labels[row.candidate] ?? row.candidate}</td><td>{pct(row.net_annual_return)}</td><td>{formatNumber(row.net_sharpe)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} 倍</td></tr>)}</tbody></table></div><p className="panel-note">容量情景使用前一交易日成交额的 5% 参与率。资本达到 100 万元后，成交率仍低于完整成交，现金权重和延迟成交会影响结果。</p><div className="table-scroll"><table><thead><tr><th>资金规模</th><th>净年化</th><th>成交率</th><th>现金权重</th><th>最大回撤</th></tr></thead><tbody>{capacity.map((row) => <tr key={row.capital}><td>{formatNumber(row.capital)} 元</td><td>{pct(row.net_annual_return)}</td><td>{pct(row.fill_ratio * 100)}</td><td>{pct(row.avg_cash_weight * 100)}</td><td>{pct(row.max_drawdown)}</td></tr>)}</tbody></table></div><p className="panel-note">这些数据使用成交额代理和模型化冲击，不能代替真实成交回报。完整字段见 <a href={publicDataUrl("low_turnover_exploration.json", import.meta.env?.BASE_URL ?? "/")}>公开快照</a>。</p></section>;
}
