import type { RotationOperations } from './rotation-operations';
import {canonical} from './rotation-evidence';
import type { RotationExtension } from './rotation-extension';
export type ComparedRow = {
    id: string;
    status: 'compatible' | 'incompatible' | 'added' | 'removed';
    cagr_delta: number | null;
    drawdown_delta: number | null;
};
export function compareRotationReleases(left: unknown, right: unknown): {
    status: 'comparable' | 'incompatible' | 'identical';
    changes: string[];
    rows: ComparedRow[];
} {
    if (!left || !right || typeof left !== 'object' || typeof right !== 'object')
        return {status:'incompatible',changes:['schema_changed'],rows:[]};
    const ls=(left as {schema_version?:string}).schema_version, rs=(right as {schema_version?:string}).schema_version;
    if(ls==='research.rotation_foundation.v1' && rs==='research.rotation_foundation.v1')
        return canonical(left) === canonical(right)
            ? {status:'identical',changes:['same_release'],rows:[]}
            : {status:'incompatible',changes:['foundation_comparison_unavailable'],rows:[]};
    if(ls==='research.rotation_operations.v1' && rs==='research.rotation_operations.v1')
        return compareOperations(left as RotationOperations,right as RotationOperations);
    if(ls==='research.rotation_operations.v1' || rs==='research.rotation_operations.v1')
        return {status:'incompatible',changes:['schema_changed','historical_archive_preserved'],rows:[]};
    const l = left as RotationExtension, r = right as RotationExtension;
    if (l.schema_version !== 'research.rotation_extension.v1' || r.schema_version !== 'research.rotation_extension.v1')
        return { status: 'incompatible', changes: ['schema_changed', 'historical_archive_preserved', ...(r.schema_version === 'research.rotation_extension.v1' ? r.changes.map(change => change.code) : [])], rows: [] };
    const changes: string[] = [];
    const sameTrust = l.sources.availability === r.sources.availability && l.robustness.historical_availability === r.robustness.historical_availability;
    if (!sameTrust) changes.push('source_availability_changed');
    if (JSON.stringify(l.sources.hashes) !== JSON.stringify(r.sources.hashes))
        changes.push('source_vintage_changed');
    if (l.sources.panel_end !== r.sources.panel_end || l.sources.panel_start !== r.sources.panel_start)
        changes.push('sample_changed');
    if (l.robustness.registration_sha256 !== r.robustness.registration_sha256)
        changes.push('registration_changed');
    if (l.forward.settled_weeks !== r.forward.settled_weeks || l.forward.registration_id !== r.forward.registration_id || l.forward.effective_at !== r.forward.effective_at || l.forward.status !== r.forward.status)
        changes.push('forward_evidence_changed');
    if (l.theme.status !== r.theme.status)
        changes.push('theme_status_changed');
    for (const change of r.changes)
        if (!l.changes.some(prior => prior.kind === change.kind && prior.code === change.code)) changes.push(change.code);
    const a = new Map(l.robustness.rows.map(row => [row.id, row])), b = new Map(r.robustness.rows.map(row => [row.id, row]));
    const rows: ComparedRow[] = [...new Set([...a.keys(), ...b.keys()])].map(id => {
        const x = a.get(id), y = b.get(id);
        let status: ComparedRow['status'] = 'incompatible';
        if (!x)
            status = 'added';
        else if (!y)
            status = 'removed';
        else {
            const panel = x.experiment_id.startsWith('pool-') ? 'pool' : 'core';
            if (x.status === 'available' && y.status === 'available' && sameTrust && l.sources.hashes.mapping === r.sources.hashes.mapping && x.experiment_id === y.experiment_id && x.group_id === y.group_id && x.window_id === y.window_id && l.sources.hashes[panel] === r.sources.hashes[panel] && l.robustness.registration_sha256 === r.robustness.registration_sha256 && JSON.stringify(x.period) === JSON.stringify(y.period) && x.cost_bps === y.cost_bps && x.delay_sessions === y.delay_sessions && x.allocator === y.allocator)
                status = 'compatible';
        }
        return { id, status, cagr_delta: status === 'compatible' ? y!.metrics!.cagr - x!.metrics!.cagr : null, drawdown_delta: status === 'compatible' ? y!.metrics!.max_drawdown - x!.metrics!.max_drawdown : null };
    });
    if (rows.some(row => row.status === 'incompatible')) changes.push('row_definitions_changed');
    return { status: 'comparable', changes: changes.length ? changes : ['same_definitions'], rows };
}


function compareOperations(l:RotationOperations,r:RotationOperations):{status:'comparable'|'incompatible';changes:string[];rows:ComparedRow[]}{
 const changes:string[]=[];
 if(l.comparisons.protocol_sha256!==r.comparisons.protocol_sha256||canonical(l.comparisons.risk)!==canonical(r.comparisons.risk))changes.push('matched_protocol_changed');
 if(l.audit.audit_sha256!==r.audit.audit_sha256||canonical(l.audit.source_hashes)!==canonical(r.audit.source_hashes)||l.audit.historical_availability!==r.audit.historical_availability||l.comparisons.historical_availability!==r.comparisons.historical_availability)changes.push('source_availability_changed');
 if(l.health.cutoff_local!==r.health.cutoff_local||l.health.timezone!==r.health.timezone)changes.push('decision_cutoff_changed');
 if(l.base_evidence_id!==r.base_evidence_id)changes.push('schema_changed');
 if(l.health.captured_weeks!==r.health.captured_weeks||l.health.settled_weeks!==r.health.settled_weeks||l.health.state!==r.health.state)changes.push('forward_evidence_changed');
 const compatible=!changes.some(code=>code!=='forward_evidence_changed');
 const a=new Map(l.comparisons.rows.map(row=>[row.id,row])),b=new Map(r.comparisons.rows.map(row=>[row.id,row]));
 const rows:ComparedRow[]=[...new Set([...a.keys(),...b.keys()])].map(id=>{
  const x=a.get(id),y=b.get(id);
  const match=compatible&&x&&y&&x.status==='available'&&y.status==='available'&&x.protocol_sha256===y.protocol_sha256&&canonical(x.period)===canonical(y.period)&&canonical(x.reference_period)===canonical(y.reference_period)&&canonical(x.comparator_period)===canonical(y.comparator_period)&&x.cost_bps===y.cost_bps&&x.execution_delay_sessions===y.execution_delay_sessions&&x.baseline===y.baseline&&x.eligibility_case===y.eligibility_case&&x.comparison===y.comparison;
  return {id,status:!x?'added':!y?'removed':match?'compatible':'incompatible',cagr_delta:match?y!.metrics!.reference.cagr-x!.metrics!.reference.cagr:null,drawdown_delta:match?y!.metrics!.reference.max_drawdown-x!.metrics!.reference.max_drawdown:null};
 });
 if(rows.some(row=>row.status==='incompatible'))changes.push('row_definitions_changed');
 return {status:'comparable',changes:changes.length?changes:['same_definitions'],rows};
}
