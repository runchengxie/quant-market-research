import {createHash} from 'node:crypto';
import {canonical} from './rotation-evidence';
import {validateFoundationShape,validateFoundationReview} from './rotation-foundation';
export function validateRotationFoundation(value:unknown,review:unknown){const asset=validateFoundationShape(value);const sha=(s:string)=>createHash('sha256').update(s).digest('hex');validateFoundationReview(asset,review,{content:sha(canonical(asset)),asset:sha(canonical(asset)+'\n')});return asset;}
