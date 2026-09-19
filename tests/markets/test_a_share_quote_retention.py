import json
import numpy as np
import pandas as pd
import pytest

from market_research.barra import analyze_size_monotonicity
from market_research.contracts import CANONICAL_COLUMNS, normalize_panel
from market_research.markets.a_share import build_a_share_panel


def source_rows():
    frame = pd.DataFrame([
        {
            "ts_code": symbol, "trade_date": date, "close": 10 + t,
            "adj_close": 10 + t, "vol": 100, "amount": 100.0,
            "total_mv": cap, "is_st": False, "is_suspended": False,
        }
        for symbol, cap in [("000001.SZ", 1.0), ("000002.SZ", 2.0)]
        for t, date in enumerate(["2024-01-01", "2024-01-02", "2024-01-03"])
    ])
    return frame.astype({"is_st": "boolean", "is_suspended": "boolean"})


def write_source(root, frame):
    root.mkdir(exist_ok=True)
    # Partition filenames need not equal the security identifier.
    frame.to_parquet(root / "part-000.parquet", index=False)


@pytest.mark.parametrize("engine", [False, True], ids=["pandas", "duckdb"])
@pytest.mark.parametrize("column, value", [
    ("is_st", True), ("is_suspended", True), ("amount", 0.0), ("total_mv", 0.0),
    ("is_st", None), ("is_suspended", None), ("amount", np.nan),
    ("total_mv", np.inf),
])
def test_holding_marks_survive_ineligibility_without_new_formation(tmp_path, engine, column, value):
    frame = source_rows()
    future_a = frame.ts_code.eq("000001.SZ") & frame.trade_date.ne("2024-01-01")
    frame.loc[future_a, column] = value
    write_source(tmp_path, frame)
    panel, metadata = build_a_share_panel(tmp_path, use_duckdb=engine, retain_ineligible_quotes=True)
    assert len(panel) == 6
    a = panel.loc[panel.symbol.eq("000001.SZ")].reset_index(drop=True)
    assert a["is_tradable"].tolist() == [True, False, False]
    assert a["adj_close"].tolist() == [10, 11, 12]
    if column in {"is_st", "is_suspended"}:
        assert pd.isna(a.loc[1, column]) if value is None else bool(a.loc[1, column])
    assert "holding" in metadata.universe_filter
    rows, _ = analyze_size_monotonicity(panel, quantiles=2)
    first = rows.loc[rows.formation_date.eq("2024-01-01")]
    assert first["observed_return_count"].sum() == 2
    assert first["return_coverage"].eq(1).all()
    assert first["mean_forward_return"].tolist() == pytest.approx([0.1, 0.1])
    assert rows.loc[rows.formation_date.eq("2024-01-02"), "count"].sum() == 1


@pytest.mark.parametrize("retain", [False, True])
def test_engines_agree_and_default_filters_ineligible_rows(tmp_path, retain):
    frame = source_rows()
    frame.loc[[1, 2], "is_st"] = True
    write_source(tmp_path, frame)
    pandas_panel, _ = build_a_share_panel(tmp_path, retain_ineligible_quotes=retain)
    duck_panel, _ = build_a_share_panel(tmp_path, use_duckdb=True, retain_ineligible_quotes=retain)
    pd.testing.assert_frame_equal(
        pandas_panel.drop(columns="source"), duck_panel.drop(columns="source")
    )
    assert len(pandas_panel) == (6 if retain else 4)
    assert set(pandas_panel.symbol) == {"000001.SZ", "000002.SZ"}


@pytest.mark.parametrize("engine", [False, True])
@pytest.mark.parametrize("missing", ["is_st", "is_suspended", "amount", "total_mv"])
def test_absent_eligibility_fields_retain_marks_but_never_enable_formation(tmp_path, engine, missing):
    write_source(tmp_path, source_rows().drop(columns=missing))
    panel, metadata = build_a_share_panel(tmp_path, use_duckdb=engine, retain_ineligible_quotes=True)
    assert len(panel) == 6
    assert metadata.quality_status == "incomplete"
    assert not panel["is_tradable"].any()
    assert panel["adj_close"].tolist() == [10, 11, 12, 10, 11, 12]
    rows, summary = analyze_size_monotonicity(panel, quantiles=2)
    assert rows.empty
    assert summary["status"] == "unavailable"


@pytest.mark.parametrize("engine", [False, True])
def test_retention_honors_as_of_and_never_fills_missing_price(tmp_path, engine):
    frame = source_rows()
    frame["adj_close"] = frame.adj_close.astype(float)
    frame.loc[1, "adj_close"] = np.nan
    frame.loc[1, "is_st"] = True
    write_source(tmp_path, frame)
    panel, _ = build_a_share_panel(
        tmp_path, as_of="2024-01-02", use_duckdb=engine, retain_ineligible_quotes=True
    )
    assert len(panel) == 4
    assert panel.adj_close.isna().sum() == 1
    rows, _ = analyze_size_monotonicity(panel, quantiles=2)
    assert rows["count"].sum() == 2
    assert rows["missing_return_count"].sum() == 1


@pytest.mark.parametrize("engine", [False, True])
def test_symbols_fall_back_to_filename_only_without_ts_code(tmp_path, engine):
    frame = source_rows().loc[lambda x: x.ts_code.eq("000001.SZ")].drop(columns="ts_code")
    frame.to_parquet(tmp_path / "000001.SZ.parquet", index=False)
    panel, _ = build_a_share_panel(tmp_path, use_duckdb=engine)
    assert panel.symbol.unique().tolist() == ["000001.SZ"]


def test_pandas_uses_actual_security_code_even_for_single_file(tmp_path):
    source = tmp_path / "part-000.parquet"
    source_rows().to_parquet(source, index=False)
    panel, _ = build_a_share_panel(source)
    assert set(panel.symbol) == {"000001.SZ", "000002.SZ"}


def test_normalize_preserves_extra_columns_flags_and_attrs(tmp_path):
    # Use one security so the original loader can supply valid canonical data.
    source_rows().iloc[:3].to_parquet(tmp_path / "000001.SZ.parquet", index=False)
    panel, metadata = build_a_share_panel(tmp_path)
    panel["is_st"] = pd.Series([False, True, pd.NA], dtype="boolean")
    panel["formation_audit"] = ["known", "known", "unknown"]
    panel.attrs["retained_quotes"] = True
    normalized, _ = normalize_panel(panel.iloc[::-1], metadata)
    assert list(normalized.columns[:len(CANONICAL_COLUMNS)]) == list(CANONICAL_COLUMNS)
    assert normalized.is_st.iloc[:2].tolist() == [False, True]
    assert pd.isna(normalized.is_st.iloc[2])
    assert normalized.formation_audit.tolist() == ["known", "known", "unknown"]
    assert normalized.attrs == {"retained_quotes": True}


@pytest.mark.parametrize("engine", [False, True])
def test_barra_cli_opts_into_retention_and_reports_observed_return(tmp_path, monkeypatch, engine):
    from market_research import cli

    source = tmp_path / "source"
    frame = source_rows()
    frame.loc[[1, 2], "is_st"] = True
    write_source(source, frame)
    output = tmp_path / "output"
    config = tmp_path / "config.toml"
    config.write_text(
        f'output_root = "{output}"\nuse_duckdb = {str(engine).lower()}\n'
        f'[sources]\na_share_root = "{source}"\n[barra]\nsize_quantiles = 2\n'
    )
    calls = []

    def spy(*args, **kwargs):
        calls.append(kwargs)
        return build_a_share_panel(*args, **kwargs)

    monkeypatch.setattr(cli, "build_a_share_panel", spy)
    assert cli.main(["report", "barra", "--config", str(config)]) == 0
    assert calls == [{"use_duckdb": engine, "retain_ineligible_quotes": True}]
    rows = pd.read_csv(output / "barra_size_quantiles.csv")
    first = rows.loc[rows.formation_date.eq("2024-01-01")]
    assert first["observed_return_count"].sum() == 2
    assert first["mean_forward_return"].tolist() == pytest.approx([0.1, 0.1])
    summary = json.loads((output / "barra_summary.json").read_text())
    assert summary["size_monotonicity"]["observations"] == 1
    calls.clear()
    assert cli.main(["report", "smallcap-turnover", "--config", str(config)]) == 0
    assert calls == [{"use_duckdb": engine}]


@pytest.mark.parametrize("engine", [False, True], ids=["pandas", "duckdb"])
@pytest.mark.parametrize("case, expected", [
    ("complete", "derived"),
    ("known_st_holding_quote", "derived"),
    ("unknown_st", "incomplete"),
    ("unknown_suspension", "incomplete"),
    ("unknown_amount", "incomplete"),
    ("invalid_cap", "incomplete"),
    ("all_st", "incomplete"),
    ("all_zero_amount", "incomplete"),
])
def test_retained_metadata_distinguishes_derived_from_incomplete(tmp_path, engine, case, expected):
    frame = source_rows()
    if case == "known_st_holding_quote":
        frame.loc[1, "is_st"] = True
    elif case == "unknown_st":
        frame.loc[1, "is_st"] = pd.NA
    elif case == "unknown_suspension":
        frame.loc[1, "is_suspended"] = pd.NA
    elif case == "unknown_amount":
        frame.loc[1, "amount"] = np.nan
    elif case == "invalid_cap":
        frame.loc[1, "total_mv"] = np.inf
    elif case == "all_st":
        frame["is_st"] = True
    elif case == "all_zero_amount":
        frame["amount"] = 0.0
    write_source(tmp_path, frame)
    panel, metadata = build_a_share_panel(tmp_path, use_duckdb=engine, retain_ineligible_quotes=True)
    assert len(panel) == 6
    assert metadata.quality_status == expected
    if case in {"all_st", "all_zero_amount"}:
        assert not panel.is_tradable.any()
        assert analyze_size_monotonicity(panel, quantiles=2)[1]["status"] == "unavailable"


@pytest.mark.parametrize("engine", [False, True])
def test_default_loader_keeps_legacy_metadata_status(tmp_path, engine):
    write_source(tmp_path, source_rows())
    _, metadata = build_a_share_panel(tmp_path, use_duckdb=engine)
    assert metadata.quality_status == "verified"
