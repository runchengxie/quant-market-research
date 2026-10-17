import { createHash } from "node:crypto";
import {
  canonical,
  validateShape,
  validatePublicText,
  type Review,
} from "./rotation-evidence";
const sha = (s: string) => createHash("sha256").update(s).digest("hex");
export function validateRotationEvidence(value: unknown, record: unknown) {
  const asset = validateShape(value);
  const review = record as Review;
  if (
    !review ||
    typeof review !== "object" ||
    Array.isArray(review) ||
    Object.keys(review).sort().join(",") !==
      [
        "status",
        "source_sha256",
        "content_sha256",
        "asset_sha256",
        "reviewer",
        "reviewed_at",
      ]
        .sort()
        .join(",")
  )
    throw Error("Unreviewed public review fields");
  Object.values(review).forEach(validatePublicText);
  if (
    review.status !== "approved" ||
    typeof review.reviewer !== "string" ||
    !review.reviewer ||
    !/[Zz]|[+-]\d\d:\d\d$/.test(review.reviewed_at) ||
    !Number.isFinite(Date.parse(review.reviewed_at)) ||
    review.source_sha256 !== asset.reviewed_source_digest ||
    review.content_sha256 !== sha(canonical(asset)) ||
    review.asset_sha256 !== sha(canonical(asset) + "\n")
  )
    throw Error("Rotation source/content/asset review mismatch");
  return asset;
}
