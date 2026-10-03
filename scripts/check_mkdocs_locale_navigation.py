from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path


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
    checks = (
        ("index.html", False),
        ("research/factors/pb-roe/index.html", False),
        ("index.zh-CN/index.html", True),
        ("research/factors/pb-roe.zh-CN/index.html", True),
    )
    errors = []
    for relative, chinese in checks:
        path = args.site_dir / relative
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
    print("Verified English and Chinese MkDocs navigation on overview and factor pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
