from market_research import barra, style_factors
from market_research.cli import _build_parser


def test_legacy_imports_are_exact_aliases():
    assert barra.load_barra_summary is style_factors.load_style_factor_summary
    assert barra.summarize_barra_factor_file is style_factors.summarize_style_factor_file
    assert barra.analyze_size_monotonicity is style_factors.analyze_size_monotonicity


def test_style_command_aliases():
    parser = _build_parser()
    for command in ("style-factors", "barra", "style-risk-inputs", "barra-risk-inputs"):
        args = parser.parse_args(["report", command, "--config", "example.toml"])
        assert args.report_command == command


def test_style_study_command_remains_available():
    args = _build_parser().parse_args(["report", "style-factors", "--study", "study.yml"])
    assert args.study == "study.yml"
    assert args.config is None
