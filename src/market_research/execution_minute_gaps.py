"""Localize missing sampled minute keys; do not infer a vendor failure cause."""

from __future__ import annotations

from collections import Counter

import pandas as pd


def summarize_minute_gaps(selection: pd.DataFrame, expected_minutes: list[int]) -> dict:
    keys = ["SecuCode", "minute"]
    if selection[keys].isna().any().any() or selection.duplicated(keys).any():
        raise ValueError("null or duplicate selection keys")
    expected = set(expected_minutes)
    if not set(selection.minute.astype(int)).issubset(expected):
        raise ValueError("selection contains out-of-session minutes")
    grouped = {"Shanghai": [], "Shenzhen": []}
    for code, rows in selection.groupby("SecuCode"):
        digits = str(int(code)).zfill(6)
        if not digits.startswith(("0", "3", "6")):
            raise ValueError("only sampled Shanghai/Shenzhen stocks are supported")
        venue = "Shanghai" if digits.startswith("6") else "Shenzhen"
        grouped[venue].append(expected - set(rows.minute.astype(int)))
    venues = []
    for venue, gaps in grouped.items():
        counts = Counter(minute for gap in gaps for minute in gap)
        blocks = []
        for minute, count in sorted(counts.items()):
            if (
                blocks
                and blocks[-1]["last"] == minute - 1
                and blocks[-1]["missing_per_minute"] == count
            ):
                blocks[-1]["last"] = minute
                blocks[-1]["minutes"] += 1
            else:
                blocks.append(dict(first=minute, last=minute, minutes=1, missing_per_minute=count))

        def clock(minute):
            return f"{minute // 60:02d}:{minute % 60:02d}"

        venues.append(
            dict(
                venue=venue,
                observed_stocks=len(gaps),
                affected_stocks=sum(bool(gap) for gap in gaps),
                expected_minutes=len(expected) * len(gaps),
                observed_minutes=len(expected) * len(gaps) - sum(counts.values()),
                missing_minutes=sum(counts.values()),
                blocks=[
                    dict(
                        start=clock(b["first"]),
                        end=clock(b["last"]),
                        minutes=b["minutes"],
                        missing_per_minute=b["missing_per_minute"],
                    )
                    for b in blocks
                ],
            )
        )
    return dict(
        observed_stocks=selection.SecuCode.nunique(),
        sampled_minutes=len(selection),
        expected_minutes=len(expected) * selection.SecuCode.nunique(),
        missing_minutes=sum(v["missing_minutes"] for v in venues),
        venues=venues,
        full_universe_coverage_proven=False,
        missing_cause_identified=False,
    )
