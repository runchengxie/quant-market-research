import { createHash } from 'node:crypto';
import { canonical, validatePublicText } from './rotation-evidence';
import { validateExtensionShape } from './rotation-extension';
export function validateRotationExtension(value: unknown, record: unknown) {
    const asset = validateExtensionShape(value);
    if (!record || typeof record !== 'object' || Array.isArray(record))
        throw Error('Missing review');
    const review = record as Record<string, string>;
    if (Object.keys(review).sort().join() !== ['status', 'source_sha256', 'content_sha256', 'asset_sha256', 'reviewer', 'reviewed_at'].sort().join())
        throw Error('Unknown review fields');
    Object.values(review).forEach(v => { validatePublicText(v); if (typeof v !== 'string' || !v)
        throw Error('Invalid review text'); });
    const sha = (s: string) => createHash('sha256').update(s).digest('hex');
    if (review.status !== 'approved' || review.source_sha256 !== asset.reviewed_source_digest || review.content_sha256 !== sha(canonical(asset)) || review.asset_sha256 !== sha(canonical(asset) + '\n') || !/(Z|[+-]\d{2}:\d{2})$/.test(review.reviewed_at) || !Number.isFinite(Date.parse(review.reviewed_at)))
        throw Error('Extension review mismatch');
    return asset;
}
