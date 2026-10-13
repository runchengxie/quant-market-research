import hashlib
import json

import pandas as pd
import pytest

from market_research.studies.ashare_execution_costs.factor_evidence import validate_factor_evidence


def fixture(tmp_path, stable=False):
    marks = pd.DataFrame(
        dict(
            ts_code=["000001.SZ"] * 2,
            trade_date=["20240102", "20240103"],
            open=[10.0, 10.0],
            high=[10.0, 10.0],
            low=[10.0, 10.0],
            close=[10.0, 10.0],
            pre_close=[10.0, 10.0],
            adj_factor=[1.0, 1.01],
        )
    )

    def ref(name, value, parquet=False):
        path = tmp_path / name
        if parquet:
            value.to_parquet(path, index=False)
        else:
            path.write_text(json.dumps(value))
        return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    diagnostic = ref(
        "diagnostic.parquet",
        pd.DataFrame(
            dict(
                ts_code=["000001.SZ"],
                trade_date=["20240103"],
                adj_factor_clean=[1.01],
                prev=[1.0],
                prev_trade_date=["20240102"],
            )
        ),
        True,
    )
    fresh = ref(
        "fresh.parquet",
        pd.DataFrame(
            dict(
                ts_code=["000001.SZ"] * 2,
                trade_date=["20240102", "20240103"],
                adj_factor=[1.0, 1.0 if stable else 1.01],
            )
        ),
        True,
    )
    queries = []
    for kind, fields, rows, params in [
        (
            "raw_daily",
            ["date", "code", "open", "high", "low", "close", "preclose"],
            [
                ["2024-01-02", "sz.000001", "10", "10", "10", "10", "10"],
                ["2024-01-03", "sz.000001", "10", "10", "10", "10", "10"],
            ],
            dict(start_date="2024-01-02", end_date="2024-01-03", adjustflag="3"),
        ),
        (
            "back_adjusted_daily",
            ["date", "code", "close"],
            [["2024-01-02", "sz.000001", "20"], ["2024-01-03", "sz.000001", "20"]],
            dict(start_date="2024-01-02", end_date="2024-01-03", adjustflag="1"),
        ),
        (
            "adjustment_events",
            ["code", "dividOperateDate"],
            [],
            dict(start_date="2024-01-01", end_date="2024-12-31"),
        ),
        ("dividends", ["code", "dividOperateDate"], [], dict(year="2024", yearType="operate")),
    ]:
        params["code"] = "sz.000001"
        response = ref(kind + ".json", dict(fields=fields, rows=rows, error_code="0"))
        queries.append(
            dict(
                symbol="000001.SZ",
                kind=kind,
                params=params,
                error_code="0",
                rows=len(rows),
                file=response["path"],
                sha256=response["sha256"],
            )
        )
    independent = ref("receipt.json", dict(provider="baostock", queries=queries))
    packet = dict(
        schema_version="execution-factor-evidence.v1",
        scope="raw_price_execution_event_screen",
        study={"start": "20240102", "end": "20240103", "symbols": ["000001.SZ"]},
        diagnostic=diagnostic,
        reobservations=[fresh],
        independent_receipt=independent,
        daily_manifest_sha256="a" * 64,
        dividend_sha256="b" * 64,
    )
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(packet))
    return marks, path


def validate(marks, path):
    return validate_factor_evidence(
        marks, set(), path, daily_manifest_sha256="a" * 64, dividend_sha256="b" * 64
    )


def test_actual_cross_source_prices_and_events_explain_alarm_without_mutating_factor(tmp_path):
    marks, path = fixture(tmp_path)
    before = marks.copy(deep=True)
    audit = validate(marks, path)
    assert audit["cross_source_nonaction_keys"] == 1
    assert audit["unexplained_changes"] == 0
    pd.testing.assert_frame_equal(marks, before)


def test_stable_reobservation_still_requires_unchanged_market_reference(tmp_path):
    marks, path = fixture(tmp_path, stable=True)
    assert validate(marks, path)["reobserved_stable_keys"] == 1
    marks.loc[1, "pre_close"] = 9.99
    with pytest.raises(ValueError, match="reference"):
        validate(marks, path)


def test_new_key_or_changed_original_value_is_never_exempted_by_old_packet(tmp_path):
    marks, path = fixture(tmp_path)
    marks.loc[1, "adj_factor"] = 1.02
    with pytest.raises(ValueError, match="original"):
        validate(marks, path)
    marks, path = fixture(tmp_path)
    extra = marks.iloc[-1:].assign(trade_date="20240104", adj_factor=1.02)
    packet = json.loads(path.read_text())
    packet["study"]["end"] = "20240104"
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="uncovered"):
        validate(pd.concat([marks, extra]), path)


def test_modified_native_response_and_incomplete_query_coverage_reject(tmp_path):
    marks, path = fixture(tmp_path)
    p = tmp_path / "raw_daily.json"
    p.write_text(p.read_text() + " ")
    with pytest.raises(ValueError, match="hash"):
        validate(marks, path)


def test_observed_economic_event_or_changing_adjusted_ratio_blocks(tmp_path):
    marks, path = fixture(tmp_path)
    # Rebind a deliberately changed response to distinguish semantics from hash checks.
    for filename, change in [
        ("adjustment_events.json", "event"),
        ("back_adjusted_daily.json", "ratio"),
    ]:
        marks, path = fixture(tmp_path)
        p = tmp_path / filename
        v = json.loads(p.read_text())
        if change == "event":
            v["rows"] = [["sz.000001", "2024-01-03"]]
        else:
            v["rows"][1][-1] = "20.1"
        p.write_text(json.dumps(v))
        receipt = tmp_path / "receipt.json"
        r = json.loads(receipt.read_text())
        for q in r["queries"]:
            if q["file"] == filename:
                q["rows"] = len(v["rows"])
                q["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
        receipt.write_text(json.dumps(r))
        packet = json.loads(path.read_text())
        packet["independent_receipt"]["sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
        path.write_text(json.dumps(packet))
        with pytest.raises(ValueError, match="economic event|ratio"):
            validate(marks, path)


def test_stable_reobservation_cannot_hide_available_independent_event(tmp_path):
    marks, path = fixture(tmp_path, stable=True)
    p = tmp_path / "adjustment_events.json"
    v = json.loads(p.read_text())
    v["rows"] = [["sz.000001", "2024-01-03"]]
    p.write_text(json.dumps(v))
    receipt = tmp_path / "receipt.json"
    r = json.loads(receipt.read_text())
    for q in r["queries"]:
        if q["kind"] == "adjustment_events":
            q["rows"] = 1
            q["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(r))
    packet = json.loads(path.read_text())
    packet["independent_receipt"]["sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="economic event"):
        validate(marks, path)


def test_tiny_independent_ratio_change_is_not_ignored_by_precision_threshold(tmp_path):
    marks, path = fixture(tmp_path)
    response = tmp_path / "back_adjusted_daily.json"
    value = json.loads(response.read_text())
    value["rows"][1][-1] = "20.00000000001"
    response.write_text(json.dumps(value))
    receipt = tmp_path / "receipt.json"
    data = json.loads(receipt.read_text())
    for query in data["queries"]:
        if query["kind"] == "back_adjusted_daily":
            query["sha256"] = hashlib.sha256(response.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(data))
    packet = json.loads(path.read_text())
    packet["independent_receipt"]["sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="ratio"):
        validate(marks, path)


@pytest.mark.parametrize("value", [1.0, float("nan"), 0.0])
def test_changed_original_alarm_cannot_disappear_before_binding_check(tmp_path, value):
    marks, path = fixture(tmp_path)
    marks.loc[1, "adj_factor"] = value
    with pytest.raises(ValueError, match="original|invalid factor"):
        validate(marks, path)


def test_missing_original_key_in_a_declared_window_rejects(tmp_path):
    marks, path = fixture(tmp_path)
    end = marks.iloc[-1:].assign(trade_date="20240104")
    packet = json.loads(path.read_text())
    packet["study"]["end"] = "20240104"
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="original"):
        validate(pd.concat([marks.iloc[:1], end]), path)


def test_unknown_economic_event_date_cannot_establish_absence(tmp_path):
    marks, path = fixture(tmp_path)
    response = tmp_path / "adjustment_events.json"
    value = json.loads(response.read_text())
    value["rows"] = [["sz.000001", None]]
    response.write_text(json.dumps(value))
    receipt = tmp_path / "receipt.json"
    data = json.loads(receipt.read_text())
    for query in data["queries"]:
        if query["kind"] == "adjustment_events":
            query["rows"] = 1
            query["sha256"] = hashlib.sha256(response.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(data))
    packet = json.loads(path.read_text())
    packet["independent_receipt"]["sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="economic event"):
        validate(marks, path)
