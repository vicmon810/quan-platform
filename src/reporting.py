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

    return pd.DataFrame(results)[
        COMPARISON_COLUMNS
    ].copy()