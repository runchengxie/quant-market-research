import hashlib
import json

import pytest

from market_research.liquidity_relative_publication import reviewed_relative
from test_liquidity_relative import fixture
from market_research.liquidity_relative import rank_features, summarize_relative


def proposal():
    con, template = fixture()
    rank_features(con, "features", "ranked")
    period = summarize_relative(con, "ranked", template)
    base_raw = json.dumps(dict(markets=template["markets"], periods=[template])).encode()
    data = dict(
        schema_version="liquidity.relative.v1",
        absolute_summary_sha256=hashlib.sha256(base_raw).hexdigest(),
        method="daily quintiles",
        code_receipts={},
        feature_receipts=[],
        markets=period["markets"],
        periods=[period],
    )
    raw = json.dumps(data).encode()
    review = dict(
        reviewed_summary_sha256=hashlib.sha256(raw).hexdigest(),
        aggregate_cells_reconciled=1,
        absolute_aggregate_cells_reconciled=1,
        feature_checksums_verified=True,
        independent_daily_membership_checked=True,
    )
    return data, raw, review, base_raw


def test_relative_release_binds_review_and_base_and_does_not_allow_private_fields():
    data, raw, review, base_raw = proposal()
    assert reviewed_relative(raw, review, base_raw)["markets"][0]["eligible_stocks"] == 5
    with pytest.raises(ValueError, match="checksum"):
        reviewed_relative(raw + b" ", review, base_raw)
    with pytest.raises(ValueError, match="base"):
        reviewed_relative(raw, review, base_raw + b" ")
    data["markets"][0]["buckets"][0]["symbol"] = "PRIVATE"
    raw = json.dumps(data).encode()
    review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="fields"):
        reviewed_relative(raw, review, base_raw)


def test_changed_relative_denominator_is_rejected():
    data, _, review, base_raw = proposal()
    data["markets"][0]["eligible_observations"] = 6
    raw = json.dumps(data).encode()
    review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="universe"):
        reviewed_relative(raw, review, base_raw)


def test_relative_zero_share_and_quantile_order_are_validated():
    data, _, review, base_raw = proposal()
    data["markets"][0]["buckets"][0]["zero_adv20_share"] = 0.5
    raw = json.dumps(data).encode()
    review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="statistics"):
        reviewed_relative(raw, review, base_raw)

    data, _, review, base_raw = proposal()
    data["markets"][0]["buckets"][0]["p10_usd"] = 21
    raw = json.dumps(data).encode()
    review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="quantiles"):
        reviewed_relative(raw, review, base_raw)


@pytest.mark.parametrize(
    "key", ["feature_checksums_verified", "absolute_aggregate_cells_reconciled"]
)
def test_relative_review_cannot_omit_input_or_absolute_checks(key):
    _, raw, review, base_raw = proposal()
    review.pop(key)
    with pytest.raises(ValueError, match="incomplete"):
        reviewed_relative(raw, review, base_raw)
