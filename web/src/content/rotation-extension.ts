import schema from './rotation-extension-schema.json';
import { validatePublicText, canonical } from './rotation-evidence';
export type Metrics = {
    total_return: number;
    cagr: number;
    sharpe_zero_rf: number;
    max_drawdown: number;
};
export type Period = {
    start: string;
    end: string;
    sessions: number;
};
export type RobustRow = {
    id: string;
    experiment_id: string;
    group_id: string;
    allocator: string;
    cost_bps: number;
    delay_sessions: number;
    window_id: string;
    status: 'available' | 'unavailable';
    reasons: string[];
    period: Period | null;
    metrics: (Metrics & {
        volatility: number;
        cost_drag: number;
        avg_bond_weight: number;
        attribution: {
            risk: number;
            bond: number;
            costs: number;
            residual: number;
            total_return: number;
        };
    }) | null;
    turnover: number | null;
    pending_terminal: number;
};
export type RotationExtension = {
    schema_version: 'research.rotation_extension.v1';
    release_id: string;
    created_at: string;
    producer_commit: string;
    base_evidence_id: string;
    reviewed_source_digest: string;
    sources: {
        availability: string;
        panel_start: string;
        panel_end: string;
        panel_count: number;
        admitted_count: number;
        recovered_symbols: string[];
        hashes: {
            core: string;
            pool: string;
            mapping: string;
        };
        symbols: {
            symbol: string;
            status: string;
            reason: string;
        }[];
        reconciliation: {
            symbol: string;
            status: string;
            reason: string;
            median_amount: number;
        }[];
    };
    forward: {
        status: 'waiting_for_fresh_inputs' | 'collecting';
        reasons: string[];
        registration_id: string | null;
        effective_at: string | null;
        captured_weeks: number;
        settled_weeks: number;
        missed_weeks: {
            week: string;
            reason: string;
        }[];
        coverage: {
            experiment_id: string;
            captured_weeks: number;
            settled_weeks: number;
            metrics: Metrics | null;
        }[];
        metrics: Metrics | null;
    };
    robustness: {
        registration_sha256: string;
        historical_availability: string;
        rows: RobustRow[];
        unavailable_experiments: {
            experiment_id: string;
            reason: string;
        }[];
        benchmarks: {
            group_id: string;
            allocator: string;
            benchmark_id: string;
            window_id: string;
            cost_bps: number;
            status: 'available' | 'unavailable';
            reasons: string[];
            period: Period | null;
            metrics: Metrics | null;
        }[];
    };
    theme: {
        status: 'blocked' | 'diagnostic';
        reasons: string[];
        registration_id: string | null;
        metrics: {
            baseline: Metrics;
            overlay: Metrics;
            difference: {
                total_return_pp: number;
                cagr_pp: number;
            };
        } | null;
    };
    changes: {
        kind: string;
        code: string;
    }[];
};
export type ReleaseEntry = {
    release_id: string;
    schema_version: string;
    path: string;
    sha256: string;
    content_sha256: string;
    reviewer: string;
    published_at: string;
};
export type ReleaseIndex = {
    schema_version: 'research.rotation_release_index.v1';
    current_release_id: string;
    releases: ReleaseEntry[];
};
export const isHash = (v: unknown): v is string => typeof v === 'string' && /^[a-f0-9]{64}$/.test(v);
const isObject = (v: unknown): v is Record<string, unknown> => !!v && typeof v === 'object' && !Array.isArray(v);
function validateDescriptor(value: unknown, rule: unknown): void {
    if (Array.isArray(rule)) {
        if (!Array.isArray(value))
            throw Error('Expected public array');
        value.forEach(v => validateDescriptor(v, rule[0]));
        return;
    }
    if (isObject(rule)) {
        if (Object.keys(rule).join() === '?') {
            if (value !== null)
                validateDescriptor(value, rule['?']);
            return;
        }
        if (!isObject(value) || Object.keys(value).sort().join() !== Object.keys(rule).sort().join())
            throw Error('Unknown public fields');
        Object.entries(rule).forEach(([k, r]) => validateDescriptor(value[k], r));
        return;
    }
    if (rule === 'number' || rule === 'integer') {
        if (typeof value !== 'number' || !Number.isFinite(value) || Math.abs(value) > 1e9 || (rule === 'integer' && (!Number.isInteger(value) || value < 0)))
            throw Error('Invalid public number');
        return;
    }
    validatePublicText(value);
    if (typeof value !== 'string' || !value || value.length > 1000)
        throw Error('Invalid text');
    if (rule === 'sha256' && !isHash(value))
        throw Error('Invalid hash');
    if (rule === 'date' && (!/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().slice(0, 10) !== value))
        throw Error('Invalid date');
    if (rule === 'timestamp' && (!/(Z|[+-]\d{2}:\d{2})$/.test(value) || !Number.isFinite(Date.parse(value))))
        throw Error('Invalid timestamp');
}
export function validateExtensionShape(value: unknown): RotationExtension {
    validateDescriptor(value, schema);
    const a = value as RotationExtension;
    if (a.schema_version !== 'research.rotation_extension.v1' || !/^\w[\w-]{0,95}$/.test(a.release_id) || !/^[a-f0-9]{40}$/.test(a.producer_commit))
        throw Error('Invalid extension identity');
    if (!['waiting_for_fresh_inputs', 'collecting'].includes(a.forward.status) || a.forward.settled_weeks > a.forward.captured_weeks || (!a.forward.settled_weeks && a.forward.metrics !== null))
        throw Error('Invalid forward evidence');
    if (!['blocked', 'diagnostic'].includes(a.theme.status) || (a.theme.status === 'blocked') !== (a.theme.metrics === null))
        throw Error('Invalid theme state');
    const ids = new Set<string>();
    for (const r of a.robustness.rows) {
        if (ids.has(r.id))
            throw Error('Duplicate case');
        ids.add(r.id);
        if (![0, 5, 10].includes(r.cost_bps) || ![1, 2].includes(r.delay_sessions) || !['available', 'unavailable'].includes(r.status) || (r.status === 'available') !== (r.metrics !== null && r.period !== null))
            throw Error('Invalid robustness case');
        if (r.metrics && r.period) {
            const m = r.metrics, t = m.attribution;
            if (r.period.start > r.period.end || r.period.sessions < 2 || r.period.sessions > (Date.parse(r.period.end) - Date.parse(r.period.start)) / 86400000 + 1)
                throw Error('Invalid period');
            if (['last_252', 'last_756'].includes(r.window_id) && r.period.sessions !== Number(r.window_id.slice(5)))
                throw Error('Incomplete window');
            if (Math.abs(t.total_return - m.total_return) > 1e-10 || Math.abs(t.risk + t.bond + t.costs + t.residual - m.total_return) > 1e-10 || m.avg_bond_weight < 0 || m.avg_bond_weight > 1 || m.max_drawdown < -1 || m.max_drawdown > 0)
                throw Error('Invalid attribution');
        }
    }
    for (const b of a.robustness.benchmarks) {
        if (!['available', 'unavailable'].includes(b.status) || (b.status === 'available') !== (b.metrics !== null) || ![0, 5, 10].includes(b.cost_bps))
            throw Error('Invalid benchmark status or metrics');
        if (b.metrics && (!b.period || b.period.start > b.period.end || b.period.sessions < 2 || b.metrics.max_drawdown < -1 || b.metrics.max_drawdown > 0))
            throw Error('Invalid benchmark period');
    }
    return a;
}
export function validateReleaseIndex(value: unknown): ReleaseIndex {
    validateDescriptor(value, { schema_version: 'text', current_release_id: 'text', releases: [{ release_id: 'text', schema_version: 'text', path: 'text', sha256: 'sha256', content_sha256: 'sha256', reviewer: 'text', published_at: 'timestamp' }] });
    const index = value as ReleaseIndex;
    if (index.schema_version !== 'research.rotation_release_index.v1' || !index.releases.length || new Set(index.releases.map(r => r.release_id)).size !== index.releases.length || !index.releases.some(r => r.release_id === index.current_release_id))
        throw Error('Invalid release index');
    for (const r of index.releases)
        if (!/^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$/.test(r.release_id) || r.path !== `rotation/releases/${r.release_id}.json`)
            throw Error('Unsafe release path');
    return index;
}
export async function shaBytes(value: Uint8Array | string): Promise<string> {
    const bytes = typeof value === 'string' ? new TextEncoder().encode(value) : value;
    return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes as BufferSource)), b => b.toString(16).padStart(2, '0')).join('');
}
export async function loadIndexedRelease(entry: ReleaseEntry, baseUrl: string) {
    const response = await fetch(new URL(entry.path, baseUrl).href);
    if (!response.ok)
        throw Error('Release unavailable');
    const raw = new Uint8Array(await response.arrayBuffer());
    if (await shaBytes(raw) !== entry.sha256)
        throw Error('Release bytes mismatch');
    const envelope = JSON.parse(new TextDecoder().decode(raw));
    if (await shaBytes(canonical(envelope.asset)) !== entry.content_sha256)
        throw Error('Release content mismatch');
    if (envelope.asset.schema_version === 'research.rotation_extension.v1')
        validateExtensionShape(envelope.asset);
    return envelope.asset as RotationExtension | Record<string, unknown>;
}
