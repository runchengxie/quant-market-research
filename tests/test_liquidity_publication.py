import hashlib
import json

import pytest

from market_research.liquidity_publication import reviewed_publication


def fixture():
    bucket = dict(
        label="< $10m",
        count=1,
        observations=1,
        median_usd=10.0,
        mean_usd=10.0,
        p10_usd=10.0,
        p25_usd=10.0,
        p75_usd=10.0,
        p90_usd=10.0,
        zero_adv20_observations=0,
        zero_adv20_share=0.0,
        median20_median_usd=8.0,
        median20_mean_usd=8.0,
        median20_p10_usd=8.0,
        median20_p25_usd=8.0,
        median20_p75_usd=8.0,
        median20_p90_usd=8.0,
    )
    labels = ["< $10m", "$10m-$100m", "$100m-$1bn", "$1bn-$10bn", ">= $10bn"]
    buckets = [bucket] + [
        dict(
            bucket,
            label=label,
            count=0,
            observations=0,
            median_usd=None,
            mean_usd=None,
            p10_usd=None,
            p25_usd=None,
            p75_usd=None,
            p90_usd=None,
            zero_adv20_observations=0,
            zero_adv20_share=None,
            median20_median_usd=None,
            median20_mean_usd=None,
            median20_p10_usd=None,
            median20_p25_usd=None,
            median20_p75_usd=None,
            median20_p90_usd=None,
        )
        for label in labels[1:]
    ]
    market = dict(
        market="US",
        status="derived",
        aggregation="snapshot",
        as_of="2025-01-21",
        coverage_start="2025-01-21",
        coverage_end="2025-01-21",
        unique_stocks=1,
        eligible_observations=1,
        below_100m_observations=1,
        fx_start="2025-01-20",
        fx_end="2025-01-20",
        buckets=buckets,
        eligible_stocks=1,
        sub_100m_count=1,
        sub_100m_median_usd=10.0,
    )
    summary = dict(
        schema_version="liquidity.rebuilt.v1",
        generated_on="2026-10-16",
        method={"roll_days": 20, "historical_pit_eligible": False},
        markets=[market],
        periods=[],
        source_profiles={
            "US": {
                "source_rows": 1,
                "observed_stocks": 1,
                "coverage_start": "2025-01-21",
                "coverage_end": "2025-01-21",
                "eligible_observations": 1,
                "exclusions": {"included": 1},
                "duplicate_keys": 0,
            }
        },
        source_receipts=[],
        code_receipts={},
        caveats=[],
    )
    raw = json.dumps(summary).encode()
    review = dict(
        schema_version="liquidity.independent-review.v1",
        reviewed_summary_sha256=hashlib.sha256(raw).hexdigest(),
        aggregate_cells_reconciled=40,
        count_and_reason_conservation=True,
        strict_prior_fx_checked=True,
        actual_execution_calibrated=False,
        full_raw_warehouse_audited=False,
    )
    return summary, raw, review


def test_review_receipt_must_match_exact_proposed_bytes():
    _, raw, review = fixture()
    assert reviewed_publication(raw, review)["markets"][0]["eligible_stocks"] == 1
    with pytest.raises(ValueError, match="checksum"):
        reviewed_publication(raw + b" ", review)


def test_private_fields_and_paths_cannot_enter_publication():
    summary, _, review = fixture()
    for mutation in [
        lambda s: s.update(raw_rows=[]),
        lambda s: s["markets"][0].update(symbol="PRIVATE"),
        lambda s: s.update(caveats=["/home/private/input.parquet"]),
    ]:
        value = json.loads(json.dumps(summary))
        mutation(value)
        raw = json.dumps(value).encode()
        review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
        with pytest.raises(ValueError):
            reviewed_publication(raw, review)


def test_inconsistent_bucket_counts_cannot_be_published_even_with_a_receipt():
    summary, _, review = fixture()
    summary["markets"][0]["eligible_observations"] = 2
    raw = json.dumps(summary).encode()
    review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="observations"):
        reviewed_publication(raw, review)


def test_zero_adv20_share_must_match_observed_eligible_rows():
    summary, _, review = fixture()
    summary["markets"][0]["buckets"][0]["zero_adv20_observations"] = 1
    raw = json.dumps(summary).encode()
    review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="share"):
        reviewed_publication(raw, review)
