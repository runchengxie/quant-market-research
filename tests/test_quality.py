from datetime import date
import re
from pathlib import Path

import pandas as pd


def test_quality_preserves_missing_observation_as_issue_not_zero():
    from market_research.quality import profile_panel

    frame = pd.DataFrame(
        {
            "market": ["us", "us"],
            "symbol": ["ABC", "ABC"],
            "date": [date(2026, 1, 1), date(2026, 1, 2)],
            "close": [1.0, 1.0],
            "volume": [10.0, None],
            "turnover": [10.0, None],
            "market_cap": [100.0, 100.0],
            "currency": ["USD", "USD"],
            "is_tradable": [True, False],
            "is_suspended": [False, True],
            "source": ["fixture", "fixture"],
        }
    )

    profile = profile_panel(frame)

    assert profile["rows"] == 2
    assert profile["missing_turnover_rows"] == 1
    assert profile["zero_turnover_rows"] == 0


def test_documentation_and_examples_do_not_publish_machine_specific_roots():
    root = Path(__file__).resolve().parents[1]
    local_path = re.compile(r"(?<![A-Za-z0-9])(?:/home/|/Users/|/mnt/|[A-Za-z]:[/\\])")
    documents = [root / "README.md", root / "AGENTS.md"]
    documents.extend((root / "docs").rglob("*.md"))
    documents.extend((root / "studies").rglob("*.md"))
    documents.append(root / "configs/local.example.toml")
    for suffix in ("*.json", "*.yml", "*.yaml"):
        documents.extend((root / "studies").rglob(suffix))
    leaks = [
        f"{path.relative_to(root)}:{number}"
        for path in documents
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if local_path.search(line)
    ]
    assert not leaks, "Documentation contains machine-specific paths:\n" + "\n".join(leaks)
