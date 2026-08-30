import pandas as pd
import sys
from src.helper import reporting
import pytest
RESULTS = [
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
            "average_drawdown_duration_days": 45.0, 
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
            "max_drawdown_duration_days": 180,
            "average_drawdown_duration_days": 45.0, 
        },
    ]


def test_build_strategy_comparison():
    
    comparison = reporting.build_strategy_comparison(
        RESULTS
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
        "max_drawdown_duration_days",
        "average_drawdown_duration_days"
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
    comparison = reporting.build_strategy_comparison(RESULTS) 

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
                "max_drawdown_duration_days":1,
                "average_drawdown_duration_days":12
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


def test_add_metric_ranks_includes_drawdown_duration_ranks():
    comparison = pd.DataFrame(
        [
            {
                "strategy": "BuyAndHold",
                "cagr": 0.12,
                "max_drawdown": 0.30,
                "daily_sharpe": 0.80,
                "calmar": 0.40,
                "max_drawdown_duration_days": 180,
                "average_drawdown_duration_days": 45.0,
            },
            {
                "strategy": "TimeSeriesMomentum",
                "cagr": 0.10,
                "max_drawdown": 0.15,
                "daily_sharpe": 1.00,
                "calmar": 0.65,
                "max_drawdown_duration_days": 90,
                "average_drawdown_duration_days": 20.0,
            },
            {
                "strategy": "MovingAverageCross",
                "cagr": 0.08,
                "max_drawdown": 0.20,
                "daily_sharpe": 0.75,
                "calmar": 0.45,
                "max_drawdown_duration_days": 120,
                "average_drawdown_duration_days": 30.0,
            },
        ]
    )

    ranked = reporting.add_metric_ranks(
        comparison=comparison
    )

    buy_and_hold = ranked.iloc[ranked["strategy"] == "BuyAndHold"].iloc[0]
    momentum = ranked.iloc[ranked["strategy"] == "TimeSeriesMomentum"].iloc[0]
    moving_average = ranked.loc[
        ranked["strategy"] == "MovingAverageCross"
    ].iloc[0]

    assert momentum[
        "max_drawdown_duration_days_rank"
    ] == 1

    assert moving_average[
        "max_drawdown_duration_days_rank"
    ] == 2

    assert buy_and_hold[
        "max_drawdown_duration_days_rank"
    ] == 3

    assert momentum[
        "average_drawdown_duration_days_rank"
    ] == 1

    assert moving_average[
        "average_drawdown_duration_days_rank"
    ] == 2

    assert buy_and_hold[
        "average_drawdown_duration_days_rank"
    ] == 3


def test_add_metric_ranks_rejects_missing_metrics():
    comparison = pd.DataFrame(
        [
            {
                "strategy": "BuyAndHold",
                "cagr": 0.12,
            }
        ]
    )

    with pytest.raises(
        ValueError,
        match="missing required ranking metrics",
    ):
        reporting.add_metric_ranks(
            comparison
        )

def test_add_benchmark_deltas():
    comparison = pd.DataFrame(
        [
            {
                "strategy": "BuyAndHold",
                "cagr": 0.14,
                "max_drawdown": 0.32,
                "daily_sharpe": 0.75,
                "calmar": 0.44,
                "max_drawdown_duration_days": 300,
            },
            {
                "strategy": "TimeSeriseMomentum",
                "cagr": 0.10,
                "max_drawdown": 0.17,
                "daily_sharpe": 1.02,
                "calmar": 0.62,
                "max_drawdown_duration_days": 120,
            },
        ]
    )

    result = reporting.add_benchmark_deltas(
        comparison=comparison,
        benchmark_strategy="BuyAndHold",
    )

    benchmark = result.loc[
        result["strategy"] == "BuyAndHold"
    ].iloc[0]

    momentum = result.loc[
        result["strategy"] == "TimeSeriseMomentum"
    ].iloc[0]

    assert benchmark["cagr_vs_benchmark"] == pytest.approx(0.0)
    assert benchmark["sharpe_vs_benchmark"] == pytest.approx(0.0)
    assert benchmark["calmar_vs_benchmark"] == pytest.approx(0.0)
    assert benchmark["max_drawdown_improvement"] == pytest.approx(0.0)

    assert momentum["cagr_vs_benchmark"] == pytest.approx(-0.04)
    assert momentum["sharpe_vs_benchmark"] == pytest.approx(0.27)
    assert momentum["calmar_vs_benchmark"] == pytest.approx(0.18)

    assert momentum[
        "max_drawdown_improvement"
    ] == pytest.approx(0.15)
    # print('\ntest:\n',momentum["max_drawdown_duration_improvement_days"], sys.stderr)
    assert momentum[
        "max_drawdown_duration_improvement_days"
    ] == pytest.approx(180)
    


def test_add_benchmark_deltas_with_empty_strategy():
        comparison = pd.DataFrame(
                [
                    {
                                    "strategy": "BuyAndHold",
                                    "cagr": 0.14,
                                    "max_drawdown": 0.32,
                                    "daily_sharpe": 0.75,
                                    "calmar": 0.44,
                                    "max_drawdown_duration_days": 300,
                    }
                ]
            )
        
        with pytest.raises(
                ValueError,
                match="at least one benchmark strategy",
            ):
             reporting.add_benchmark_deltas(
                        comparison=comparison,
                        benchmark_strategy="",
                    )    

def test_add_benchmark_deltas_allows_benchmark_only():
    comparison = pd.DataFrame(
        [
            {
                "strategy": "BuyAndHold",
                "cagr": 0.14,
                "max_drawdown": 0.32,
                "daily_sharpe": 0.75,
                "calmar": 0.44,
                "max_drawdown_duration_days": 300,
            }
        ]
    )

    result = reporting.add_benchmark_deltas(
        comparison=comparison,
        benchmark_strategy="BuyAndHold",
    )

    row = result.iloc[0]

    assert row["cagr_vs_benchmark"] == pytest.approx(0.0)
    assert row["sharpe_vs_benchmark"] == pytest.approx(0.0)
    assert row["calmar_vs_benchmark"] == pytest.approx(0.0)
    assert row["max_drawdown_improvement"] == pytest.approx(0.0)

    assert row[
        "max_drawdown_duration_improvement_days"
    ] == pytest.approx(0.0)

def test_add_benchmark_deltas_rejects_missing_benchmark():
    comparison = pd.DataFrame(
        [
            {
                "strategy": "TimeSeriseMomentum",
                "cagr": 0.10,
                "max_drawdown": 0.17,
                "daily_sharpe": 1.02,
                "calmar": 0.62,
                "max_drawdown_duration_days": 120,
            },
            {
                "strategy": "MovingAverageCross",
                "cagr": 0.08,
                "max_drawdown": 0.20,
                "daily_sharpe": 0.76,
                "calmar": 0.44,
                "max_drawdown_duration_days": 180,
            },
        ]
    )

    with pytest.raises(
        ValueError,
        match="benchmark strategy not found",
    ):
        reporting.add_benchmark_deltas(
            comparison=comparison,
            benchmark_strategy="BuyAndHold",
        )


def test_add_benchmark_deltas_rejects_duplicate_benchmark():
    comparison = pd.DataFrame(
        [
            {
                "strategy": "BuyAndHold",
                "cagr": 0.14,
                "max_drawdown": 0.32,
                "daily_sharpe": 0.75,
                "calmar": 0.44,
                "max_drawdown_duration_days": 300,
            },
            {
                "strategy": "BuyAndHold",
                "cagr": 0.13,
                "max_drawdown": 0.30,
                "daily_sharpe": 0.74,
                "calmar": 0.43,
                "max_drawdown_duration_days": 280,
            },
        ]
    )

    with pytest.raises(
        ValueError,
        match="benchmark strategy must be unique",
    ):
        reporting.add_benchmark_deltas(
            comparison=comparison,
            benchmark_strategy="BuyAndHold",
        )