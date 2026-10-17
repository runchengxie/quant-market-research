/** Public research contract. No strategy calculation or private producer imports. */
export type Period = { start: string; end: string; sessions: number };
export type Metrics = {
  total_return: number;
  cagr: number;
  sharpe_zero_rf: number;
  max_drawdown: number;
};
export type Experiment = {
  id: string;
  group_id: string;
  allocator: string;
  source_id: string;
  protocol_id: string;
  evidence_stage: string;
  original_period: Period | null;
  original_metrics: Metrics | null;
};
export type Member = {
  experiment_id: string;
  metrics: Metrics;
  avg_bond_weight: number;
  gross_traded_notional: number;
  one_way_turnover: number;
  status_counts: Record<string, number>;
};
export type Comparison = {
  id: string;
  group_id: string;
  window_id: string;
  allocator: string;
  protocol_id: string;
  period: Period | null;
  status: string;
  reasons: string[];
  members: Member[];
};
export type Replay = {
  experiment_id: string;
  signal_date: string;
  execution_date: string;
  status: string;
  availability: string;
  assets: {
    symbol: string;
    name: string;
    exposure_class: string;
    first_observed_date: string | null;
    listing_verified: boolean;
    observed_history: number;
    eligible: boolean;
    reasons: string[];
  }[];
  allocation: { risk_weight: number; bond_weight: number };
};
export type Attribution = {
  experiment_id: string;
  window_id: string;
  period: Period | null;
  status: string;
  reasons: string[];
  risk: number | null;
  bond: number | null;
  costs: number | null;
  residual: number | null;
  total_return: number | null;
};
export type RotationEvidence = {
  schema_version: string;
  evidence_id: string;
  producer_commit: string;
  generated_at: string;
  reviewed_source_digest: string;
  units: { returns: string; sharpe: string; contributions: string };
  protocols: {
    id: string;
    price_convention: string;
    execution_convention: string;
    cost_bps: number;
    annualization_sessions: number;
    risk_budget_policy: string;
  }[];
  sources: {
    id: string;
    status: string;
    panel_start: string;
    panel_end: string;
    availability: string;
  }[];
  experiments: Experiment[];
  comparisons: Comparison[];
  replay: Replay[];
  attribution: Attribution[];
  theme_status: {
    status: string;
    reasons: string[];
    registration_id: string | null;
    metrics: {
      baseline: Metrics;
      overlay: Metrics;
      difference: { total_return_pp: number; cagr_pp: number };
    } | null;
  };
  limitations: string[];
};
export type Review = {
  status: string;
  source_sha256: string;
  content_sha256: string;
  asset_sha256: string;
  reviewer: string;
  reviewed_at: string;
};
export function canonical(value: unknown): string {
  if (typeof value === "number") {
    if (!Number.isFinite(value) || Math.abs(value) > 1e9)
      throw Error("Invalid public number");
    const result = value.toFixed(12).replace(/\.?0+$/, "");
    return result === "-0" || result === "" ? "0" : result;
  }
  if (value === null || typeof value === "string" || typeof value === "boolean")
    return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (typeof value === "object") {
    const row = value as Record<string, unknown>;
    return `{${Object.keys(row)
      .sort()
      .map((k) => `${JSON.stringify(k)}:${canonical(row[k])}`)
      .join(",")}}`;
  }
  throw Error("Unsupported public JSON");
}
function fields(value: any, keys: string) {
  if (
    !value ||
    typeof value !== "object" ||
    Array.isArray(value) ||
    Object.keys(value).sort().join(" ") !== keys.split(" ").sort().join(" ")
  )
    throw Error("Unreviewed public fields");
}
export function validatePublicText(value: any) {
  if (
    typeof value !== "string" ||
    !value ||
    value.length > 1000 ||
    /\/home\/|\/tmp\/|\/mnt\/|\/Users\/|file:\/\/|\\\\|[A-Za-z]:\\|API_KEY|TOKEN=|SECRET|\.worktrees/.test(
      value,
    )
  )
    throw Error("Private or invalid public text");
}
function number(value: any, low = -1e9, high = 1e9) {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value) ||
    value < low ||
    value > high
  )
    throw Error("Invalid public numeric value");
}
function day(value: any): number {
  if (
    typeof value !== "string" ||
    !/^\d{4}-\d{2}-\d{2}$/.test(value) ||
    !Number.isFinite(Date.parse(value)) ||
    new Date(value).toISOString().slice(0, 10) !== value
  )
    throw Error("Invalid public date");
  return Date.parse(value);
}
function period(value: any) {
  fields(value, "start end sessions");
  const start = day(value.start),
    end = day(value.end);
  number(value.sessions, 2, 100000);
  if (
    start > end ||
    !Number.isInteger(value.sessions) ||
    value.sessions > (end - start) / 86400000 + 1
  )
    throw Error("Invalid public period");
}
function metrics(value: any) {
  fields(value, "total_return cagr sharpe_zero_rf max_drawdown");
  Object.values(value).forEach((v) => number(v));
  number(value.total_return, -1);
  number(value.max_drawdown, -1, 0);
}
function strings(value: any) {
  if (!Array.isArray(value) || value.length > 50)
    throw Error("Invalid public reasons");
  value.forEach(validatePublicText);
}
function collection(value: any, limit: number, keys: string): any[] {
  if (!Array.isArray(value) || value.length > limit)
    throw Error("Invalid collection");
  value.forEach((row) => fields(row, keys));
  return value;
}
function unique(rows: any[], key = "id") {
  if (new Set(rows.map((r) => r[key])).size !== rows.length)
    throw Error("Duplicate identity");
}
const executionStates = new Set([
  "EXECUTED",
  "OPTIMIZER_FALLBACK",
  "NO_TRADE_THRESHOLD",
  "BLOCKED_EXECUTION_MARK",
]);
function availablePeriod(row: any) {
  period(row.period);
  const required: Record<string, number> = { last_252: 252, last_756: 756 };
  if (
    required[row.window_id] &&
    row.period.sessions !== required[row.window_id]
  )
    throw Error("Incomplete named window");
}
export function validateShape(value: unknown): RotationEvidence {
  const a = value as any;
  fields(
    a,
    "schema_version evidence_id producer_commit generated_at reviewed_source_digest units protocols sources experiments comparisons replay attribution theme_status limitations",
  );
  if (
    a.schema_version !== "research.rotation_evidence_public.v1" ||
    !/^[a-f0-9]{40}$/.test(a.producer_commit) ||
    !/[Zz]|[+-]\d\d:\d\d$/.test(a.generated_at) ||
    !Number.isFinite(Date.parse(a.generated_at)) ||
    !/^[a-f0-9]{64}$/.test(a.reviewed_source_digest)
  )
    throw Error("Invalid evidence identity");
  if (
    canonical(a.units) !==
    canonical({
      returns: "decimal",
      sharpe: "ratio",
      contributions: "decimal_nav",
    })
  )
    throw Error("Unknown units");
  strings(a.limitations);
  if (!a.limitations.length) throw Error("Limitations required");
  const protocols = collection(
    a.protocols,
    24,
    "id price_convention execution_convention cost_bps annualization_sessions risk_budget_policy",
  );
  unique(protocols);
  protocols.forEach((r) => {
    number(r.cost_bps, 0, 10000);
    if (r.annualization_sessions !== 252) throw Error("Unknown annualization");
  });
  const sources = collection(
    a.sources,
    10,
    "id status panel_start panel_end availability",
  );
  unique(sources);
  sources.forEach((r) => {
    if (day(r.panel_start) > day(r.panel_end))
      throw Error("Invalid source period");
  });
  const experiments = collection(
    a.experiments,
    24,
    "id group_id allocator source_id protocol_id evidence_stage original_period original_metrics",
  );
  unique(experiments);
  if (!experiments.length) throw Error("Experiments required");
  const byId = new Map<string, Experiment>(experiments.map((r) => [r.id, r]));
  experiments.forEach((r) => {
    if (
      !sources.some((s) => s.id === r.source_id) ||
      !protocols.some((p) => p.id === r.protocol_id) ||
      !["risk", "pool", "holdover", "score"].includes(r.group_id) ||
      !["fixed_slots", "defensive", "growth"].includes(r.allocator)
    )
      throw Error("Invalid experiment reference");
    if (r.original_period !== null) period(r.original_period);
    if (r.original_metrics !== null) metrics(r.original_metrics);
  });
  const comparisons = collection(
    a.comparisons,
    100,
    "id group_id window_id allocator protocol_id period status reasons members",
  );
  unique(comparisons);
  comparisons.forEach((r) => {
    strings(r.reasons);
    if (!["common", "last_252", "last_756"].includes(r.window_id))
      throw Error("Unknown window");
    if (r.status === "unavailable") {
      if (r.period !== null || !Array.isArray(r.members) || r.members.length)
        throw Error("Unavailable comparison has values");
      return;
    }
    if (r.status !== "available") throw Error("Unknown comparison status");
    availablePeriod(r);
    const members = collection(
      r.members,
      24,
      "experiment_id metrics avg_bond_weight gross_traded_notional one_way_turnover status_counts",
    );
    if (!members.length) throw Error("Missing members");
    unique(members, "experiment_id");
    members.forEach((m) => {
      const e = byId.get(m.experiment_id);
      if (
        !e ||
        (["group_id", "allocator", "protocol_id"] as const).some(
          (k) => e[k] !== r[k],
        )
      )
        throw Error("Incompatible comparison");
      metrics(m.metrics);
      number(m.avg_bond_weight, 0, 1);
      number(m.gross_traded_notional, 0);
      number(m.one_way_turnover, 0);
      if (
        !m.status_counts ||
        typeof m.status_counts !== "object" ||
        Array.isArray(m.status_counts)
      )
        throw Error("Missing execution counts");
      if (Object.keys(m.status_counts).some((k) => !executionStates.has(k)))
        throw Error("Unknown execution count field");
      Object.values(m.status_counts).forEach((v) => {
        number(v, 0, 100000);
        if (!Number.isInteger(v)) throw Error("Invalid event count");
      });
    });
  });
  collection(
    a.replay,
    12000,
    "experiment_id signal_date execution_date status availability assets allocation",
  ).forEach((r) => {
    if (
      !byId.has(r.experiment_id) ||
      !executionStates.has(r.status) ||
      day(r.signal_date) >= day(r.execution_date)
    )
      throw Error("Invalid replay identity/date");
    fields(r.allocation, "risk_weight bond_weight");
    number(r.allocation.risk_weight, 0, 1);
    number(r.allocation.bond_weight, 0, 1);
    if (
      Math.abs(r.allocation.risk_weight + r.allocation.bond_weight - 1) > 1e-10
    )
      throw Error("Invalid allocation");
    const assets = collection(
      r.assets,
      50,
      "symbol name exposure_class first_observed_date listing_verified observed_history eligible reasons",
    );
    unique(assets, "symbol");
    assets.forEach((s) => {
      if (
        !/^\d{6}$/.test(s.symbol) ||
        typeof s.eligible !== "boolean" ||
        typeof s.listing_verified !== "boolean"
      )
        throw Error("Invalid public ETF");
      number(s.observed_history, 0, 100000);
      if (!Number.isInteger(s.observed_history)) throw Error("Invalid history");
      if (
        s.first_observed_date !== null &&
        day(s.first_observed_date) > day(r.signal_date)
      )
        throw Error("Future observation");
      strings(s.reasons);
    });
  });
  collection(
    a.attribution,
    72,
    "experiment_id window_id period status reasons risk bond costs residual total_return",
  ).forEach((r) => {
    if (
      !byId.has(r.experiment_id) ||
      !["common", "last_252", "last_756"].includes(r.window_id)
    )
      throw Error("Invalid attribution identity");
    strings(r.reasons);
    const keys = ["risk", "bond", "costs", "residual", "total_return"];
    if (r.status === "unavailable") {
      if (r.period !== null || keys.some((k) => r[k] !== null))
        throw Error("Unavailable attribution has values");
      return;
    }
    if (r.status !== "available") throw Error("Unknown attribution status");
    availablePeriod(r);
    keys.forEach((k) => number(r[k]));
    if (
      Math.abs(r.risk + r.bond + r.costs + r.residual - r.total_return) > 1e-10
    )
      throw Error("Unreconciled attribution");
    const matches = comparisons.flatMap((c) =>
      c.status === "available" &&
      c.window_id === r.window_id &&
      canonical(c.period) === canonical(r.period)
        ? c.members.filter((m: any) => m.experiment_id === r.experiment_id)
        : [],
    );
    if (
      matches.length !== 1 ||
      Math.abs(matches[0].metrics.total_return - r.total_return) > 1e-10
    )
      throw Error("Attribution does not match comparison return");
  });
  fields(a.theme_status, "status reasons registration_id metrics");
  strings(a.theme_status.reasons);
  if (a.theme_status.status === "blocked") {
    if (a.theme_status.metrics !== null)
      throw Error("Blocked theme has performance");
  } else if (a.theme_status.status === "diagnostic") {
    const m = a.theme_status.metrics;
    fields(m, "baseline overlay difference");
    metrics(m.baseline);
    metrics(m.overlay);
    fields(m.difference, "total_return_pp cagr_pp");
    Object.values(m.difference).forEach((v) => number(v));
  } else throw Error("Unknown theme status");
  const textKeys = new Set(
    "schema_version evidence_id producer_commit generated_at reviewed_source_digest id price_convention execution_convention risk_budget_policy status availability panel_start panel_end group_id allocator source_id protocol_id evidence_stage window_id experiment_id signal_date execution_date symbol name exposure_class returns sharpe contributions start end".split(
      " ",
    ),
  );
  function scan(v: any) {
    if (typeof v === "string") validatePublicText(v);
    else if (Array.isArray(v)) v.forEach(scan);
    else if (v && typeof v === "object")
      Object.entries(v).forEach(([k, x]) => {
        validatePublicText(k);
        if (
          textKeys.has(k) ||
          (["registration_id", "first_observed_date"].includes(k) && x !== null)
        )
          validatePublicText(x);
        scan(x);
      });
  }
  scan(a);
  canonical(a);
  return a;
}
export function selectComparison(
  e: RotationEvidence,
  q: { groupId: string; windowId: string; allocator: string },
): Comparison {
  return (
    e.comparisons.find(
      (r) =>
        r.group_id === q.groupId &&
        r.window_id === q.windowId &&
        r.allocator === q.allocator,
    ) ?? {
      id: "unavailable",
      group_id: q.groupId,
      window_id: q.windowId,
      allocator: q.allocator,
      protocol_id: "unavailable",
      period: null,
      status: "unavailable",
      reasons: ["no_compatible_comparison"],
      members: [],
    }
  );
}
export function selectReplay(
  e: RotationEvidence,
  q: { date: string; experimentId: string },
):
  | { status: "available"; record: Replay }
  | { status: "unavailable"; reasons: string[] } {
  try {
    day(q.date);
  } catch {
    return { status: "unavailable", reasons: ["invalid_date"] };
  }
  const rows = e.replay
    .filter((r) => r.experiment_id === q.experimentId)
    .sort((a, b) => a.signal_date.localeCompare(b.signal_date));
  if (
    !rows.length ||
    q.date < rows[0].signal_date ||
    q.date > rows[rows.length - 1].signal_date
  )
    return { status: "unavailable", reasons: ["outside_replay_coverage"] };
  const record = rows.filter((r) => r.signal_date <= q.date).at(-1);
  return record
    ? { status: "available", record }
    : { status: "unavailable", reasons: ["outside_replay_coverage"] };
}
export function selectAttribution(
  e: RotationEvidence,
  q: { comparisonId: string; windowId: string },
):
  | { status: "available"; rows: Attribution[] }
  | { status: "unavailable"; reasons: string[] } {
  const c = e.comparisons.find(
    (r) => r.id === q.comparisonId && r.window_id === q.windowId,
  );
  if (!c || c.status !== "available")
    return { status: "unavailable", reasons: ["no_compatible_comparison"] };
  const rows = c.members.map((m) =>
    e.attribution.find(
      (r) =>
        r.window_id === q.windowId &&
        r.experiment_id === m.experiment_id &&
        canonical(r.period) === canonical(c.period),
    ),
  );
  if (rows.some((r) => !r || r.status !== "available"))
    return {
      status: "unavailable",
      reasons: ["missing_contribution_evidence"],
    };
  return { status: "available", rows: rows as Attribution[] };
}

export async function loadReplay(
  url: string,
  expectedSha: string,
): Promise<RotationEvidence> {
  const response = await fetch(url);
  if (!response.ok) throw Error("release_unavailable");
  const bytes = await response.arrayBuffer();
  const hash = Array.from(
    new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
    (b) => b.toString(16).padStart(2, "0"),
  ).join("");
  if (hash !== expectedSha) throw Error("release_hash_mismatch");
  const envelope = JSON.parse(new TextDecoder().decode(bytes));
  fields(envelope, "asset review");
  return validateShape(envelope.asset);
}
