from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PUBLISHED_PAIRS = (
    ("index.md", "index.zh-CN.md"),
    ("research-closeout-status.md", "research-closeout-status.zh-CN.md"),
    ("research/factors/pb-roe.md", "research/factors/pb-roe.zh-CN.md"),
    ("research/factors/low-turnover.md", "research/factors/low-turnover.zh-CN.md"),
    ("research/factors/microcap.md", "research/factors/microcap.zh-CN.md"),
    (
        "research/experiments/microcap-execution-diagnostic-20260928.md",
        "research/experiments/microcap-execution-diagnostic-20260928.zh-CN.md",
    ),
    (
        "research/factors/smallcap-turnover-history.md",
        "research/factors/smallcap-turnover-history.zh-CN.md",
    ),
    (
        "research/factors/barra-factor-dictionary.md",
        "research/factors/barra-factor-dictionary.zh-CN.md",
    ),
    (
        "research/factors/barra-source-inventory.md",
        "research/factors/barra-source-inventory.zh-CN.md",
    ),
)


def _navigation_paths(node: Any) -> set[str]:
    if isinstance(node, dict):
        return set().union(*(_navigation_paths(value) for value in node.values()))
    if isinstance(node, list):
        return set().union(*(_navigation_paths(value) for value in node))
    if isinstance(node, str):
        return {node}
    return set()


def test_published_pages_have_reciprocal_language_links_and_shareable_routes() -> None:
    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((root / "mkdocs.yml").read_text(encoding="utf-8"))

    assert config["theme"]["locale"] == "en"
    assert config["use_directory_urls"] is True
    navigation = _navigation_paths(config["nav"])

    for english_name, chinese_name in PUBLISHED_PAIRS:
        english = root / "docs" / english_name
        chinese = root / "docs" / chinese_name
        assert english.as_posix().removeprefix(f"{root.as_posix()}/docs/") in navigation
        assert chinese.is_file()

        english_text = english.read_text(encoding="utf-8")
        chinese_text = chinese.read_text(encoding="utf-8")
        assert f"[中文页面]({chinese.name})" in english_text
        assert f"[English page]({english.name})" in chinese_text

    assert not any(path.endswith(".zh-CN.md") for path in navigation)
