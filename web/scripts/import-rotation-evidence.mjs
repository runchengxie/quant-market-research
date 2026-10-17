import { readFile, mkdir, mkdtemp, writeFile, rename, rm } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { validateRotationEvidence } from '../src/content/rotation-evidence.server.ts';
import { canonical } from '../src/content/rotation-evidence.ts';
export async function importRotationEvidence({assetPath,reviewPath,outputDirectory,beforeRename=()=>{}}){const asset=JSON.parse(await readFile(assetPath,'utf8')),review=JSON.parse(await readFile(reviewPath,'utf8'));validateRotationEvidence(asset,review);await mkdir(outputDirectory,{recursive:true});const temporary=await mkdtemp(join(outputDirectory,'.rotation-'));try {const stage=join(temporary,'release.json');await writeFile(stage,canonical({asset,review})+'\n',{flag:'wx'});await beforeRename();await rename(stage,join(outputDirectory,'rotation-evidence-release.json'));}finally{await rm(temporary,{recursive:true});}}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){const [assetPath,reviewPath,outputDirectory]=process.argv.slice(2);if(!assetPath||!reviewPath||!outputDirectory)throw Error('Usage: node --import tsx scripts/import-rotation-evidence.mjs ASSET REVIEW OUTPUT_DIRECTORY');await importRotationEvidence({assetPath,reviewPath,outputDirectory});}
