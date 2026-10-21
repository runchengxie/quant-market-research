import importlib
import json
from pathlib import Path

import pandas as pd
import pytest


def prepared(tmp_path, monkeypatch, *, bad_price=False, bad_side=False):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "scripts"))
    module = importlib.import_module("audit_grouped_valuation_fills")
    run = tmp_path / "run"
    (run / "basket").mkdir(parents=True)
    prices = tmp_path / "daily_clean_fixture/data/X.parquet"
    prices.parent.mkdir(parents=True)
    pd.DataFrame(
        [
            dict(
                ts_code="X",
                trade_date="20230103",
                adj_close=10.0,
                high=10.0,
                low=10.0,
                up_limit=11.0,
                down_limit=9.0,
                amount=100.0,
                is_suspended=False,
                is_limit_up=False,
                is_limit_down=False,
            )
        ]
    ).to_parquet(prices)
    members = tmp_path / "private_factor_members.parquet"
    pd.DataFrame([dict(ts_code="X", delist_date="20300101")]).to_parquet(members)
    order = dict(
        symbol="X",
        date="20230103",
        price=None if bad_price else 10.0,
        units=1.0,
        notional=10.0,
        fee=0.0,
        side="hold" if bad_side else "buy",
        status="filled",
    )
    orders = run / "basket/orders.parquet"
    pd.DataFrame([order]).to_parquet(orders)
    summary = run / "summary.json"
    summary.write_text(
        json.dumps(
            {
                "portfolios": [
                    dict(
                        portfolio="basket",
                        entry_date="20230103",
                        last_date="20230103",
                        scenario="touch10",
                    )
                ]
            }
        )
    )
    (run / "receipt.json").write_text(
        json.dumps(
            {
                "inputs": {
                    str(prices): module.digest(prices),
                    str(members): module.digest(members),
                },
                "outputs": {str(p.relative_to(run)): module.digest(p) for p in [orders, summary]},
            }
        )
    )
    monkeypatch.setattr(
        "sys.argv", ["audit", "--run", str(run), "--output", str(tmp_path / "audit")]
    )
    return module, orders


def test_fill_audit_accepts_valid_daily_fill(tmp_path, monkeypatch):
    module, _ = prepared(tmp_path, monkeypatch)
    module.main()
    receipt = json.loads((tmp_path / "audit/receipt.json").read_text())
    assert receipt["status"] == "passed"
    assert receipt["portfolios"][0]["filled_orders"] == 1


@pytest.mark.parametrize("bad", ["price", "side"])
def test_fill_audit_rejects_invalid_fields_even_with_matching_hashes(tmp_path, monkeypatch, bad):
    module, _ = prepared(tmp_path, monkeypatch, bad_price=bad == "price", bad_side=bad == "side")
    with pytest.raises(AssertionError, match="ineligible hypothetical fills"):
        module.main()


def test_fill_audit_rejects_modified_orders_before_checking_fills(tmp_path, monkeypatch):
    module, orders = prepared(tmp_path, monkeypatch)
    frame = pd.read_parquet(orders)
    frame["price"] = 9.0
    frame.to_parquet(orders)
    with pytest.raises(ValueError, match="persisted artifact hash mismatch"):
        module.main()
