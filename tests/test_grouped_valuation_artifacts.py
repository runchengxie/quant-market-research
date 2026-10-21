from pathlib import Path

import pandas as pd


def test_empty_terminal_holdings_preserves_readable_schema(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "scripts"))
    from run_grouped_valuation_ledger import AuditSink, HOLDING_SCHEMA

    sink = AuditSink(tmp_path / "empty", 100.0)
    sink.close()
    frame = pd.read_csv(tmp_path / "empty/terminal_holdings.csv")
    assert frame.empty
    assert frame.columns.tolist() == HOLDING_SCHEMA.names
