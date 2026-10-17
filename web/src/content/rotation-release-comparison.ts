import type {RotationExtension} from './rotation-extension';
export type ComparedRow={id:string;status:'compatible'|'incompatible'|'added'|'removed';cagr_delta:number|null;drawdown_delta:number|null};
export function compareRotationReleases(left:unknown,right:unknown):{status:'comparable'|'incompatible';changes:string[];rows:ComparedRow[]}{
 const l=left as RotationExtension,r=right as RotationExtension;
 if(l.schema_version!=='research.rotation_extension.v1'||r.schema_version!=='research.rotation_extension.v1')return {status:'incompatible',changes:['schema_changed','historical_archive_preserved'],rows:[]};
 const changes:string[]=[];
 if(JSON.stringify(l.sources.hashes)!==JSON.stringify(r.sources.hashes))changes.push('source_vintage_changed');
 if(l.sources.panel_end!==r.sources.panel_end||l.sources.panel_start!==r.sources.panel_start)changes.push('sample_changed');
 if(l.robustness.registration_sha256!==r.robustness.registration_sha256)changes.push('registration_changed');
 if(l.forward.settled_weeks!==r.forward.settled_weeks)changes.push('forward_evidence_changed');
 if(l.theme.status!==r.theme.status)changes.push('theme_status_changed');
 const a=new Map(l.robustness.rows.map(row=>[row.id,row])),b=new Map(r.robustness.rows.map(row=>[row.id,row]));
 const rows:ComparedRow[]=[...new Set([...a.keys(),...b.keys()])].map(id=>{
  const x=a.get(id),y=b.get(id);let status:ComparedRow['status']='incompatible';
  if(!x)status='added';else if(!y)status='removed';
  else {const panel=x.experiment_id.startsWith('pool-')?'pool':'core';
   if(x.status==='available'&&y.status==='available'&&l.sources.hashes[panel]===r.sources.hashes[panel]&&l.robustness.registration_sha256===r.robustness.registration_sha256&&JSON.stringify(x.period)===JSON.stringify(y.period)&&x.cost_bps===y.cost_bps&&x.delay_sessions===y.delay_sessions&&x.allocator===y.allocator)status='compatible';}
  return {id,status,cagr_delta:status==='compatible'?y!.metrics!.cagr-x!.metrics!.cagr:null,drawdown_delta:status==='compatible'?y!.metrics!.max_drawdown-x!.metrics!.max_drawdown:null};
 });
 return {status:'comparable',changes:changes.length?changes:['same_definitions'],rows};
}
