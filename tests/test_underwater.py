import pandas as pd
import pytest


def test_underwater_episodes_keep_recovery_and_right_censored_durations_separate():
    from market_research.underwater import build_underwater_episodes

    nav = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=7, freq="B"),
            "nav": [1.0, 0.9, 1.0, 0.8, 0.8, 1.1, 1.05],
        }
    )

    episodes = build_underwater_episodes(nav)

    assert episodes[
        [
            "peak_date",
            "underwater_start_date",
            "trough_date",
            "recovery_date",
            "underwater_trading_sessions",
            "peak_to_recovery_trading_sessions",
            "right_censored",
        ]
    ].to_dict("records") == [
        {
            "peak_date": pd.Timestamp("2020-01-01"),
            "underwater_start_date": pd.Timestamp("2020-01-02"),
            "trough_date": pd.Timestamp("2020-01-02"),
            "recovery_date": pd.Timestamp("2020-01-03"),
            "underwater_trading_sessions": 1,
            "peak_to_recovery_trading_sessions": 2,
            "right_censored": False,
        },
        {
            "peak_date": pd.Timestamp("2020-01-03"),
            "underwater_start_date": pd.Timestamp("2020-01-06"),
            "trough_date": pd.Timestamp("2020-01-06"),
            "recovery_date": pd.Timestamp("2020-01-08"),
            "underwater_trading_sessions": 2,
            "peak_to_recovery_trading_sessions": 3,
            "right_censored": False,
        },
        {
            "peak_date": pd.Timestamp("2020-01-08"),
            "underwater_start_date": pd.Timestamp("2020-01-09"),
            "trough_date": pd.Timestamp("2020-01-09"),
            "recovery_date": pd.NaT,
            "underwater_trading_sessions": 1,
            "peak_to_recovery_trading_sessions": None,
            "right_censored": True,
        },
    ]
    assert episodes.loc[1, "max_drawdown"] == pytest.approx(-0.2)


def test_underwater_summary_uses_kaplan_meier_for_right_censored_tail():
    from market_research.underwater import build_underwater_episodes, summarize_underwater

    nav = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=5, freq="B"),
            "nav": [1.0, 0.5, 1.0, 0.75, 0.8],
        }
    )

    summary = summarize_underwater(build_underwater_episodes(nav), thresholds=(1, 2))

    assert summary["completed_episode_count"] == 1
    assert summary["right_censored_episode_count"] == 1
    assert summary["longest_completed_underwater_trading_sessions"] == 1
    assert summary["longest_observed_underwater_trading_sessions"] == 2
    assert summary["survival_probability_beyond_sessions"] == {"1": 0.5, "2": 0.5}


def test_underwater_summary_reports_empty_series_and_rejects_ambiguous_nav():
    from market_research.underwater import build_underwater_episodes, summarize_underwater

    no_drawdown = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "nav": [1.0, 1.1, 1.1]})
    summary = summarize_underwater(build_underwater_episodes(no_drawdown))

    assert summary["episode_count"] == 0
    assert summary["max_drawdown"] == 0.0
    with pytest.raises(ValueError, match="unique dates"):
        build_underwater_episodes(pd.DataFrame({"date": ["2020-01-01", "2020-01-01"], "nav": [1.0, 0.9]}))


def test_zero_nav_is_valid_after_an_explicit_total_loss():
    from market_research.underwater import build_underwater_episodes

    nav = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=3), "nav": [1.0, 0.0, 0.0]})
    episodes = build_underwater_episodes(nav)
    assert episodes.loc[0, "max_drawdown"] == pytest.approx(-1.0)
    assert bool(episodes.loc[0, "right_censored"])
