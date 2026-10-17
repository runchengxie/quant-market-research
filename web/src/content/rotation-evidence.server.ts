import { createHash } from "node:crypto";
import { canonical, validateShape, type Review } from "./rotation-evidence";
const sha = (s: string) => createHash("sha256").update(s).digest("hex");
export function validateRotationEvidence(value: unknown, record: unknown) {
  const asset = validateShape(value);
  const review = record as Review;
  if (
    !review ||
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
        .join(",") ||
    Object.values(review).some(
      (v) =>
        typeof v !== "string" ||
        !v ||
        v.length > 1000 ||
        /\/home\/|\/tmp\/|API_KEY|TOKEN=|SECRET/.test(v),
    ) ||
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
