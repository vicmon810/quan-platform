from collections.abc import Sequence
from typing import Any

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
    ranked = comparison.copy()

    ranked["cagr_rank"] = ranked["cagr"].rank(
        ascending=False,
        method='min',
        na_option='bottom'
    )
    ranked["max_drawdown_rank"] = ranked["max_drawdown"].rank(
            ascending=True,
            method='min',
            na_option='bottom'
        )
    ranked["daily_sharpe_rank"] = ranked["daily_sharpe"].rank(
            ascending=False,
            method='min',
            na_option='bottom'
        )
    ranked["calmar_rank"] = ranked["calmar"].rank(
            ascending=False,
            method='min',
            na_option='bottom'
        )
    rank_columns = [
        "cagr_rank",
        "max_drawdown_rank",
        "daily_sharpe_rank",
        "calmar_rank",
    ]

    ranked[rank_columns] = (
        ranked[rank_columns].astype("Int64")
    )

    return ranked