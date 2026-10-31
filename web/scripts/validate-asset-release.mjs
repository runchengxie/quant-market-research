import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

export function validateAssetRelease(read, manifest) {
  if (manifest.schema_version !== 1 || Object.keys(manifest.files).length !== 4) throw new Error('Invalid asset release manifest');
  for (const [path, expected] of Object.entries(manifest.files)) {
    const blob = read(path);
    if (createHash('sha256').update(blob).digest('hex') !== expected) throw new Error(`Unreviewed asset release: ${path}`);
    JSON.parse(blob);
  }
  return true;
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const root = new URL('../../', import.meta.url);
  const manifest = JSON.parse(readFileSync(new URL('studies/asset_returns/release-manifest.json', root)));
  validateAssetRelease(path => readFileSync(new URL(path, root)), manifest);
  console.log('Reviewed asset release and prospective protocol verified');
}
