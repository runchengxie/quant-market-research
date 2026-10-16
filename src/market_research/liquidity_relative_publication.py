"""Publish relative-size aggregates only for their reviewed absolute base release."""

from __future__ import annotations

import hashlib
import json

from .liquidity_publication import BUCKET, MARKET, PERIOD, _fields, _safe
from .liquidity_relative import RELATIVE_LABELS

REMOVED = {"below_100m_observations", "sub_100m_count", "sub_100m_median_usd"}


def _match_market(item, base):
    _fields(item, MARKET - REMOVED)
    if {k: v for k, v in item.items() if k != "buckets"} != {
        k: v for k, v in base.items() if k != "buckets" and k not in REMOVED
    }:
        raise ValueError("relative universe or metadata differs from base")
    if [b["label"] for b in item["buckets"]] != list(RELATIVE_LABELS):
        raise ValueError("relative bucket definitions differ")
    for b in item["buckets"]:
        _fields(b, BUCKET | {"cap_min_usd", "cap_max_usd"})
        n, stocks = b["observations"], b["count"]
        if type(n) is not int or type(stocks) is not int or not 0 <= stocks <= n:
            raise ValueError("invalid relative sample counts")
        metrics = [b[k] for k in BUCKET - {"label", "observations", "count"}] + [
            b["cap_min_usd"],
            b["cap_max_usd"],
        ]
        if n == 0:
            if any(v is not None for v in metrics):
                raise ValueError("empty relative buckets must retain null statistics")
        elif (
            any(type(v) not in (int, float) or v < 0 for v in metrics)
            or not 0 < b["cap_min_usd"] <= b["cap_max_usd"]
        ):
            raise ValueError("invalid relative statistics")
    if sum(b["observations"] for b in item["buckets"]) != item["eligible_observations"]:
        raise ValueError("relative bucket counts do not conserve universe")
    if (
        item["aggregation"] == "snapshot"
        and sum(b["count"] for b in item["buckets"]) != item["eligible_stocks"]
    ):
        raise ValueError("snapshot stock count does not conserve universe")


def reviewed_relative(raw: bytes, review: dict, base_raw: bytes) -> dict:
    if hashlib.sha256(raw).hexdigest() != review.get("reviewed_summary_sha256"):
        raise ValueError("relative review checksum mismatch")
    if not (
        review.get("independent_daily_membership_checked") is True
        and review.get("aggregate_cells_reconciled", 0) > 0
        and review.get("absolute_aggregate_cells_reconciled", 0) > 0
        and review.get("feature_checksums_verified") is True
    ):
        raise ValueError("relative independent review incomplete")
    data = json.loads(raw)
    base = json.loads(base_raw)
    if hashlib.sha256(base_raw).hexdigest() != data["absolute_summary_sha256"]:
        raise ValueError("absolute base checksum mismatch")
    _safe(data)
    _fields(
        data,
        {
            "schema_version",
            "absolute_summary_sha256",
            "method",
            "code_receipts",
            "feature_receipts",
            "markets",
            "periods",
        },
    )
    if data["schema_version"] != "liquidity.relative.v1":
        raise ValueError("unknown relative schema")
    _fields(data["code_receipts"], {"build_liquidity_relative.py", "liquidity_relative.py"})
    for receipt in data["feature_receipts"]:
        _fields(receipt, {"market", "bytes", "sha256"})
    if len(data["periods"]) != len(base["periods"]):
        raise ValueError("relative period coverage differs from base")
    collections = [(data["markets"], base["markets"])]
    for p, b in zip(data["periods"], base["periods"], strict=True):
        _fields(p, PERIOD)
        if {k: v for k, v in p.items() if k != "markets"} != {
            k: v for k, v in b.items() if k != "markets"
        }:
            raise ValueError("relative period dates differ from base")
        collections.append((p["markets"], b["markets"]))
    for items, originals in collections:
        if [m["market"] for m in items] != [m["market"] for m in originals]:
            raise ValueError("relative market coverage differs from base")
        for item, original in zip(items, originals, strict=True):
            _match_market(item, original)
    return data
