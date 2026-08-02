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