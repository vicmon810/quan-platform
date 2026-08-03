import pandas as pd

from src import reporting
import pytest

def test_build_strategy_comparison():
    results = [
        {
            "ticker": "SPY",
            "strategy": "BuyAndHold",
            "final_value": 150_000.0,
            "cumulative_return": 0.50,
            "cagr": 0.12,
            "max_drawdown": 0.30,
            "daily_sharpe": 0.80,
            "calmar": 0.40,
            "market_exposure": 0.95,
        },
        {
            "ticker": "SPY",
            "strategy": "TimeSeriesMomentum",
            "final_value": 135_000.0,
            "cumulative_return": 0.35,
            "cagr": 0.09,
            "max_drawdown": 0.15,
            "daily_sharpe": 0.95,
            "calmar": 0.60,
            "market_exposure": 0.55,
        },
    ]

    comparison = reporting.build_strategy_comparison(
        results
    )

    assert isinstance(comparison, pd.DataFrame)

    assert comparison.columns.tolist() == [
        "ticker",
        "strategy",
        "final_value",
        "cumulative_return",
        "cagr",
        "max_drawdown",
        "daily_sharpe",
        "calmar",
        "market_exposure",
    ]

    assert len(comparison) == 2

    assert comparison.iloc[0]["strategy"] == (
        "BuyAndHold"
    )

    assert comparison.iloc[1]["market_exposure"] == (
        0.55
    )



def test_build_strategy_comparsion_rejection_empty_results():
    with pytest.raises(
        ValueError,
        match="at least one strategy result"
    ):
        reporting.build_strategy_comparison([])


def test_build_strategy_comparison_rejects_empty_results():
    results = [
        {
            "ticker": "SPY",
            "strategy":"BuyAndHold",
            "final_value":150_000.0
        }
    ]

    with pytest.raises(ValueError,match="missing required comparison fields"):
        reporting.build_strategy_comparison(results=results)


def test_add_metric_ranks():
    comparison = pd.DataFrame(
        [
            {
                "ticker": "SPY",
                "strategy": "BuyAndHold",
                "final_value": 150_000.0,
                "cumulative_return": 0.50,
                "cagr": 0.12,
                "max_drawdown": 0.30,
                "daily_sharpe": 0.80,
                "calmar": 0.40,
                "market_exposure": 0.95,
            },
            {
                "ticker": "SPY",
                "strategy": "TimeSeriesMomentum",
                "final_value": 135_000.0,
                "cumulative_return": 0.35,
                "cagr": 0.09,
                "max_drawdown": 0.15,
                "daily_sharpe": 0.95,
                "calmar": 0.60,
                "market_exposure": 0.55,
            },
        ]
    )

    ranked = reporting.add_metric_ranks(comparison)

    buy_and_hold = ranked.loc[
        ranked["strategy"] == "BuyAndHold"
    ].iloc[0]

    momentum = ranked.loc[
        ranked["strategy"] == "TimeSeriesMomentum"
    ].iloc[0]
    assert buy_and_hold["cagr_rank"] == 1
    assert momentum["cagr_rank"] == 2

    assert momentum["max_drawdown_rank"] == 1
    assert buy_and_hold["max_drawdown_rank"] == 2

    assert momentum["daily_sharpe_rank"] == 1
    assert momentum["calmar_rank"] == 1
    

def test_add_metric_ranks_does_not_modify_input():
    comparison = pd.DataFrame(
        [
            {
                "cagr": 0.10,
                "max_drawdown": 0.20,
                "daily_sharpe": 0.80,
                "calmar": 0.50,
            }
        ]
    )

    original_columns = comparison.columns.tolist()

    reporting.add_metric_ranks(comparison=comparison)
    assert comparison.columns.tolist() == original_columns


def test_build_strategy_comparison_includes_drawdown_duration_metrics():
    results = [
        {
            "ticker": "SPY",
            "strategy": "BuyAndHold",
            "final_value": 150_000.0,
            "cumulative_return": 0.50,
            "cagr": 0.12,
            "max_drawdown": 0.30,
            "daily_sharpe": 0.80,
            "calmar": 0.40,
            "market_exposure": 0.95,
            "max_drawdown_duration_days": 180,
            "average_drawdown_duration_days": 45.5,
        }
    ]

    comparison = reporting.build_strategy_comparison(results=results)

    assert (comparison.iloc[0]["max_drawdown_duration_days"] == 180)
    assert comparison.iloc[0]["average_drawdown_duration_days"] == pytest.approx(45.5)

    assert comparison.columns.tolist() == [
        "ticker",
        "strategy",
        "final_value",
        "cumulative_return",
        "cagr",
        "max_drawdown",
        "daily_sharpe",
        "calmar",
        "market_exposure",
        "max_drawdown_duration_days",
        "average_drawdown_duration_days",
    ]