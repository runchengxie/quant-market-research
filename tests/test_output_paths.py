from pathlib import Path

import pytest

from market_research.output_paths import resolve_output_root


def test_data_platform_root_provides_owner_specific_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATA_PLATFORM_ROOT", str(tmp_path / "data"))
    monkeypatch.delenv("MARKET_RESEARCH_OUTPUT_ROOT", raising=False)

    assert resolve_output_root() == (tmp_path / "data" / "reports" / "market-research").resolve()


def test_explicit_output_root_overrides_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATA_PLATFORM_ROOT", str(tmp_path / "data"))
    explicit = tmp_path / "results"

    assert resolve_output_root({"output_root": str(explicit)}) == explicit.resolve()


def test_missing_root_fails_closed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DATA_PLATFORM_ROOT", raising=False)
    monkeypatch.delenv("MARKET_RESEARCH_OUTPUT_ROOT", raising=False)

    with pytest.raises(RuntimeError, match="durable research output requires"):
        resolve_output_root()


def test_checkout_output_is_rejected():
    with pytest.raises(ValueError, match="outside the code repository"):
        resolve_output_root({"output_root": "outputs"})
