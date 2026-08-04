from collections.abc import Sequence
from typing import Any, Literal

import pandas as pd


COMPARISON_COLUMNS = [
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

RANK_PREFERENCE = Literal["higher", "lower"]

RANK_RULES: dict[str, RANK_PREFERENCE] = {
    "cagr": "higher",
    "max_drawdown": "lower",
    "daily_sharpe": "higher",
    "calmar": "higher",
    "max_drawdown_duration_days": "lower",
    "average_drawdown_duration_days": "lower",    
}

def build_strategy_comparison(
    results: Sequence[dict[str, Any]],
) -> pd.DataFrame:
    """Build a strategy performance comparison table."""

    if not results:
        raise ValueError(
            "at least one strategy result is required"
        )
    required_fields = set(COMPARISON_COLUMNS)
    for index, result in enumerate(results):
        missing_fields = required_fields - result.keys()

        if missing_fields:
            missing_name = ", ".join(sorted(missing_fields))
            raise ValueError(f"missing required comparison fields in result {index}:{missing_name}" )

    return pd.DataFrame(results)[
        COMPARISON_COLUMNS
    ].copy()


def add_metric_ranks(comparison:pd.DataFrame) -> pd.DataFrame:
    """add per-metric ranks to a strategy comparison table"""
    missing_metrics = [metric for metric in RANK_RULES if metric not in comparison.columns]

    if missing_metrics:
        raise ValueError(f"missing required ranking metrics: {missing_metrics}")

    ranked = comparison.copy()
    rank_columns: list[str] = []

    for metric,preference in RANK_RULES.items():
        rank_column = f"{metric}_rank"
        ranked[rank_column] = ranked[metric].rank(
            ascending=preference == "lower",
            method="min",
            na_option="bottom"
        )
        rank_columns.append(rank_column)

    ranked[rank_columns] = (
        ranked[rank_columns].astype("Int64")
    )

    return ranked


def add_benchmark_deltas(comparison:pd.DataFrame, benchmark_strategy:str)-> pd.DataFrame:
    """
    Add per-strategy deltas relative to a chosen benchmark strategy.

    For return-oriented metrics (cagr, sharpe, calmar), the delta is
    (strategy - benchmark), so positive means better.
    For risk metrics (max_drawdown, max_drawdown_duration_days), the
    "improvement" is (benchmark - strategy), so positive still means better
    (i.e. less risk than the benchmark).
    """
    require_columns = [
        "strategy",
        "cagr",
        "max_drawdown",
        "daily_sharpe",
        "calmar",
        "max_drawdown_duration_days"
        ]
    
    if not benchmark_strategy.strip():
        raise ValueError("at least one benchmark strategy")

    missing_columns = [column for column in require_columns if column not in comparison.columns ]

    if missing_columns: 
        raise ValueError(f"missing required benchmark fields: {missing_columns}")

    if len(comparison ) <1:
        raise ValueError("at least two portfolio value")

    matching_rows = comparison.loc[comparison["strategy"] == benchmark_strategy]

    if matching_rows.empty:
        raise ValueError( f"benchmark strategy not found in comparison: '{benchmark_strategy}'")

    if len(matching_rows) > 1:
            raise ValueError(f"benchmark strategy must be unique: '{benchmark_strategy}'")

    result = comparison.copy()

    benchmark_rows = matching_rows.iloc[0]
    
    result["cagr_vs_benchmark"] = result["cagr"] - benchmark_rows["cagr"]
    result["sharpe_vs_benchmark"] = result["daily_sharpe"] - benchmark_rows["daily_sharpe"]
    result["calmar_vs_benchmark"] = result["calmar"] - benchmark_rows["calmar"]
    result["max_drawdown_improvement"] =   benchmark_rows["max_drawdown"] - result["max_drawdown"]
    result["max_drawdown_duration_improvement_days"] =   (
        benchmark_rows["max_drawdown_duration_days"] - result["max_drawdown_duration_days"]
    )

    return result