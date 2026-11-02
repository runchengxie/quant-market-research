import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import type {EvidenceVersion} from './research-reading';
import {assetReadingCopy as c} from './asset-topics';

type PublicationRecord={schema_version:number;source_revision:string;published_at:string;version_date:string;timezone:string;publication_url:string;manifest_sha256:string};
export function validateAssetPublication(record:PublicationRecord,manifest:Buffer):PublicationRecord{
 if(record.schema_version!==1||!(/^[a-f0-9]{40}$/).test(record.source_revision)||record.timezone!=='Asia/Shanghai'||!(/^https:\/\/github\.com\/runchengxie\/quant-market-research\/pull\/\d+$/).test(record.publication_url))throw Error('Invalid asset publication record');
 if(createHash('sha256').update(manifest).digest('hex')!==record.manifest_sha256)throw Error('Asset publication manifest mismatch');
 const instant=new Date(record.published_at);
 if(!Number.isFinite(instant.getTime())||instant.toISOString().replace('.000Z','Z')!==record.published_at)throw Error('Invalid publication date');
 const parts=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:record.timezone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(instant).map(p=>[p.type,p.value]));
 if(`${parts.year}-${parts.month}-${parts.day}`!==record.version_date)throw Error('Publication version date differs from the local publication date');
 return record;
}
const record=validateAssetPublication(JSON.parse(readFileSync(resolve('../studies/asset_returns/publication-record.json'),'utf8')),readFileSync(resolve('../studies/asset_returns/release-manifest.json')));
export const assetEvidenceVersion:EvidenceVersion={date:record.version_date,revision:record.source_revision,publishedAt:record.published_at,publicationUrl:record.publication_url,manifestUrl:`https://github.com/runchengxie/quant-market-research/blob/${record.source_revision}/studies/asset_returns/release-manifest.json`,explanation:c.versionBasis,acquisition:c.acquisitionBasis};
