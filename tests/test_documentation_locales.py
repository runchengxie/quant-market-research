from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
from typing import Any

import yaml

_CHECKER_PATH = Path(__file__).resolve().parents[1] / "scripts/check_mkdocs_locale_navigation.py"
_CHECKER_SPEC = spec_from_file_location("check_mkdocs_locale_navigation", _CHECKER_PATH)
assert _CHECKER_SPEC is not None and _CHECKER_SPEC.loader is not None
_CHECKER = module_from_spec(_CHECKER_SPEC)
_CHECKER_SPEC.loader.exec_module(_CHECKER)
PUBLISHED_PAIRS = _CHECKER.PUBLISHED_PAIRS
check_built_navigation = _CHECKER.main


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
    english_nav, chinese_nav = config["nav"][:-1], config["nav"][-1]["简体中文"]
    navigation = _navigation_paths(english_nav)
    chinese_navigation = _navigation_paths(chinese_nav)

    for english_name, chinese_name in PUBLISHED_PAIRS:
        english = root / "docs" / english_name
        chinese = root / "docs" / chinese_name
        assert english.as_posix().removeprefix(f"{root.as_posix()}/docs/") in navigation
        assert chinese.is_file()
        assert chinese_name in chinese_navigation

        english_text = english.read_text(encoding="utf-8")
        chinese_text = chinese.read_text(encoding="utf-8")
        assert re.search(rf"\[[^\]]+\]\({re.escape(chinese.name)}\)", english_text)
        assert f"[English page]({english.name})" in chinese_text

    assert not any(path.endswith(".zh-CN.md") for path in navigation)
    assert all(path.endswith(".zh-CN.md") for path in chinese_navigation)


def test_chinese_overview_keeps_factor_links_on_chinese_pages() -> None:
    root = Path(__file__).resolve().parents[1]
    overview = (root / "docs" / "index.zh-CN.md").read_text(encoding="utf-8")
    factor_section = overview.split("## 因子研究", 1)[1].split("\n## ", 1)[0]
    destinations = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", factor_section)

    assert len(destinations) == 7
    assert all(destination.endswith(".zh-CN.md") for destination in destinations)
    assert all((root / "docs" / destination).is_file() for destination in destinations)


def test_built_navigation_checker_covers_every_published_locale_route(
    tmp_path: Path, monkeypatch: Any
) -> None:
    site_dir = tmp_path / "site"
    expected_pages: list[tuple[Path, bool]] = []
    for english_source, chinese_source in PUBLISHED_PAIRS:
        for source, chinese in ((english_source, False), (chinese_source, True)):
            route = Path(source).with_suffix("")
            if source == "index.md":
                rendered = site_dir / "index.html"
            else:
                rendered = site_dir / route / "index.html"
            rendered.parent.mkdir(parents=True, exist_ok=True)
            language = "zh-CN" if chinese else "en"
            localized_link = "index.zh-CN/" if chinese else "index/"
            rendered.write_text(
                f'<html lang="{language}"><ul class="nav navbar-nav">'
                f'<li><a href="{localized_link}">Home</a></li></ul></html>',
                encoding="utf-8",
            )
            expected_pages.append((rendered, chinese))

    assert len(expected_pages) == len(PUBLISHED_PAIRS) * 2
    monkeypatch.setattr("sys.argv", ["check_mkdocs_locale_navigation", "--site-dir", str(site_dir)])
    assert check_built_navigation() == 0

    missing_path, _ = expected_pages[-1]
    missing_path.unlink()
    try:
        check_built_navigation()
    except SystemExit as error:
        assert str(missing_path) in str(error)
    else:
        raise AssertionError("The checker accepted a missing locale route")
