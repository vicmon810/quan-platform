import pandas as pd

from src import reporting


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