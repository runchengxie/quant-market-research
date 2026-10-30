"""Compatibility imports for the historical module name.

New code should import :mod:`market_research.style_factors`.
"""
from .style_factors import (
    analyze_size_monotonicity,
    load_style_factor_summary as load_barra_summary,
    summarize_style_factor_file as summarize_barra_factor_file,
)

__all__ = ["analyze_size_monotonicity", "load_barra_summary", "summarize_barra_factor_file"]
