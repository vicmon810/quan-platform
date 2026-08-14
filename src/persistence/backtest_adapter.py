from collections.abc import Mapping
from decimal import Decimal
from typing import Any

NON_STRATEGY_FIELDS = {
    "ticker",
    "strategy",
    "start_year",
    "end_year",
    "final_value",
    "trades",
    "portfolio_values",
    "signal_history",
    "cumulative_return",
    "cagr",
    "max_drawdown",
    "daily_sharpe",
    "calmar",
    "market_exposure",
    "max_drawdown_duration_days",
    "average_drawdown_duration_days",
}

def build_persistence_payload(
        result: Mapping[str,Any],
        *,
        exchange_code:str,
        display_name:str,
        currency_code:str,
        asset_type:str,
        initial_cash: Decimal,
        strategy_version:str,
        engine_version:str,
) -> dict[str, Any]:
    portfolio_values = result["portfolio_values"]

    asset = {
        "exchange_code":exchange_code,
        "symbol": result["ticker"],
        "display_name":display_name,
        "currency_code":currency_code,
        "asset_type": asset_type,
    }

    strategy_parameter = {
        key: value
        for key, value in result.items()
        if key not in NON_STRATEGY_FIELDS
    }

    run = {
        "strategy_name": result["strategy"],
        "strategy_version": strategy_version,
        "start_date": portfolio_values[0]["date"],
        "end_date":portfolio_values[-1]["date"],
        "initial_cash": initial_cash,
        "parameters": strategy_parameter,
        "engine_version": engine_version,
    }

    return {"asset":asset, "run":run,}