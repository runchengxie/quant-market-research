import { useEffect, useState } from "react";
import RotationThemeEvidence from "./RotationThemeEvidence";
import {extText} from "../content/rotation-extension-display";
import { ResearchBarChart } from "./ResearchCharts";
import {
  englishLocale,
  SortableTable,
  SimpleTable,
} from "./react/research-shared";
import {
  weeklyRows,
  groupLabels,
  type Copy,
  type Group,
} from "../content/rotation-research";
import {
  evidenceCopy as copy,
  stateCopy,
  limitationCopy,
} from "../content/rotation-evidence-copy";
import {
  selectComparison,
  selectAttribution,
  selectReplay,
  loadReplay,
  type RotationEvidence,
  type Metrics,
} from "../content/rotation-evidence";
const text = (v: Copy) => v[englishLocale() ? 0 : 1];
const t = (k: keyof typeof copy) => text(copy[k]);
const label = (id: string) => {
  const row = weeklyRows.find((r) => r.id === id);
  return row ? text(row.label) : id;
};
const pct = (v: number | null) =>
  v === null ? t("unavailable") : `${(v * 100).toFixed(2)}%`;
const dateLabel = (s: string) =>
  new Intl.DateTimeFormat(englishLocale() ? "en-US" : "zh-CN", {
    timeZone: "UTC",
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(`${s}T00:00:00Z`));
const states = (key: string) =>
  stateCopy[key] ? text(stateCopy[key]) : t("unavailable");
type Query = {
  groupId: string;
  windowId: string;
  allocator: string;
  date: string;
};
function query(): Query {
  const p = new URLSearchParams(location.search);
  const groupId = p.get("rotationGroup") ?? "risk";
  const group = ["risk", "pool", "holdover", "score"].includes(groupId)
    ? groupId
    : "risk";
  const allocator =
    p.get("rotationAllocator") ??
    (group === "pool" ? "defensive" : "fixed_slots");
  return {
    groupId: group,
    windowId: ["common", "last_252", "last_756"].includes(
      p.get("rotationWindow") ?? "",
    )
      ? p.get("rotationWindow")!
      : "common",
    allocator:
      group === "pool"
        ? "defensive"
        : group === "holdover" || group === "score"
          ? "fixed_slots"
          : ["fixed_slots", "defensive", "growth"].includes(allocator)
            ? allocator
            : "fixed_slots",
    date: p.get("rotationDate") ?? "",
  };
}
export default function RotationEvidenceExplorer({
  evidence,
  releaseUrl,
  releaseSha,
}: {
  evidence: RotationEvidence;
  releaseUrl: string;
  releaseSha: string;
}) {
  const [q, setQ] = useState<Query>(query),
    [measure, setMeasure] = useState<keyof Metrics | "avg_bond_weight">(
      "max_drawdown",
    );
  const [full, setFull] = useState<RotationEvidence | null>(null),
    [error, setError] = useState(false),
    [loading, setLoading] = useState(false),
    [variant, setVariant] = useState("fixed-base"),
    [filter, setFilter] = useState("all"),
    [contributor, setContributor] = useState("");
  useEffect(() => {
    const pop = () => setQ(query());
    window.addEventListener("popstate", pop);
    return () => window.removeEventListener("popstate", pop);
  }, []);
  function update(next: Partial<Query>) {
    const value = { ...q, ...next };
    if (value.groupId === "pool") value.allocator = "defensive";
    if (["holdover", "score"].includes(value.groupId))
      value.allocator = "fixed_slots";
    const url = new URL(location.href);
    for (const [key, v] of Object.entries({
      rotationGroup: value.groupId,
      rotationWindow: value.windowId,
      rotationAllocator: value.allocator,
      rotationDate: value.date,
    })) {
      if (v) url.searchParams.set(key, v);
      else url.searchParams.delete(key);
    }
    history.pushState(null, "", url);
    setQ(value);
  }
  async function fetchReplay() {
    setLoading(true);
    setError(false);
    try {
      const data = await loadReplay(releaseUrl, releaseSha);
      setFull(data);
    } catch {
      setError(true);
      setFull(null);
    } finally {
      setLoading(false);
    }
  }
  const counts = {
    registered: evidence.experiments.length,
    reproduced: evidence.experiments.filter(
      (e) => !e.evidence_stage.startsWith("unavailable"),
    ).length,
    missing: evidence.experiments.filter((e) =>
      e.evidence_stage.startsWith("unavailable"),
    ).length,
  };
  const c = selectComparison(evidence, q),
    rows = c.members;
  const contributionView = selectAttribution(evidence, {
    comparisonId: c.id,
    windowId: q.windowId,
  });
  const contributions =
    contributionView.status === "available" ? contributionView.rows : [];
  const active =
    contributions.find((r) => r.experiment_id === contributor) ??
    contributions[0];
  const availableReplays =
    full?.replay
      .filter((r) => r.experiment_id === variant)
      .sort((a, b) => a.signal_date.localeCompare(b.signal_date)) ?? [];
  const selectedDate = q.date || availableReplays.at(-1)?.signal_date || "";
  const replay = full
    ? selectReplay(full, { date: selectedDate, experimentId: variant })
    : null;
  const index =
    replay?.status === "available"
      ? availableReplays.findIndex(
          (r) => r.signal_date === replay.record.signal_date,
        )
      : -1;
  const metrics: [keyof Metrics | "avg_bond_weight", (v: number) => string][] =
    [
      ["total_return", pct],
      ["cagr", pct],
      ["max_drawdown", pct],
      ["sharpe_zero_rf", (v) => v.toFixed(3)],
      ["avg_bond_weight", pct],
    ];
  return (
    <section
      className="panel evidence-workbench"
      id="rotation-evidence"
      aria-labelledby="evidence-title"
    >
      <h2 id="evidence-title">{t("title")}</h2>
      <p>{t("intro")}</p>
      <p className="panel-note">
        {t("coverage").replace(
          /\{(registered|reproduced|missing)\}/g,
          (_, k: keyof typeof counts) =>
            new Intl.NumberFormat(englishLocale() ? "en-US" : "zh-CN").format(
              counts[k],
            ),
        )}
      </p>
      <div className="rotation-controls">
        <label className="rotation-control">
          {t("group")}
          <select
            aria-label={t("group")}
            value={q.groupId}
            onChange={(e) => update({ groupId: e.target.value })}
          >
            {(Object.keys(groupLabels) as Group[]).map((k) => (
              <option key={k} value={k}>
                {text(groupLabels[k])}
              </option>
            ))}
          </select>
        </label>
        <label className="rotation-control">
          {t("window")}
          <select
            aria-label={t("window")}
            value={q.windowId}
            onChange={(e) => update({ windowId: e.target.value })}
          >
            {(["common", "last_252", "last_756"] as const).map((k) => (
              <option key={k} value={k}>
                {t(k)}
              </option>
            ))}
          </select>
        </label>
        <label className="rotation-control">
          {t("allocator")}
          <select
            aria-label={t("allocator")}
            value={q.allocator}
            onChange={(e) => update({ allocator: e.target.value })}
          >
            {(["fixed_slots", "defensive", "growth"] as const)
              .filter(
                (k) =>
                  q.groupId === "risk" ||
                  k === (q.groupId === "pool" ? "defensive" : "fixed_slots"),
              )
              .map((k) => (
                <option key={k} value={k}>
                  {t(k)}
                </option>
              ))}
          </select>
        </label>
        <label className="rotation-control">
          {t("measure")}
          <select
            aria-label={t("measure")}
            value={measure}
            onChange={(e) => setMeasure(e.target.value as typeof measure)}
          >
            {metrics.map(([k]) => (
              <option key={k} value={k}>
                {t(k)}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p role="status" data-testid="comparison-period">
        {t("period")}:{" "}
        {c.period
          ? `${dateLabel(c.period.start)} – ${dateLabel(c.period.end)} · ${c.period.sessions} ${t("sessions")}`
          : t("unavailable")}
      </p>
      <p>{t("sameWindow")}</p>
      <p className="panel-note">{t("tableHint")}</p>
      {c.status === "available" ? (
        <>
          <ResearchBarChart
            rows={rows.map((r) => ({
              name: label(r.experiment_id),
              value: String(
                measure === "avg_bond_weight"
                  ? r.avg_bond_weight
                  : r.metrics[measure],
              ),
            }))}
            labelKey="name"
            valueKey="value"
            formatter={measure === "sharpe_zero_rf" ? (v) => v.toFixed(3) : pct}
          />
          <SortableTable
            key={c.id}
            rows={rows.map((r) => ({
              name: label(r.experiment_id),
              total: (r.metrics.total_return * 100).toFixed(2),
              cagr: (r.metrics.cagr * 100).toFixed(2),
              sharpe: r.metrics.sharpe_zero_rf.toFixed(3),
              drawdown: (r.metrics.max_drawdown * 100).toFixed(2),
              bond: (r.avg_bond_weight * 100).toFixed(2),
              gross: r.gross_traded_notional.toFixed(2),
              oneway: r.one_way_turnover.toFixed(2),
              events: Object.entries(r.status_counts)
                .map(([s, n]) => `${states(s)}: ${n}`)
                .join("; "),
            }))}
            columns={[
              ["name", t("configuration")],
              ["total", `${t("total_return")} (%)`],
              ["cagr", `${t("cagr")} (%)`],
              ["sharpe", t("sharpe_zero_rf")],
              ["drawdown", `${t("max_drawdown")} (%)`],
              ["bond", `${t("avg_bond_weight")} (%)`],
              ["gross", t("gross")],
              ["oneway", t("oneway")],
              ["events", t("events")],
            ]}
          />
        </>
      ) : (
        <p>{t("unavailable")}</p>
      )}
      {evidence.experiments
        .filter(
          (e) =>
            e.group_id === q.groupId &&
            e.evidence_stage.startsWith("unavailable"),
        )
        .map((e) => (
          <p className="panel-note" key={e.id}>
            {label(e.id)}: {t("missing")}
          </p>
        ))}
      <section aria-labelledby="attribution-title">
        <h3 id="attribution-title">{t("attribution")}</h3>
        <p>{t("linked")}</p>
        {contributionView.status === "unavailable" && (
          <p role="status">{t("unavailable")}</p>
        )}
        <label className="rotation-control">
          {t("configuration")}
          <select
            aria-label={`${t("attribution")} ${t("configuration")}`}
            value={active?.experiment_id ?? ""}
            onChange={(e) => setContributor(e.target.value)}
          >
            {contributions.map((r) => (
              <option key={r.experiment_id} value={r.experiment_id}>
                {label(r.experiment_id)}
              </option>
            ))}
          </select>
        </label>
        {active?.status === "available" && (
          <ResearchBarChart
            rows={(["risk", "bond", "costs", "residual"] as const).map((k) => ({
              name: t(k),
              value: String(active[k]),
            }))}
            labelKey="name"
            valueKey="value"
            formatter={pct}
          />
        )}
        <SimpleTable
          rows={contributions.map((r) => ({
            name: label(r.experiment_id),
            risk: pct(r.risk),
            bond: pct(r.bond),
            costs: pct(r.costs),
            residual:
              r.residual === null
                ? t("unavailable")
                : `${(r.residual * 100).toExponential(2)}%`,
            total: pct(r.total_return),
          }))}
          columns={[
            ["name", t("configuration")],
            ["risk", t("risk")],
            ["bond", t("bond")],
            ["costs", t("costs")],
            ["residual", t("residual")],
            ["total", t("total_return")],
          ]}
        />
      </section>
      <section aria-labelledby="replay-title">
        <h3 id="replay-title">{t("replay")}</h3>
        <p>{t("replayScope")}</p>
        {!full && (
          <button type="button" disabled={loading} onClick={fetchReplay}>
            {loading ? t("loading") : error ? t("retry") : t("openReplay")}
          </button>
        )}
        {error && <p role="alert">{t("loadError")}</p>}
        {full && (
          <>
            <div className="rotation-controls">
              <label className="rotation-control">
                {t("replayVariant")}
                <select
                  aria-label={t("replayVariant")}
                  value={variant}
                  onChange={(e) => setVariant(e.target.value)}
                >
                  {["fixed-base", "pool-core"].map((k) => (
                    <option key={k} value={k}>
                      {label(k)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="rotation-control">
                {t("date")}
                <input
                  aria-label={t("date")}
                  type="date"
                  min={availableReplays[0]?.signal_date}
                  max={availableReplays.at(-1)?.signal_date}
                  value={selectedDate}
                  onChange={(e) => update({ date: e.target.value })}
                />
              </label>
              <button
                type="button"
                disabled={index <= 0}
                onClick={() =>
                  update({ date: availableReplays[index - 1].signal_date })
                }
              >
                {t("previous")}
              </button>
              <button
                type="button"
                disabled={index < 0 || index >= availableReplays.length - 1}
                onClick={() =>
                  update({ date: availableReplays[index + 1].signal_date })
                }
              >
                {t("next")}
              </button>
            </div>
            {replay?.status === "available" ? (
              <>
                <p role="status" data-testid="replay-status">
                  {t("date")}: {dateLabel(replay.record.signal_date)} ·{" "}
                  {t("execution")}: {dateLabel(replay.record.execution_date)} ·{" "}
                  {states(replay.record.status)}
                </p>
                <p>
                  {t("riskWeight")}: {pct(replay.record.allocation.risk_weight)}{" "}
                  · {t("bondWeight")}:{" "}
                  {pct(replay.record.allocation.bond_weight)}
                </p>
                <label className="rotation-control">
                  {t("eligibility")}
                  <select
                    aria-label={t("eligibility")}
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                  >
                    {(["all", "eligible", "ineligible"] as const).map((k) => (
                      <option key={k} value={k}>
                        {t(k)}
                      </option>
                    ))}
                  </select>
                </label>
                <SimpleTable
                  rows={replay.record.assets
                    .filter(
                      (a) =>
                        filter === "all" ||
                        (filter === "eligible") === a.eligible,
                    )
                    .map((a) => ({
                      symbol: englishLocale()
                        ? a.symbol
                        : `${a.symbol} ${a.name}`,
                      exposure: states(a.exposure_class),
                      first: a.first_observed_date
                        ? dateLabel(a.first_observed_date)
                        : t("unavailable"),
                      listing: t("unverified"),
                      history: String(a.observed_history),
                      eligible: t(a.eligible ? "eligible" : "ineligible"),
                      reasons: a.reasons.length
                        ? a.reasons.map(states).join("; ")
                        : t("passed"),
                    }))}
                  columns={[
                    ["symbol", t("symbol")],
                    ["exposure", t("exposure")],
                    ["first", t("firstObserved")],
                    ["listing", t("listing")],
                    ["history", t("history")],
                    ["eligible", t("eligible")],
                    ["reasons", t("reasons")],
                  ]}
                />
              </>
            ) : (
              <p role="status">
                {t("outside")}{" "}
                <button
                  type="button"
                  onClick={() =>
                    update({ date: availableReplays.at(-1)?.signal_date ?? "" })
                  }
                >
                  {t("restore")}
                </button>
              </p>
            )}
          </>
        )}
        <p className="panel-note">{t("listingNote")}</p>
      </section>
      <section className="rotation-card" aria-labelledby="theme-status-title">
        <h3 id="theme-status-title">{evidence.theme_status.status==="diagnostic"?extText("theme"):t("theme")}</h3>
        <RotationThemeEvidence theme={evidence.theme_status}/>
      </section>
      <p>
        <a
          href={releaseUrl.replace(
            "/data/rotation-evidence-release.json",
            "/research-notes/rotation-evidence-review" +
              (englishLocale() ? "" : ".zh-CN") +
              ".md",
          )}
        >
          {t("reviewNote")}
        </a>
      </p>
      <details>
        <summary>{t("methods")}</summary>
        <p>{t("methodBody")}</p>
        <ul>
          {evidence.limitations.map((k) => (
            <li key={k}>
              {limitationCopy[k] ? text(limitationCopy[k]) : t("unavailable")}
            </li>
          ))}
        </ul>
        <p>
          {t("sourceId")}: <code>{evidence.evidence_id}</code>
        </p>
        <p>
          <a href={releaseUrl} download>
            {t("source")}
          </a>
        </p>
      </details>
    </section>
  );
}
