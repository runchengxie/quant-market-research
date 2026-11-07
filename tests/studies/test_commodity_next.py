import numpy as np
import pandas as pd
import pytest

from market_research.studies.commodity_equity.risk_controls import lagged_risk_control
from market_research.studies.commodity_equity.contract_trial import settlement_trial


def test_risk_weights_do_not_use_future_prices():
    dates = pd.bdate_range("2010-01-01", periods=850)
    rng = np.random.default_rng(3)
    panel = pd.DataFrame(
        np.exp(np.cumsum(rng.normal(0, 0.01, (850, 2)), axis=0)),
        index=dates,
        columns=["equity", "commodity"],
    )
    ends = pd.DatetimeIndex(pd.Series(dates, index=dates.to_period("M")).groupby(level=0).max())
    first = lagged_risk_control(panel, ends, lookback=60)
    changed = panel.copy()
    changed.loc[dates[500] :, "commodity"] *= 20
    second = lagged_risk_control(changed, ends, lookback=60)
    pd.testing.assert_series_equal(
        first["weights"].loc[: dates[499]], second["weights"].loc[: dates[499]]
    )
    assert first["weights"].between(0, 1).all()
    assert first["nav"].iloc[0] == 1


def trial_input():
    dates = pd.bdate_range("2025-01-01", periods=4)
    rows = []
    for d in dates:
        for code, price in [("A", 100 + dates.get_loc(d)), ("B", 200 + dates.get_loc(d))]:
            rows.append(
                dict(
                    trade_date=d,
                    ts_code=code,
                    settle=price,
                    trading_fee=1.5,
                    long_margin_rate=0.1,
                    vol=1000,
                )
            )
    return pd.DataFrame(rows), dates


def test_contract_roll_does_not_create_price_gap_profit_and_charges_both_legs():
    frame, dates = trial_input()
    result = settlement_trial(
        frame,
        [(dates[1], "A"), (dates[2], "B")],
        dates[3],
        capital=10000,
        per_unit=10,
        slippage_ticks=0,
    )
    ledger = result["ledger"]
    assert ledger[0]["lots"] == 10
    assert ledger[1]["lots"] == 4  # quantity sized at prior B settlement, with fee-funded equity
    assert ledger[1]["pnl"] == 100
    assert ledger[1]["traded_lots"] == 14
    assert ledger[1]["fee"] == 21
    assert ledger[-1]["lots"] == 0
    assert ledger[-1]["fee"] == 6
    assert result["total_pnl"] == 140
    assert result["terminal_equity"] == 10000 + 140 - 42


def test_contract_missing_mark_or_margin_fails_closed():
    frame, dates = trial_input()
    frame.loc[frame.trade_date == dates[2], "long_margin_rate"] = 2
    with pytest.raises(ValueError, match="margin"):
        settlement_trial(frame, [(dates[1], "A")], dates[3], capital=10000, per_unit=10)


def test_missing_interior_roll_day_cannot_be_silently_skipped():
    frame, dates = trial_input()
    frame = frame.loc[frame.trade_date != dates[2]]
    with pytest.raises(ValueError, match="endpoints"):
        settlement_trial(frame, [(dates[1], "A"), (dates[2], "B")], dates[3], capital=10000)


def test_macro_capture_rejects_backdated_or_changed_index_metadata(tmp_path):
    import hashlib
    import json
    from market_research.studies.commodity_equity.next_run import verified_capture

    raw = b"month,value\n202610,50.1\n"
    digest = hashlib.sha256(raw).hexdigest()
    receipt = {"dataset": "cn_pmi", "sha256": digest, "retrieved_at": "2026-11-08T01:00:00+00:00"}
    body = json.dumps(receipt).encode()
    receipt_hash = hashlib.sha256(body).hexdigest()
    (tmp_path / "raw.bin").write_bytes(raw)
    (tmp_path / "receipt.json").write_bytes(body)
    (tmp_path / "manifest.seal.json").write_text(
        json.dumps({"files": {"raw.bin": digest, "receipt.json": receipt_hash}})
    )
    row = {
        "path": str(tmp_path),
        "dataset": "cn_pmi",
        "rows": 1,
        "periods": ["202610"],
        "retrieved_at": receipt["retrieved_at"],
        "raw_sha256": digest,
        "receipt_sha256": receipt_hash,
    }
    assert verified_capture({"snapshots": [row]})[0]["rows"] == 1
    for key, changed in [
        ("retrieved_at", "2007-01-01T00:00:00+00:00"),
        ("raw_sha256", "wrong"),
        ("rows", 2),
        ("dataset", "cn_ppi"),
    ]:
        with pytest.raises(ValueError, match="contradicts"):
            verified_capture({"snapshots": [{**row, key: changed}]})


def test_reviewed_next_summary_is_bound_to_current_numerical_source():
    import hashlib
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    result = json.loads((root / 'studies/china_commodity_equity/next-summary-20261108.json').read_text())
    for name, digest in result['code_sha256'].items():
        source = root / 'src/market_research/studies/commodity_equity' / name
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    assert result['prospective_archive']['forward_outcomes'] == 0
    assert result['contract_trial']['execution_established'] is False
