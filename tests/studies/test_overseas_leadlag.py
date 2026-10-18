import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from market_research.studies.overseas_leadlag.models import purged_train
from market_research.studies.overseas_leadlag.proxy import adjusted_etf, simulate
from market_research.studies.overseas_leadlag.timing import align_external, assumed_available
from market_research.studies.overseas_leadlag.run import run


def test_us_dst_and_gmt_day_are_respected():
    assert assumed_available(pd.Timestamp("2024-07-01"), "spx") == pd.Timestamp("2024-07-01 21:00Z")
    assert assumed_available(pd.Timestamp("2024-01-02"), "spx") == pd.Timestamp("2024-01-02 22:00Z")
    # GMT Monday's full bar is not available at Tuesday 08:45 Shanghai.
    assert assumed_available(pd.Timestamp("2024-01-08"), "fx") == pd.Timestamp("2024-01-09 01:00Z")


def test_raw_run_outputs_cannot_be_written_into_the_repository():
    root = Path(__file__).resolve().parents[2]
    with pytest.raises(ValueError, match="outside"):
        run(root, root, root / "forbidden-generated-output")


def test_fx_unfinished_bar_excluded_and_foreign_holiday_not_reused():
    target = pd.DataFrame({"date": pd.to_datetime(["2024-01-08", "2024-01-09", "2024-01-10"])})
    source = pd.DataFrame({"date": pd.to_datetime(["2024-01-04", "2024-01-05", "2024-01-08"]),
                           "close": [1., 1.1, 1.21]})
    frame, audit = align_external(target, {"fx": (source, "fx", "close")})
    assert frame.fx.iloc[1] == 0  # Same completed Friday bar remains selected on Tuesday.
    assert frame.fx.iloc[2] == pytest.approx(.1)
    assert not (audit.assumed_available_utc > audit.decision_utc).any()
    delayed, _ = align_external(target, {"fx": (source, "fx", "close")}, lag=1)
    assert delayed.fx.iloc[2] == 0


def test_training_label_at_test_open_is_purged():
    frame = pd.DataFrame({"date": pd.to_datetime(["2023-12-28", "2023-12-29"]),
                          "label_end_utc": pd.to_datetime(["2023-12-29 01:30Z", "2024-01-02 01:30Z"])})
    assert len(purged_train(frame, pd.Timestamp("2024-01-02 00:45Z"))) == 1


def test_adjustment_split_does_not_create_a_false_loss():
    dates = pd.to_datetime(["2024-01-01", "2024-01-02"])
    bars = pd.DataFrame({"date": dates, "open": [2., 1.], "close": [2., 1.],
                         "pre_close": [2., 2.], "amount": [100., 100.]})
    factors = pd.DataFrame({"date": dates, "adj_factor": [1., 2.]})
    data = adjusted_etf(bars, factors)
    assert data.adjusted_open.pct_change().iloc[-1] == 0
    assert data.auction_reference.iloc[-1] == 1  # Nominal split is not a limit-down open.
    with pytest.raises(ValueError, match="Missing"):
        adjusted_etf(bars, factors.iloc[:1])


def proxy_frame():
    return pd.DataFrame({"date": pd.date_range("2024-01-02", periods=3),
                         "open": [1., 1., 1.], "pre_close": [1., 1., 1.],
                         "exit_raw_open": [1., 1., 1.], "exit_pre_close": [1., 1., 1.],
                         "adv20_yuan": [1e9] * 3, "y": [.01, .02, -.01]})


def test_consecutive_long_signals_pay_entry_and_terminal_exit_only():
    frame = proxy_frame()
    stats, net = simulate(frame, dict.fromkeys(frame.date, 1.), 5)
    assert stats["one_way_trades"] == 2
    assert net == pytest.approx([.0095, .02, -.0105])
    assert stats["mean_daily_net_bp"] == pytest.approx(np.mean(net) * 10000)


def test_liquidity_and_limit_guards_preserve_blocked_holdings():
    frame = proxy_frame()
    frame.loc[0, "adv20_yuan"] = 1  # No future-day volume used to permit entry.
    stats, _ = simulate(frame, dict.fromkeys(frame.date, 1.), 0)
    assert stats["blocked_changes"] == 1
    assert stats["exposure_fraction"] == pytest.approx(2 / 3)
    frame = proxy_frame()
    frame.loc[1, "open"] = .9
    stats, _ = simulate(frame, {frame.date[0]: 1}, 0)
    assert stats["blocked_changes"] == 1
    assert stats["exposure_fraction"] == pytest.approx(2 / 3)
