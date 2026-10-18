import hashlib
import json

import pytest

from market_research.liquidity_stress_publication import reviewed_stress


def package():
    value = dict(
        schema_version="liquidity.stress-persistence.v1",
        historical_pit_eligible=False,
        actual_execution_calibrated=False,
        feature_sha256="feature",
        stress=[],
        cohorts=[],
        minute_quality=[
            dict(date="20250102", eligible_candidates=1, accepted=1, reasons={"accepted": 1})
        ],
        windows=[
            dict(
                year=2025,
                window=w,
                observations=1,
                missing_window_observations=0,
                p25=0.1,
                median=0.2,
                p75=0.3,
            )
            for w in ["open30", "late_morning", "afternoon", "close30", "core"]
        ],
    )
    raw = json.dumps(value).encode()
    review = dict(
        passed=True,
        reviewed_summary_sha256=hashlib.sha256(raw).hexdigest(),
        aggregate_cells_checked=1,
        cohort_formations_checked=1,
        raw_minute_dates_checked=1,
    )
    base = dict(source_receipts=[dict(source_id="a_sh_sz_features", sha256="feature")])
    return raw, review, base


def test_review_bytes_and_source_binding_are_required():
    raw, review, base = package()
    assert reviewed_stress(raw, review, base)
    with pytest.raises(ValueError, match="checksum"):
        reviewed_stress(raw + b" ", review, base)
    base["source_receipts"][0]["sha256"] = "other"
    with pytest.raises(ValueError, match="source feature"):
        reviewed_stress(raw, review, base)


def test_sample_denominators_are_not_silently_lost():
    raw, review, base = package()
    value = json.loads(raw)
    value["windows"].pop()
    raw = json.dumps(value).encode()
    review["reviewed_summary_sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(ValueError, match="conserve"):
        reviewed_stress(raw, review, base)
