import {validateRotationFoundation} from './rotation-foundation.server';
import {validateRotationExtension} from './rotation-extension.server';
import {validateRotationEvidence} from './rotation-evidence.server';
import {createHash} from 'node:crypto';
import {canonical} from './rotation-evidence';
import {validateOperationsShape,validateOperationsReview} from './rotation-operations';
export function validateRotationOperations(value:unknown,review:unknown){
 const asset=validateOperationsShape(value);
 const sha=(text:string)=>createHash('sha256').update(text).digest('hex');
 validateOperationsReview(asset,review,{content:sha(canonical(asset)),asset:sha(canonical(asset)+'\n')});
 return asset;
}

export function validateReviewedRotationEnvelope(value:unknown){
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).sort().join()!=='asset,review')throw Error('Invalid reviewed release envelope');
 const e=value as {asset:{schema_version?:string};review:unknown};
 switch(e.asset?.schema_version){
  case 'research.rotation_foundation.v1':return validateRotationFoundation(e.asset,e.review);
  case 'research.rotation_operations.v1':return validateRotationOperations(e.asset,e.review);
  case 'research.rotation_extension.v1':return validateRotationExtension(e.asset,e.review);
  case 'research.rotation_evidence_public.v1':return validateRotationEvidence(e.asset,e.review);
  default:throw Error('Unknown rotation release schema');
 }
}
