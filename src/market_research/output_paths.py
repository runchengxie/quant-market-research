"""Resolve durable research output directories outside the source checkout."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[2]


def resolve_output_root(config: Mapping[str, object] | None = None, *, subdir: str | None = None) -> Path:
    """Return the configured durable output root and reject checkout-local paths.

    ``output_root`` in a study/config has highest precedence, followed by
    ``MARKET_RESEARCH_OUTPUT_ROOT`` and then ``DATA_PLATFORM_ROOT``.  The
    latter keeps each owner in its own subtree instead of mixing reports with
    shared market-data assets.
    """

    values = config or {}
    configured = values.get("output_root")
    raw = str(configured).strip() if configured is not None else ""
    if not raw:
        raw = os.environ.get("MARKET_RESEARCH_OUTPUT_ROOT", "").strip()
    if raw:
        output = Path(raw).expanduser()
    else:
        data_root = os.environ.get("DATA_PLATFORM_ROOT", "").strip()
        if not data_root:
            raise RuntimeError(
                "durable research output requires output_root, "
                "MARKET_RESEARCH_OUTPUT_ROOT, or DATA_PLATFORM_ROOT"
            )
        output = Path(data_root).expanduser() / "reports" / "market-research"
    if not output.is_absolute():
        output = Path.cwd() / output
    output = output.resolve()
    if output == _REPO_ROOT or _REPO_ROOT in output.parents:
        raise ValueError("research output must be outside the code repository")
    if subdir:
        output = output / subdir
    return output
