from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path

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


def _rendered_path(site_dir: Path, source: str) -> Path:
    if source == "index.md":
        return site_dir / "index.html"
    return site_dir / Path(source).with_suffix("") / "index.html"


def _navigation_checks(site_dir: Path) -> tuple[tuple[Path, bool], ...]:
    return tuple(
        [(_rendered_path(site_dir, english), False) for english, _ in PUBLISHED_PAIRS]
        + [(_rendered_path(site_dir, chinese), True) for _, chinese in PUBLISHED_PAIRS]
    )


class PrimaryNavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.started = False
        self.finished = False
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "ul" and {"nav", "navbar-nav"}.issubset(
            set((attributes.get("class") or "").split())
        ):
            if not self.started and not self.finished:
                self.started = True
                self.depth = 1
                return
            if self.started and not self.finished:
                self.depth += 1
        elif self.started and not self.finished:
            if tag == "ul":
                self.depth += 1
            elif tag == "a" and attributes.get("href"):
                self.links.append(attributes["href"] or "")

    def handle_endtag(self, tag: str) -> None:
        if self.started and not self.finished and tag == "ul":
            self.depth -= 1
            if self.depth == 0:
                self.finished = True


def _nav_links(path: Path) -> list[str]:
    parser = PrimaryNavigationParser()
    parser.feed(path.read_text(encoding="utf-8"))
    if not parser.started or not parser.finished:
        raise ValueError(f"Could not find the primary navigation in {path}")
    return parser.links


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", type=Path, default=Path(".build/mkdocs-reference"))
    args = parser.parse_args()
    errors = []
    for path, chinese in _navigation_checks(args.site_dir):
        relative = path.relative_to(args.site_dir).as_posix()
        if not path.is_file():
            errors.append(f"Missing built page: {path}")
            continue
        try:
            links = _nav_links(path)
        except ValueError as error:
            errors.append(str(error))
            continue
        expected_language = "zh-CN" if chinese else "en"
        if f'<html lang="{expected_language}"' not in path.read_text(encoding="utf-8"):
            errors.append(f"{relative}: HTML language metadata is not {expected_language}")
        wrong_locale = [
            link for link in links if (".zh-CN/" in link) != chinese and link not in {"./", "#"}
        ]
        if wrong_locale:
            errors.append(
                f"{relative}: primary navigation contains other-locale links: {wrong_locale}"
            )
    if errors:
        raise SystemExit("\n".join(errors))
    print("Verified English and Chinese MkDocs navigation across all published routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
