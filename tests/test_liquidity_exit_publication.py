import copy
import hashlib
import json

import pytest


def package():
    row = dict(
        year=2025,
        bucket=2,
        position_usd=1000000,
        participation=0.03,
        horizon=5,
        mode="raw",
        formations=1,
        stocks=2,
        covered=1,
        not_covered=1,
        unresolved=0,
        static_covered=1,
        covered_day_p50=2,
        covered_day_p95=2,
        all_names_day_max=None,
        uncredited_fraction=0.4,
        top_decile_uncredited_share=1,
    )
    value = dict(
        schema_version="liquidity.exit-exploration.v1",
        feature_sha256="x",
        historical_pit_eligible=False,
        actual_execution_calibrated=False,
        rows=[row, {**row, "mode": "guarded"}],
        quality=dict(path_rows=40, states={"credited": 40}),
    )
    base = dict(source_receipts=[dict(source_id="a_sh_sz_features", sha256="x")])
    return value, base


def checked(value):
    raw = json.dumps(value).encode()
    return raw, dict(
        passed=True,
        reviewed_summary_sha256=hashlib.sha256(raw).hexdigest(),
        aggregate_cells_checked=1,
        raw_path_rows_checked=40,
    )


def test_exit_gate_binds_source_review_and_original_denominator():
    from market_research.liquidity_exit_publication import reviewed_exit

    value, base = package()
    raw, review = checked(value)
    assert reviewed_exit(raw, review, base)
    with pytest.raises(ValueError, match="checksum"):
        reviewed_exit(raw + b" ", review, base)
    broken = copy.deepcopy(value)
    broken["rows"][0]["covered"] = 2
    raw, review = checked(broken)
    with pytest.raises(ValueError, match="denominator"):
        reviewed_exit(raw, review, base)


def test_exit_gate_does_not_publish_censored_maxima_or_improved_guarded_coverage():
    from market_research.liquidity_exit_publication import reviewed_exit

    value, base = package()
    value["rows"][0]["all_names_day_max"] = 5
    raw, review = checked(value)
    with pytest.raises(ValueError, match="censored"):
        reviewed_exit(raw, review, base)
    value, base = package()
    value["rows"][0].update(covered=0, not_covered=2, covered_day_p50=None, covered_day_p95=None)
    raw, review = checked(value)
    with pytest.raises(ValueError, match="guarded"):
        reviewed_exit(raw, review, base)


def test_every_public_companion_rejects_private_paths_and_security_identifiers():
    from market_research.liquidity_exit_publication import validate_public_payload

    validate_public_payload({"reviewed": True, "count": 3})
    for payload in [{"note": "/home/example/private.json"}, {"note": "000001.SZ"}]:
        with pytest.raises(ValueError):
            validate_public_payload(payload)
