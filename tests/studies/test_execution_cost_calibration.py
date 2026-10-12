import pandas as pd
import pytest
from market_research.studies.ashare_execution_costs.calibration import (
    measure_orders,
    chronological_validation,
    public_calibration,
)

T = "2026-01-05T01:30:"


def inputs(side="buy"):
    orders = pd.DataFrame(
        [
            dict(
                parent_order_id="private-parent",
                symbol="private-symbol",
                side=side,
                target_qty=100,
                decision_time=T + "00Z",
                arrival_time=T + "01Z",
                end_time=T + "10Z",
                state="cancelled",
                fees_cny=1,
            )
        ]
    )
    fills = pd.DataFrame(
        [
            dict(
                fill_id="private-fill",
                parent_order_id="private-parent",
                fill_time=T + "02Z",
                qty=60,
                price=10.02,
            )
        ]
    )
    quotes = pd.DataFrame(
        [
            dict(
                symbol="private-symbol",
                quote_time=T + sec + "Z",
                bid=mid - 0.01,
                ask=mid + 0.01,
                market_level=100,
            )
            for sec, mid in [("00", 10), ("01", 10.01), ("10", 10.03)]
        ]
    )
    return orders, fills, quotes


def test_partial_buy_reconciles_execution_opportunity_fees():
    result = measure_orders(*inputs(), data_kind="synthetic", max_quote_age_ms=1000)
    row = result.iloc[0]
    assert row.decision_execution_cny == pytest.approx(1.2)
    assert row.opportunity_cny == pytest.approx(1.2)
    assert row.shortfall_bp == pytest.approx(34)
    assert row.arrival_execution_bp == pytest.approx(10000 * (10.02 / 10.01 - 1))
    assert row.filled_qty == 60 and row.unfilled_qty == 40


def test_sell_direction_and_unfilled_no_fill():
    o, f, q = inputs("sell")
    f.price = 9.98
    q.loc[2, ["bid", "ask"]] = [9.96, 9.98]
    row = measure_orders(o, f, q, data_kind="paper").iloc[0]
    assert row.shortfall_bp == pytest.approx(34)
    o, f, q = inputs()
    f = f.iloc[:0]
    row = measure_orders(o, f, q, data_kind="synthetic").iloc[0]
    assert pd.isna(row.arrival_execution_bp)
    assert row.shortfall_bp == pytest.approx(40)


@pytest.mark.parametrize(
    "problem",
    [
        "duplicate_fill",
        "orphan_fill",
        "overfill",
        "late_fill",
        "timezone",
        "negative_fee",
        "open_state",
        "invalid_kind",
        "future_quote",
        "stale_quote",
        "duplicate_quote",
    ],
)
def test_bad_records_never_become_calibration(problem):
    o, f, q = inputs()
    kind = "synthetic"
    if problem == "duplicate_fill":
        f = pd.concat([f, f])
    if problem == "orphan_fill":
        f.parent_order_id = "unknown"
    if problem == "overfill":
        f.qty = 101
    if problem == "late_fill":
        f.fill_time = T + "11Z"
    if problem == "timezone":
        o.decision_time = "2026-01-05 09:30:00"
    if problem == "negative_fee":
        o.fees_cny = -1
    if problem == "open_state":
        o.state = "open"
    if problem == "invalid_kind":
        kind = "pretend_actual"
    if problem == "future_quote":
        q = q.iloc[1:]
    if problem == "stale_quote":
        q = q.iloc[:1]
    if problem == "duplicate_quote":
        q = pd.concat([q, q.iloc[:1]])
    if problem in ["future_quote", "stale_quote"]:
        row = measure_orders(o, f, q, data_kind=kind, max_quote_age_ms=1000).iloc[0]
        assert not row.calibration_eligible and pd.isna(row.shortfall_bp)
    else:
        with pytest.raises(ValueError):
            measure_orders(o, f, q, data_kind=kind, max_quote_age_ms=1000)


def test_filled_state_must_reconcile_quantity():
    o, f, q = inputs()
    o.state = "filled"
    with pytest.raises(ValueError):
        measure_orders(o, f, q, data_kind="synthetic")


def test_chronological_test_date_never_trains_and_synthetic_never_actual():
    frame = pd.DataFrame(
        [
            dict(
                parent_order_id=str(i),
                arrival_time=pd.Timestamp(f"2026-01-{i + 1:02}T01:30:00Z"),
                end_time=pd.Timestamp(f"2026-01-{i + 1:02}T01:31:00Z"),
                arrival_execution_bp=float(i),
                predicted_arrival_bp=1.0,
                side="buy",
                calibration_eligible=True,
                data_kind="synthetic",
            )
            for i in range(8)
        ]
    )
    validation = chronological_validation(
        frame, train_fraction=0.75, min_train_orders=4, min_test_orders=2
    )
    assert validation["train_orders"] == 6 and validation["test_orders"] == 2
    assert validation["baseline_test_mae_bp"] == pytest.approx(4)
    public = public_calibration(frame, validation, min_group_orders=20)
    assert public["actual_order_calibrated"] is False
    assert "private-parent" not in str(public) and "parent_order_id" not in str(public)
    frame.loc[7, "arrival_time"] = frame.loc[5, "arrival_time"]
    validation = chronological_validation(frame, min_train_orders=4, min_test_orders=2)
    assert validation["train_end"] < validation["test_start"]


def test_quote_available_after_arrival_is_not_used_and_no_causal_response():
    o, f, q = inputs()
    q["available_time"] = q.quote_time
    q.loc[1, "available_time"] = T + "02Z"
    row = measure_orders(o, f, q, data_kind="synthetic", max_quote_age_ms=500).iloc[0]
    assert not row.calibration_eligible and pd.isna(row.arrival_execution_bp)
    o, f, q = inputs()
    q = pd.concat(
        [
            q,
            pd.DataFrame(
                [
                    dict(
                        symbol="private-symbol",
                        quote_time=T + "40Z",
                        bid=10.09,
                        ask=10.11,
                        market_level=101,
                    )
                ]
            ),
        ]
    )
    row = measure_orders(o, f, q, data_kind="synthetic").iloc[0]
    import math

    assert row.market_adjusted_response_30s_bp == pytest.approx(
        (math.log(10.1 / 10.03) - math.log(101 / 100)) * 10000
    )


def test_future_supplied_predictions_are_rejected():
    o, f, q = inputs()
    o["predicted_arrival_bp"] = 2
    o["prediction_time"] = T + "02Z"
    with pytest.raises(ValueError):
        measure_orders(o, f, q, data_kind="synthetic")


def test_mixed_evidence_cannot_train_or_publish_as_actual():
    frame = pd.DataFrame(
        [
            dict(
                parent_order_id=str(i),
                arrival_time=pd.Timestamp(f"2026-01-{i + 1:02}T01:30:00Z"),
                end_time=pd.Timestamp(f"2026-01-{i + 1:02}T01:31:00Z"),
                arrival_execution_bp=float(i),
                side="buy",
                calibration_eligible=True,
                data_kind="actual" if i < 4 else "synthetic",
            )
            for i in range(8)
        ]
    )
    with pytest.raises(ValueError):
        chronological_validation(frame, min_train_orders=2, min_test_orders=2)


def test_publication_rejects_private_side_labels():
    frame = pd.DataFrame(
        [
            dict(
                data_kind="synthetic",
                side="/private/order",
                calibration_eligible=True,
                shortfall_bp=2,
            )
            for _ in range(20)
        ]
    )
    with pytest.raises(ValueError):
        public_calibration(frame, {"status": "insufficient_data"})


def test_csv_entry_roundtrip_preserves_kind_and_private_identity(tmp_path):
    import importlib.util
    import json
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "calibration_runner",
        Path(__file__).resolve().parents[2] / "scripts/run_execution_cost_calibration.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / "source"
    source.mkdir()
    o, f, q = inputs()
    for name, frame in [("orders", o), ("fills", f), ("quotes", q)]:
        frame.to_csv(source / (name + ".csv"), index=False)
    manifest = dict(
        schema_version="ashare_execution_costs.canonical_orders.v1",
        data_kind="synthetic",
        price_unit="CNY",
        quantity_unit="share",
        source="synthetic algebra fixture",
        time_contract="explicit_UTC_offset",
        fees_contract="actual_parent_total_CNY_once",
    )
    (source / "manifest.json").write_text(json.dumps(manifest))
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        module.run(source, tmp_path / "unsafe", min_group_orders=19)
    public = module.run(source, output)
    assert public["actual_order_calibrated"] is False
    assert public["orders"] == 1 and public["eligible_orders"] == 1
    assert "private-parent" not in json.dumps(public)
    with pytest.raises(FileExistsError):
        module.run(source, output)
    manifest["quantity_unit"] = "lot"
    (source / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        module.run(source, tmp_path / "bad")


def test_publication_minimum_is_hard_and_cli_enforced(tmp_path):
    frame = pd.DataFrame(
        [
            dict(data_kind="synthetic", side="buy", calibration_eligible=True, shortfall_bp=2)
            for _ in range(20)
        ]
    )
    with pytest.raises(ValueError):
        public_calibration(frame, {"status": "insufficient_data"}, min_group_orders=19)


def test_training_parent_finishing_in_holdout_is_purged():
    frame = pd.DataFrame(
        [
            dict(
                parent_order_id=str(i),
                arrival_time=pd.Timestamp(f"2026-01-{i + 1:02}T01:30:00Z"),
                end_time=pd.Timestamp("2026-01-20T01:30:00Z"),
                arrival_execution_bp=float(i),
                side="buy",
                calibration_eligible=True,
                data_kind="synthetic",
            )
            for i in range(8)
        ]
    )
    result = chronological_validation(
        frame, train_fraction=0.75, min_train_orders=2, min_test_orders=2
    )
    assert result["status"] == "insufficient_data"
    assert result["train_orders"] == 0 and result["purged_training_orders"] == 6
