"""Explicit public projection of reviewed historical aggregate tables.

This does not load market data or run a portfolio. Unknown historical execution
parameters remain unknown; only the three already-public candidate families pass.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

CANDIDATES = ("small_cap", "low_turnover", "composite")
EXCLUSIONS = (0.0, 0.1, 0.2, 0.3)
WEIGHTS = ("equal", "value")
BUFFERS = ("no_buffer", "buffered")


def compound_periods(rows: list[dict]) -> dict:
    """Compound percentage-valued retained periods; annualize by observations."""
    if not rows or len({row["year"] for row in rows}) != len(rows):
        raise ValueError("periods must be nonempty with distinct years")
    observations = sum(int(row["observations"]) for row in rows)
    if observations <= 0:
        raise ValueError("positive observations required")
    values = [float(row["period_return"]) for row in rows]
    if any(not math.isfinite(value) or value <= -100 for value in values):
        raise ValueError("period returns must be finite and above -100 percent")
    wealth = math.prod(1 + value / 100 for value in values)
    return {"observations": observations, "cumulative_return": (wealth - 1) * 100,
            "net_annual_return": (wealth ** (252 / observations) - 1) * 100}


def _read(path: Path, fields: tuple[str, ...], labels: set[str]) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(fields).issubset(reader.fieldnames or []):
            raise ValueError(f"missing columns in {path.name}")
        result = []
        for row in reader:
            # No private factor rows or additional candidate families enter the projection.
            if row.get("candidate", row.get("name")) not in CANDIDATES:
                continue
            if "source_type" in row and row["source_type"] != "candidate":
                continue
            if "return_type" in row and row["return_type"] != "net":
                continue
            if path.name in {"microcap_yearly.csv", "microcap_regimes.csv"} and row["buffer_setting"] != "buffered":
                continue
            parsed = {key: row[key] if key in labels else float(row[key]) for key in fields}
            if any(not math.isfinite(value) for value in parsed.values() if isinstance(value, float)):
                raise ValueError(f"nonfinite aggregate in {path.name}")
            result.append(parsed)
    return result


def _grid(rows: list[dict], fields: tuple[str, ...], axes: tuple[tuple, ...]) -> None:
    keys = [tuple(row[field] for field in fields) for row in rows]
    if len(set(keys)) != len(keys) or set(keys) != set(itertools.product(*axes)):
        raise ValueError(f"incomplete or duplicate grid: {fields}")


def project_retained_bundle(source: Path) -> dict:
    """Validate matched support and export only reviewed aggregate fields."""
    summary = json.loads((source / "microcap_summary.json").read_text())
    if summary["alpha_commit"] != "unknown" or summary["portfolio_commit"] != "unknown":
        raise ValueError("review source-code status before changing the publication contract")
    common = ("candidate", "exclusion_percentile", "weighting", "buffer_setting")
    labels = {"candidate", "weighting", "buffer_setting", "name", "regime"}
    buffer_fields = common + ("gross_annual_return", "net_annual_return", "annualized_turnover", "cost_drag", "net_sharpe", "net_max_drawdown")
    buffer = _read(source / "microcap_buffer_matrix.csv", buffer_fields, labels)
    _grid(buffer, common, (CANDIDATES, EXCLUSIONS, WEIGHTS, BUFFERS))
    for row in buffer:
        if not math.isclose(row["gross_annual_return"] - row["net_annual_return"], row["cost_drag"], abs_tol=1e-9):
            raise ValueError("cost drag does not reconcile in percentage points")
    period_fields = ("name", "exclusion_percentile", "weighting", "buffer_setting", "year", "observations", "period_return", "annual_return", "sharpe", "max_drawdown", "average_turnover")
    yearly = _read(source / "microcap_yearly.csv", period_fields, labels)
    _grid(yearly, ("name", "exclusion_percentile", "weighting", "year"), (CANDIDATES, EXCLUSIONS, WEIGHTS, tuple(range(2015, 2027))))
    era_summary = []
    expected_support = None
    for candidate, exclusion, weighting in itertools.product(CANDIDATES, EXCLUSIONS, WEIGHTS):
        selected = [r for r in yearly if (r["name"], r["exclusion_percentile"], r["weighting"]) == (candidate, exclusion, weighting)]
        support = [(r["year"], r["observations"]) for r in sorted(selected, key=lambda r: r["year"])]
        if expected_support is None:
            expected_support = support
        if support != expected_support:
            raise ValueError("yearly support differs between compared candidate arms")
        total = compound_periods(selected)
        original = next(r for r in buffer if (r["candidate"], r["exclusion_percentile"], r["weighting"], r["buffer_setting"]) == (candidate, exclusion, weighting, "buffered"))
        if total["observations"] != 2778 or not math.isclose(total["net_annual_return"], original["net_annual_return"], abs_tol=1e-8):
            raise ValueError("full-history annualization does not reconcile")
        for era, period in [("development", [r for r in selected if r["year"] <= 2023]), ("later_descriptive", [r for r in selected if r["year"] >= 2024])]:
            result = compound_periods(period)
            if result["observations"] != (2154 if era == "development" else 624):
                raise ValueError("era support changed")
            era_summary.append({"candidate": candidate, "exclusion_percentile": exclusion, "weighting": weighting, "buffer_setting": "buffered", "era": era, **result})
    regime_fields = tuple("regime" if f == "year" else f for f in period_fields)
    regimes = _read(source / "microcap_regimes.csv", regime_fields, labels)
    _grid(regimes, ("name", "exclusion_percentile", "weighting", "regime"), (CANDIDATES, EXCLUSIONS, WEIGHTS, ("pre_registration_pilot", "registration_pilot", "full_registration")))
    capacity_fields = common + ("capital", "net_annual_return", "net_sharpe", "max_drawdown", "fill_ratio", "avg_cash_weight", "cumulative_turnover")
    capacity = _read(source / "microcap_capacity_matrix.csv", capacity_fields, labels)
    _grid(capacity, ("candidate", "exclusion_percentile", "weighting", "capital"), (("small_cap", "composite"), (0.0, 0.3), WEIGHTS, (10_000_000.0, 100_000_000.0, 500_000_000.0)))
    for row in capacity:
        if row["buffer_setting"] != "buffered" or not 0 <= row["fill_ratio"] <= 1 or not 0 <= row["avg_cash_weight"] <= 1:
            raise ValueError("capacity ratio or buffer changed")
    files = ("microcap_summary.json", "microcap_buffer_matrix.csv", "microcap_yearly.csv", "microcap_regimes.csv", "microcap_capacity_matrix.csv")
    return {"schema_version": "microcap_exclusion_review.v1", "reviewed_on": "2026-10-16",
            "evidence_id": "microcap-exclusion-retained-20260910", "status": "retained_outputs_reviewed_no_backtest_rerun",
            "historical_code_revision": None, "historical_fee_bps": None, "protocol_default_fee_bps": 10,
            "input_scope": {"start": summary["data_start"], "end": summary["data_end"], "formation_start": "2015-02-27", "formation_end": "2026-07-31", "formations": 138, "return_sessions": 2778, "development_sessions": 2154, "later_sessions": 624, "first_daily_return_date": None, "capacity_effective_sessions": None},
            "source_artifacts": [{"name": name, "sha256": hashlib.sha256((source / name).read_bytes()).hexdigest()} for name in files],
            "units": {"returns": "percent", "drawdown": "percent", "cost_drag": "percentage_points", "turnover": "multiple", "fill_cash": "fraction", "capital": "CNY", "exclusion": "fraction_of_reference_stock_count"},
            "buffer_matrix": buffer, "yearly": yearly, "era_summary": era_summary, "regime_summary": regimes, "capacity_matrix": capacity}
