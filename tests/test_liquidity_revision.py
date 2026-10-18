import duckdb
import pytest


def tables():
    c = duckdb.connect()
    c.execute("CREATE TABLE b(market VARCHAR,symbol VARCHAR,date DATE,adv DOUBLE,eligible BOOLEAN)")
    c.execute(
        "INSERT INTO b VALUES ('A-share','x','2025-01-02',10,true),('A-share','y','2025-01-02',NULL,false)"
    )
    c.execute("CREATE TABLE a AS SELECT * FROM b")
    return c


def test_revision_gate_detects_values_deletions_and_historical_backfill_but_allows_new_dates():
    from market_research.liquidity_revision import compare_features

    c = tables()
    assert compare_features(c, "b", "a")["status"] == "unchanged"
    c.execute("INSERT INTO a VALUES ('A-share','x','2025-01-03',11,true)")
    assert compare_features(c, "b", "a")["status"] == "append_only"
    c.execute("UPDATE a SET adv=12 WHERE symbol='x' AND date='2025-01-02'")
    r = compare_features(c, "b", "a")
    assert r["changed_rows"] == 1 and r["status"] == "review_required"
    c.execute("DELETE FROM a WHERE symbol='y'")
    c.execute("INSERT INTO a VALUES ('A-share','z','2025-01-02',1,true)")
    r = compare_features(c, "b", "a")
    assert r["removed_rows"] == 1 and r["historical_added_rows"] == 1 and r["new_date_rows"] == 1


def test_revision_gate_rejects_duplicate_null_keys_and_schema_drift():
    from market_research.liquidity_revision import compare_features

    c = tables()
    c.execute("INSERT INTO a SELECT * FROM a LIMIT 1")
    with pytest.raises(ValueError, match="duplicate"):
        compare_features(c, "b", "a")
    c = tables()
    c.execute("UPDATE a SET symbol=NULL WHERE symbol='x'")
    with pytest.raises(ValueError, match="null"):
        compare_features(c, "b", "a")
    c = tables()
    c.execute("ALTER TABLE a ADD COLUMN extra INT")
    with pytest.raises(ValueError, match="schema"):
        compare_features(c, "b", "a")


def test_cli_binds_baseline_bytes_and_requires_review_for_changed_history(tmp_path):
    import hashlib
    import os
    from pathlib import Path
    import subprocess
    import sys
    import pandas as pd

    b = tmp_path / "baseline.parquet"
    a = tmp_path / "candidate.parquet"
    frame = pd.DataFrame(
        dict(market=["A-share"], symbol=["x"], date=pd.to_datetime(["2025-01-02"]), adv=[10.0])
    )
    frame.to_parquet(b, index=False)
    frame.assign(adv=12.0).to_parquet(a, index=False)
    command = [
        sys.executable,
        "scripts/audit_liquidity_revision.py",
        "--baseline",
        str(b),
        "--candidate",
        str(a),
        "--output",
        str(tmp_path / "run"),
        "--expected-baseline-sha256",
        hashlib.sha256(b.read_bytes()).hexdigest(),
    ]
    env = {**os.environ, "PYTHONPATH": str(Path("src").resolve())}
    r = subprocess.run(command, env=env, capture_output=True, text=True)
    assert r.returncode == 2 and "review_required" in r.stdout
    command[-1] = "0" * 64
    r = subprocess.run(command, env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "baseline checksum" in r.stderr


def test_replacing_published_feature_version_requires_matching_clean_revision_receipt():
    from market_research.liquidity_revision import validate_replacement

    old = {"source_receipts": [dict(source_id="a_sh_sz_features", sha256="old")]}
    new = {"source_receipts": [dict(source_id="a_sh_sz_features", sha256="new")]}
    validate_replacement(old, old, None)
    with pytest.raises(ValueError, match="revision receipt"):
        validate_replacement(old, new, None)
    receipt = dict(
        schema_version="liquidity.feature-revision.v1",
        sha256=dict(baseline="old", candidate="new"),
        status="append_only",
        changed_rows=0,
        removed_rows=0,
        historical_added_rows=0,
    )
    validate_replacement(old, new, receipt)
    receipt["sha256"]["baseline"] = "stale"
    with pytest.raises(ValueError, match="version binding"):
        validate_replacement(old, new, receipt)
    receipt["sha256"]["baseline"] = "old"
    receipt["status"] = "review_required"
    receipt["changed_rows"] = 1
    with pytest.raises(ValueError, match="historical revisions"):
        validate_replacement(old, new, receipt)
