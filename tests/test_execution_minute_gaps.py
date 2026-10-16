import pandas as pd
import pytest

from market_research.execution_minute_gaps import summarize_minute_gaps


def test_shared_gap_is_localized_by_venue_without_exposing_security_ids():
    rows = []
    for code in [600001, 1, 2]:
        for minute in [570, 571, 572]:
            if code != 600001 and minute == 571:
                continue
            rows.append({"SecuCode": code, "minute": minute})
    result = summarize_minute_gaps(pd.DataFrame(rows), [570, 571, 572])
    assert result["missing_minutes"] == 2
    sh, sz = result["venues"]
    assert sh["venue"] == "Shanghai" and sh["missing_minutes"] == 0
    assert sz["venue"] == "Shenzhen" and sz["affected_stocks"] == 2
    assert sz["blocks"] == [
        {"start": "09:31", "end": "09:31", "minutes": 1, "missing_per_minute": 2}
    ]
    assert "600001" not in str(result)


def test_duplicate_selection_keys_cannot_be_counted_as_coverage():
    rows = pd.DataFrame({"SecuCode": [1, 1], "minute": [570, 570]})
    with pytest.raises(ValueError, match="duplicate"):
        summarize_minute_gaps(rows, [570])
