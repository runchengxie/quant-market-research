import {readFile,mkdir,mkdtemp,writeFile,link,rename,rm,open} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {validateReviewedRotationEnvelope} from '../src/content/rotation-operations.server.ts';
import {validateIndexedBinding,validateReleaseIndex} from '../src/content/rotation-extension.ts';
import {canonical} from '../src/content/rotation-evidence.ts';
const sha=s=>createHash('sha256').update(s).digest('hex');
export async function importRotationRelease({envelopePath,outputDirectory,beforeRename=()=>{}}){
 const raw=await readFile(envelopePath);const envelope=JSON.parse(raw.toString());
 if(Object.keys(envelope).sort().join()!=='asset,review')throw Error('Invalid envelope fields');
 const a=envelope.asset;
 validateReviewedRotationEnvelope(envelope);
 const id=a.release_id??a.evidence_id;
 if(!/^[A-Za-z0-9][A-Za-z0-9_-]{0,95}$/.test(id))throw Error('Invalid release identity');
 await mkdir(outputDirectory,{recursive:true});
 const lock=join(outputDirectory,'.rotation-release.lock');const guard=await open(lock,'wx');
 let temp;
 try{
  const path=join(outputDirectory,'rotation-release-index.json');let index;
  try{index=validateReleaseIndex(JSON.parse(await readFile(path,'utf8')));}catch(e){if(e.code!=='ENOENT')throw e;index={schema_version:'research.rotation_release_index.v1',current_release_id:id,releases:[]};}
  for(const entry of index.releases){const retained=await readFile(join(outputDirectory,entry.path));if(sha(retained)!==entry.sha256)throw Error('Corrupt retained release');const priorEnvelope=JSON.parse(retained.toString());validateIndexedBinding(entry,priorEnvelope);validateReviewedRotationEnvelope(priorEnvelope);}
  const prior=index.releases.find(r=>r.release_id===id);
  if(prior){if(prior.sha256!==sha(raw))throw Error('Immutable release identity conflict');return;}
  const entry={release_id:id,schema_version:a.schema_version,path:`rotation/releases/${id}.json`,sha256:sha(raw),content_sha256:envelope.review.content_sha256,reviewer:envelope.review.reviewer,published_at:envelope.review.reviewed_at};
  const next=validateReleaseIndex({...index,current_release_id:id,releases:[...index.releases,entry]});
  await mkdir(join(outputDirectory,'rotation/releases'),{recursive:true});
  temp=await mkdtemp(join(outputDirectory,'.rotation-registry-'));
  await writeFile(join(temp,'release.json'),raw,{flag:'wx'});
  try{await link(join(temp,'release.json'),join(outputDirectory,entry.path));}catch(e){if(e.code!=='EEXIST'||sha(await readFile(join(outputDirectory,entry.path)))!==entry.sha256)throw e;}
  await writeFile(join(temp,'index.json'),canonical(next)+'\n',{flag:'wx'});
  await beforeRename();await rename(join(temp,'index.json'),path);
 }finally{if(temp)await rm(temp,{recursive:true});await guard.close();await rm(lock);}
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 const [envelopePath,outputDirectory]=process.argv.slice(2);
 if(!envelopePath||!outputDirectory)throw Error('Usage: import-rotation-release ENVELOPE OUTPUT');
 await importRotationRelease({envelopePath,outputDirectory});
}
