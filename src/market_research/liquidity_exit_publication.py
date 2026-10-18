"""Publication boundaries for reviewed frozen-name arithmetic budget sensitivities."""

import hashlib
import json
import math
import re

from .liquidity_publication import _safe


def validate_public_payload(value: dict) -> None:
    """Apply the same private-data boundary to aggregates and every receipt."""
    _safe(value)
    if re.search(r"\b\d{6}\.(SH|SZ|BJ)\b", json.dumps(value, ensure_ascii=False)):
        raise ValueError("security identifiers cannot be public")


def reviewed_exit(raw: bytes, review: dict, base: dict) -> dict:
    if (
        review.get("passed") is not True
        or review.get("reviewed_summary_sha256") != hashlib.sha256(raw).hexdigest()
    ):
        raise ValueError("review checksum mismatch")
    result = json.loads(raw)
    validate_public_payload(result)
    validate_public_payload(review)
    if re.search(r"\b\d{6}\.(SH|SZ|BJ)\b", raw.decode()):
        raise ValueError("security identifiers cannot be public")
    expected = next(
        r["sha256"] for r in base["source_receipts"] if r["source_id"] == "a_sh_sz_features"
    )
    if result["feature_sha256"] != expected:
        raise ValueError("source feature checksum mismatch")
    if (
        result["schema_version"] != "liquidity.exit-exploration.v1"
        or result["historical_pit_eligible"] is not False
        or result["actual_execution_calibrated"] is not False
    ):
        raise ValueError("invalid evidence declaration")
    if (
        review.get("aggregate_cells_checked", 0) <= 0
        or review.get("raw_path_rows_checked") != result["quality"]["path_rows"]
        or sum(result["quality"]["states"].values()) != result["quality"]["path_rows"]
    ):
        raise ValueError("source path review does not conserve rows")
    paired = {}
    for r in result["rows"]:
        n = r["stocks"]
        c = r["covered"]
        h = r["horizon"]
        if (
            not isinstance(n, int)
            or n <= 0
            or any(
                not isinstance(r[k], int) or r[k] < 0
                for k in ["covered", "not_covered", "unresolved", "static_covered"]
            )
            or c + r["not_covered"] + r["unresolved"] != n
            or r["static_covered"] > n
        ):
            raise ValueError("original stock denominator not conserved")
        if r["all_names_day_max"] is not None and (c != n or not 1 <= r["all_names_day_max"] <= h):
            raise ValueError("censored original names cannot have a completion maximum")
        for key in ["covered_day_p50", "covered_day_p95"]:
            v = r[key]
            if (c == 0 and v is not None) or (c > 0 and (v is None or not 1 <= v <= h)):
                raise ValueError("invalid covered-only day quantile")
        if c and r["covered_day_p50"] > r["covered_day_p95"]:
            raise ValueError("day quantiles out of order")
        if not 0 <= r["uncredited_fraction"] <= 1:
            raise ValueError("invalid residual fraction")
        tail = r["top_decile_uncredited_share"]
        if tail is not None and not 0 <= tail <= 1 + 1e-12:
            raise ValueError("invalid residual concentration")
        if not (r["position_usd"] > 0 and 0 < r["participation"] <= 1 and 1 <= h <= 20):
            raise ValueError("invalid scenario")
        key = tuple(r[k] for k in ["year", "bucket", "position_usd", "participation", "horizon"])
        group = paired.setdefault(key, {})
        if r["mode"] not in ["raw", "guarded"] or r["mode"] in group:
            raise ValueError("duplicate or unknown scenario mode")
        group[r["mode"]] = r
    for group in paired.values():
        if set(group) != set(["raw", "guarded"]):
            raise ValueError("both source modes required")
        a, b = group["raw"], group["guarded"]
        if (
            b["stocks"] != a["stocks"]
            or b["covered"] > a["covered"]
            or b["uncredited_fraction"] + 1e-12 < a["uncredited_fraction"]
        ):
            raise ValueError("guarded budget cannot improve raw budget coverage")
        if not math.isfinite(b["uncredited_fraction"]):
            raise ValueError("nonfinite budget")
    return result
