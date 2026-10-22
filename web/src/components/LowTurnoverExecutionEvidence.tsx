import { useEffect, useState } from "react";
import { publicDataUrl } from "../lib/public-data";
import { formatPercent, formatNumber } from "../lib/format";
import { executionCopy, executionLabels } from "../content/low-turnover-execution-copy";

type Candidate = { candidate: string; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Capacity = { capital: number; net_annual_return: number; net_sharpe: number; max_drawdown: number; fill_ratio: number; avg_cash_weight: number };
type Window = { window_days: number; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Joint = { turnover_definition: string; rebalance_frequency: string; net_annual_return: number; net_max_drawdown: number; net_sharpe: number; annualized_turnover: number };
type Snapshot = { coverage: { start: string; end: string }; window_sensitivity: Window[]; candidates: Candidate[]; capacity: Capacity[]; joint_matrix: Joint[]; caveats: string[] };

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
  const t = (key: keyof typeof executionCopy) => executionCopy[key][locale === "zh-CN" ? 1 : 0];

  const label = (value: string) => executionLabels[value]?.[locale === "zh-CN" ? 1 : 0] ?? value;

  const preferred = snapshot.candidates.filter((row) => ["low_turnover", "small_cap", "composite", "low_turnover_residual"].includes(row.candidate));
  const capacity = snapshot.capacity.filter((row) => row.capital >= 1_000_000);
  const joint = snapshot.joint_matrix;
  const windowScale = Math.max(2, Math.ceil(Math.max(0, ...snapshot.window_sensitivity.map((row) => row.net_annual_return)) / 2) * 2);

  return <section className="report-section" aria-label={t('low_turnover_execution_validation')}>
    <span className="section-kicker">{t('kicker')}</span>
    <h3>{t('heading')}</h3>
    <p>{t('coverage')} {snapshot.coverage.start} {t('through')} {snapshot.coverage.end}{t('scope')}</p>
    <p className="panel-note">{t('tableGuide')}</p>
    <div className="table-scroll"><table><thead><tr>{[t('candidate'), t('net_annualized'), t('net_sharpe'), t('max_drawdown'), t('annualized_turnover')].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{preferred.map((row) => <tr key={row.candidate}><td>{label(row.candidate)}</td><td>{pct(row.net_annual_return)}</td><td>{formatNumber(row.net_sharpe)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} {t('x')}</td></tr>)}</tbody></table></div>

    <p className="panel-note">{t('capacityNote')}</p>
    <figure className="evidence-figure" aria-labelledby="capacity-chart-title"><figcaption id="capacity-chart-title">{t('capacityChart')}</figcaption><div className="evidence-chart-rows">{capacity.map((row) => <div className="evidence-chart-row" key={row.capital}><span className="evidence-chart-label">{formatNumber(row.capital)} {t('cny')}</span><div className="evidence-chart-measure"><div className="evidence-bar-track"><span className="evidence-bar-fill" style={{ width: `${Math.max(0, Math.min(row.fill_ratio * 100, 100))}%` }} /></div><strong>{pct(row.fill_ratio * 100)}</strong></div><small>{t('avg_cash')} {pct(row.avg_cash_weight * 100)}</small></div>)}</div><p className="evidence-figure-note">{t('capacityGuide')}</p></figure>
    <div className="table-scroll"><table><thead><tr>{[t('capital'), t('net_annualized'), t('fill_ratio'), t('cash_weight'), t('max_drawdown')].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{capacity.map((row) => <tr key={row.capital}><td>{formatNumber(row.capital)} {t('cny')}</td><td>{pct(row.net_annual_return)}</td><td>{pct(row.fill_ratio * 100)}</td><td>{pct(row.avg_cash_weight * 100)}</td><td>{pct(row.max_drawdown)}</td></tr>)}</tbody></table></div>
    <p className="panel-note">{t('snapshotNote')}<a href={publicDataUrl("low_turnover_exploration.json", import.meta.env?.BASE_URL ?? "/")}>{t('public_snapshot')}</a>{t('sentenceEnd')}</p>

    <h4>{t('turnover_windows_and_rebalance_frequency')}</h4>
    <p className="panel-note">{t('windowNote')}</p>
    <figure className="evidence-figure" aria-labelledby="window-chart-title"><figcaption id="window-chart-title">{t('windowChart')}{windowScale}%</figcaption><div className="evidence-chart-rows">{snapshot.window_sensitivity.map((row) => <div className="evidence-chart-row" key={row.window_days}><span className="evidence-chart-label">{row.window_days} {t('day_average')}</span><div className="evidence-chart-measure"><div className="evidence-bar-track"><span className="evidence-bar-fill" style={{ width: `${Math.max(0, Math.min(row.net_annual_return / windowScale * 100, 100))}%` }} /></div><strong>{pct(row.net_annual_return)}</strong></div><small>{t('drawdown')} {pct(row.net_max_drawdown)} · {t('annualized_turnover')} {formatNumber(row.annualized_turnover)} {t('x')}</small></div>)}</div><p className="evidence-figure-note">{t('windowGuide')}</p></figure>
    <div className="table-scroll"><table><thead><tr>{[t('average_turnover_window'), t('net_annualized'), t('net_sharpe'), t('max_drawdown'), t('annualized_turnover')].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{snapshot.window_sensitivity.map((row) => <tr key={row.window_days}><td>{row.window_days} {t('days')}</td><td>{pct(row.net_annual_return)}</td><td>{formatNumber(row.net_sharpe)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} {t('x')}</td></tr>)}</tbody></table></div>
    <p className="panel-note">{t('jointNote')}</p>
    <div className="table-scroll"><table><thead><tr>{[t('turnover_window'), t('rebalance_frequency'), t('net_annualized'), t('max_drawdown'), t('annualized_turnover')].map((label) => <th key={label}>{label}</th>)}</tr></thead><tbody>{joint.map((row) => <tr key={`${row.turnover_definition}-${row.rebalance_frequency}`}><td>{label(row.turnover_definition)}</td><td>{label(row.rebalance_frequency)}</td><td>{pct(row.net_annual_return)}</td><td>{pct(row.net_max_drawdown)}</td><td>{formatNumber(row.annualized_turnover)} {t('x')}</td></tr>)}</tbody></table></div>
  </section>;
}
