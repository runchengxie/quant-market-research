import numpy as np
import pandas as pd
import pytest

from market_research.studies.commodity_equity.funded_products import funded_products


def test_initial_final_and_rebalance_costs_are_funded():
    dates = pd.bdate_range("2020-01-01", periods=3)
    levels = pd.DataFrame(
        {"stock": [1, 2, 2], "product": [1, 1, 1], "cash": [1, 1, 1]}, index=dates
    )
    result = funded_products(levels, [0.8, 0.2, 0], {dates[1]}, fee_bps=100)
    assert result["initial_fee"] == pytest.approx(1 - 1 / 1.01)
    assert result["terminal_wealth"] == pytest.approx(
        1 + result["gross_pnl"] - result["total_fees"]
    )
    assert result["trade_events"] == 3
    assert result["final_fee"] > 0
    assert result["ledger"][1]["two_sided_turnover"] > 0


def test_cash_is_not_charged_as_a_second_trade_leg():
    d = pd.bdate_range("2020-01-01", periods=2)
    frame = pd.DataFrame({"stock": [1, 1], "cash": [1, 1]}, index=d)
    r = funded_products(frame, [0.8, 0.2], set(), fee_bps=100)
    expected_open_wealth = 1 / 1.008
    assert r["terminal_wealth"] == pytest.approx(expected_open_wealth * 0.992)


def test_no_fill_or_invalid_weight_admission():
    d = pd.bdate_range("2020-01-01", periods=2)
    with pytest.raises(ValueError):
        funded_products(
            pd.DataFrame({"stock": [1, np.nan], "cash": [1, 1]}, index=d), [0.8, 0.2], set()
        )


def test_registration_cannot_retroactively_start_or_overwrite(tmp_path):
    from market_research.studies.commodity_equity.paper_registry import register_paper

    protocol = {
        "protocol_id": "test",
        "first_eligible_session": "2026-11-09",
        "real_orders": False,
        "initial_capital_CNY": 1000000,
    }
    calendar = pd.DatetimeIndex(["2026-11-06", "2026-11-09"])
    now = pd.Timestamp("2026-11-08T01:00:00Z")
    receipt = register_paper(protocol, calendar, now, tmp_path / "new")
    assert receipt["observed_trades"] == 0
    with pytest.raises(FileExistsError):
        register_paper(protocol, calendar, now, tmp_path / "new")
    with pytest.raises(ValueError, match="future"):
        register_paper(protocol, calendar, pd.Timestamp("2026-11-09T01:00:00Z"), tmp_path / "bad")


def test_paper_rejects_nonfinite_capital(tmp_path):
    from market_research.studies.commodity_equity.paper_registry import register_paper

    protocol = {
        "protocol_id": "bad",
        "first_eligible_session": "2026-11-09",
        "real_orders": False,
        "initial_capital_CNY": float("nan"),
    }
    with pytest.raises(ValueError):
        register_paper(
            protocol,
            pd.DatetimeIndex(["2026-11-09"]),
            pd.Timestamp("2026-11-08T01:00:00Z"),
            tmp_path / "bad",
        )


def test_forward_observation_rejects_early_marks_and_rewrites(tmp_path):
    import hashlib
    import json
    from market_research.studies.commodity_equity.paper_registry import (
        register_paper,
        append_observation,
    )

    protocol = {
        "protocol_id": "test",
        "first_eligible_session": "2026-11-09",
        "real_orders": False,
        "initial_capital_CNY": 1000000,
        "stock_product": "S",
        "commodity_product": "C",
    }
    dates = pd.DatetimeIndex(["2026-11-09", "2026-11-10"])
    registry = tmp_path / "registry"
    register_paper(protocol, dates, pd.Timestamp("2026-11-08T01:00:00Z"), registry)
    source = tmp_path / "owner.json"
    payload = {
        "trade_date": "2026-11-09",
        "available_at": "2026-11-09T07:00:00Z",
        "gross_growth": {"S": 1, "C": 1},
    }

    def write():
        source.write_text(json.dumps(payload))
        return hashlib.sha256(source.read_bytes()).hexdigest()

    with pytest.raises(ValueError, match="availability"):
        append_observation(registry, source, write(), dates, pd.Timestamp("2026-11-09T08:00:00Z"))
    payload["available_at"] = "2026-11-09T08:00:00Z"
    payload["gross_growth"]["S"] = 1.1
    with pytest.raises(ValueError, match="first paper mark"):
        append_observation(registry, source, write(), dates, pd.Timestamp("2026-11-09T09:00:00Z"))
    payload["gross_growth"]["S"] = 1
    append_observation(registry, source, write(), dates, pd.Timestamp("2026-11-09T09:00:00Z"))
    with pytest.raises(ValueError, match="rewriting"):
        append_observation(registry, source, write(), dates, pd.Timestamp("2026-11-09T10:00:00Z"))


def test_reviewed_product_source_and_registered_protocol_bindings():
    import hashlib
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    study = root / "studies/china_commodity_equity"
    summary = json.loads((study / "forward-summary-20261108.json").read_text())
    for name, digest in summary["code_sha256"].items():
        assert (
            hashlib.sha256(
                (root / "src/market_research/studies/commodity_equity" / name).read_bytes()
            ).hexdigest()
            == digest
        )
    protocol = json.loads((study / "paper-protocol-v1.json").read_text())
    registered = json.loads((study / "paper-registration-20261108.json").read_text())
    canonical = (json.dumps(protocol, sort_keys=True, separators=(",", ":")) + "\n").encode()
    assert hashlib.sha256(canonical).hexdigest() == registered["protocol_sha256"]
    assert registered["completed_forward_windows"] == 0 and registered["real_orders"] is False


def test_appended_visibility_cannot_precede_previous_record(tmp_path):
    import hashlib
    import json
    from market_research.studies.commodity_equity.paper_registry import (
        register_paper,
        append_observation,
    )

    dates = pd.DatetimeIndex(["2026-11-09", "2026-11-10"])
    registry = tmp_path / "r"
    register_paper(
        {
            "protocol_id": "test",
            "first_eligible_session": "2026-11-09",
            "real_orders": False,
            "initial_capital_CNY": 1000000,
            "stock_product": "S",
            "commodity_product": "C",
        },
        dates,
        pd.Timestamp("2026-11-08T01:00:00Z"),
        registry,
    )
    source = tmp_path / "owner.json"

    def write(day):
        source.write_text(
            json.dumps(
                {
                    "trade_date": day,
                    "available_at": day + "T08:00:00Z",
                    "gross_growth": {"S": 1, "C": 1},
                }
            )
        )
        return hashlib.sha256(source.read_bytes()).hexdigest()

    append_observation(
        registry, source, write("2026-11-09"), dates, pd.Timestamp("2026-11-12T08:00:00Z")
    )
    with pytest.raises(ValueError, match="backdate"):
        append_observation(
            registry, source, write("2026-11-10"), dates, pd.Timestamp("2026-11-11T08:00:00Z")
        )
