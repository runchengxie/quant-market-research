import { useEffect, useState } from "react";
import { publicDataUrl } from "../lib/public-data";
import { formatPercent, formatNumber } from "../lib/format";

type Candidate = { candidate: string; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Capacity = { capital: number; net_annual_return: number; net_sharpe: number; max_drawdown: number; fill_ratio: number; avg_cash_weight: number };
type Window = { window_days: number; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Joint = { turnover_definition: string; rebalance_frequency: string; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Snapshot = { coverage: { start: string; end: string }; window_sensitivity: Window[]; candidates: Candidate[]; capacity: Capacity[]; joint_matrix: Joint[]; caveats: string[] };

const labels: Record<string, string> = { low_turnover: "低换手", small_cap: "小市值", composite: "复合信号", large_cap_control: "大市值对照", low_turnover_residual: "低换手残差" };
const labelsEn: Record<string, string> = { low_turnover: "Low turnover", small_cap: "Small cap", composite: "Composite signal", large_cap_control: "Large-cap control", low_turnover_residual: "Low-turnover residual" };
const pct = (value: number) => formatPercent(value / 100);

export default function LowTurnoverExecutionEvidence() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [locale, setLocale] = useState<"en-US" | "zh-CN">("en-US");
  useEffect(() => {
    setLocale(document.documentElement.lang === "zh-CN" ? "zh-CN" : "en-US");
    fetch(publicDataUrl("low_turnover_exploration.json", import.meta.env?.BASE_URL ?? "/"))
      .then((response) => response.ok ? response.json() : null)
      .then(setSnapshot)
      .catch(() => setSnapshot(null));
  }, []);
  if (!snapshot) return null;
  const t = (zh: string, en: string) => locale === "zh-CN" ? zh : en;

  const preferred = snapshot.candidates.filter((row) => ["low_turnover", "small_cap", "composite", "low_turnover_residual"].includes(row.candidate));
  const capacity = snapshot.capacity.filter((row) => row.capital >= 1_000_000);
  const joint = snapshot.joint_matrix;
  const windowScale = Math.max(2, Math.ceil(Math.max(0, ...snapshot.window_sensitivity.map((row) => row.net_annual_return)) / 2) * 2);

  return <section className="report-section" aria-label={t("低换手执行验证", "Low-turnover execution validation")}>
    <span className="section-kicker">{t("新增执行验证", "Additional execution tests")}</span>
    <h3>{t("统一账本下，低换手的优势会被成交约束削弱", "Under a unified ledger, trading constraints reduce the low-turnover advantage")}</h3>
    <p>{t("这次探索覆盖", "This exploration covers")} {snapshot.coverage.start} {t("至", "through")} {snapshot.coverage.end}{t("。下表使用同一份额账本、停牌和参与率规则比较候选组合，收益仍属于探索性结果。", ". The table compares candidate portfolios under a common share-based ledger, suspension treatment, and participation-rate rules. Returns remain exploratory.")}</p>
    <div className="table-scroll"><table><thead><tr>{[t("候选", "Candidate"), t("净年化", "Net annualized"), t("净夏普", "Net Sharpe"), t("最大回撤", "Max drawdown"), t("年化换手", "Annualized turnover")].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{preferred.map((row) => <tr key={row.candidate}><td>{(locale === "zh-CN" ? labels : labelsEn)[row.candidate] ?? row.candidate}</td><td>{pct(row.net_annual_return)}</td><td>{formatNumber(row.net_sharpe)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} {t("倍", "x")}</td></tr>)}</tbody></table></div>

    <p className="panel-note">{t("容量情景使用前一交易日成交额的 5% 参与率。资本达到 100 万元后，成交率仍低于完整成交，现金权重和延迟成交会影响结果。", "Capacity scenarios use a 5% participation rate of the previous trading day's traded value. Even at capital of CNY 1 million, fills remain incomplete; cash weight and delayed fills affect results.")}</p>
    <figure className="evidence-figure" aria-labelledby="capacity-chart-title"><figcaption id="capacity-chart-title">{t("不同资金规模的模拟成交率 · 0–100%", "Simulated fill ratio by capital · 0–100%")}</figcaption><div className="evidence-chart-rows">{capacity.map((row) => <div className="evidence-chart-row" key={row.capital}><span className="evidence-chart-label">{formatNumber(row.capital)} {t("元", "CNY")}</span><div className="evidence-chart-measure"><div className="evidence-bar-track"><span className="evidence-bar-fill" style={{ width: `${Math.max(0, Math.min(row.fill_ratio * 100, 100))}%` }} /></div><strong>{pct(row.fill_ratio * 100)}</strong></div><small>{t("平均现金", "Avg. cash")} {pct(row.avg_cash_weight * 100)}</small></div>)}</div><p className="evidence-figure-note">{t("柱长按成交率百分比绘制。模拟成交率和现金权重反映执行约束，不代表真实订单回报。", "Bar length represents fill ratio. Simulated fills and cash weights describe execution constraints, not actual order returns.")}</p></figure>
    <div className="table-scroll"><table><thead><tr>{[t("资金规模", "Capital"), t("净年化", "Net annualized"), t("成交率", "Fill ratio"), t("现金权重", "Cash weight"), t("最大回撤", "Max drawdown")].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{capacity.map((row) => <tr key={row.capital}><td>{formatNumber(row.capital)} {t("元", "CNY")}</td><td>{pct(row.net_annual_return)}</td><td>{pct(row.fill_ratio * 100)}</td><td>{pct(row.avg_cash_weight * 100)}</td><td>{pct(row.max_drawdown)}</td></tr>)}</tbody></table></div>
    <p className="panel-note">{t("这些数据使用成交额代理和模型化冲击，不能代替真实成交回报。完整字段见", "These data use traded-value proxies and modeled market impact; they are not actual execution returns. See the complete fields in the ")}<a href={publicDataUrl("low_turnover_exploration.json", import.meta.env?.BASE_URL ?? "/")}>{t("公开快照", "public snapshot")}</a>.</p>

    <h4>{t("换手窗口与调仓频率", "Turnover windows and rebalance frequency")}</h4>
    <p className="panel-note">{t("在月频账本中，较长的换手观察窗口同时降低换手和回撤。窗口变化也会改变持仓名单，因此只能作为稳健性比较。", "In the monthly ledger, longer turnover windows reduce both turnover and drawdown. Window changes also change portfolio membership, so this is a robustness comparison only.")}</p>
    <figure className="evidence-figure" aria-labelledby="window-chart-title"><figcaption id="window-chart-title">{t("月频账本的换手观察窗口 · 净年化收益 0–", "Turnover lookback in the monthly ledger · net annualized return 0–")}{windowScale}%</figcaption><div className="evidence-chart-rows">{snapshot.window_sensitivity.map((row) => <div className="evidence-chart-row" key={row.window_days}><span className="evidence-chart-label">{row.window_days} {t("日平均", "day average")}</span><div className="evidence-chart-measure"><div className="evidence-bar-track"><span className="evidence-bar-fill" style={{ width: `${Math.max(0, Math.min(row.net_annual_return / windowScale * 100, 100))}%` }} /></div><strong>{pct(row.net_annual_return)}</strong></div><small>{t("回撤", "Drawdown")} {pct(row.net_max_drawdown)} · {t("年化换手", "Annualized turnover")} {formatNumber(row.annualized_turnover)} {t("倍", "x")}</small></div>)}</div><p className="evidence-figure-note">{t("柱长为同一月频模拟账本的净年化收益；回撤和换手一同列出，不能由收益柱长判断风险大小。", "Bar length shows net annualized return in the same monthly simulation ledger. Drawdown and turnover are shown alongside it; bar length alone does not indicate risk.")}</p></figure>
    <div className="table-scroll"><table><thead><tr>{[t("平均换手窗口", "Average turnover window"), t("净年化", "Net annualized"), t("净夏普", "Net Sharpe"), t("最大回撤", "Max drawdown"), t("年化换手", "Annualized turnover")].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{snapshot.window_sensitivity.map((row) => <tr key={row.window_days}><td>{row.window_days} {t("日", "days")}</td><td>{pct(row.net_annual_return)}</td><td>{formatNumber(row.net_sharpe)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} {t("倍", "x")}</td></tr>)}</tbody></table></div>
    <p className="panel-note">{t("联合网格显示，调仓频率对结果的影响大于均值和中位数的细微差别。双周调仓的净年化约 17%–21%，月度约 8%–14%，但回撤仍约 -59% 至 -69%。", "The joint grid suggests rebalance frequency affects results more than the small differences between mean and median turnover. Net annualized returns are about 17%–21% for biweekly rebalancing and 8%–14% monthly, while drawdowns remain around -59% to -69%.")}</p>
    <div className="table-scroll"><table><thead><tr>{[t("换手窗口", "Turnover window"), t("调仓频率", "Rebalance frequency"), t("净年化", "Net annualized"), t("最大回撤", "Max drawdown"), t("年化换手", "Annualized turnover")].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{joint.map((row) => <tr key={`${row.turnover_definition}-${row.rebalance_frequency}`}><td>{row.turnover_definition}</td><td>{row.rebalance_frequency}</td><td>{pct(row.net_annual_return)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} {t("倍", "x")}</td></tr>)}</tbody></table></div>
  </section>;
}
