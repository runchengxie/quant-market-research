from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
DICTIONARY = ROOT / "studies/style_factors_18y/factor-descriptors.yml"


def test_dictionary_has_expected_families_and_unique_factor_ids() -> None:
    payload = yaml.safe_load(DICTIONARY.read_text(encoding="utf-8"))
    families = payload["families"]
    assert set(families) >= {
        "size",
        "value",
        "momentum",
        "volatility",
        "liquidity",
        "quality",
    }

    factor_ids = [
        factor["id"]
        for family in families.values()
        for factor in family.get("factors", [])
    ]
    assert len(factor_ids) == len(set(factor_ids))


def test_quality_composite_lists_its_components_once() -> None:
    payload = yaml.safe_load(DICTIONARY.read_text(encoding="utf-8"))
    quality = payload["families"]["quality"]
    composite = next(item for item in quality["composites"] if item["id"] == "quality")
    assert composite["weighting"] == "equal"
    assert composite["components"] == [
        "profitability",
        "leverage",
        "earnings_quality",
        "earnings_variability",
    ]


def test_dictionary_documents_known_method_boundaries() -> None:
    text = DICTIONARY.read_text(encoding="utf-8")
    assert "不应直接称为标准中期 Barra 动量" in text
    assert "尚未剥离市场和行业波动" in text
    assert "归因回归时应在复合质量和其子因子之间二选一" in text
