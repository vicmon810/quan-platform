from collections.abc import Mapping
from decimal import Decimal
from typing import Any
import sys

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

def to_decimal(value:int | float|Decimal) -> Decimal:
    return Decimal(str(value))

def to_optional_decimal(value:int|float|Decimal) -> Decimal|None:
    if value is None:  return None
    return Decimal(str(value))

def build_portfolio_values(portfolio_values: list[Mapping[str,Any]])->list[dict[str,Any]]:
    result = []

    running_peak: Decimal | None = None 

    for record in portfolio_values:
        portfolio_value = to_decimal(record["value"])
        market_exposure = to_decimal(record["exposure"])

        if (running_peak is None or portfolio_value > running_peak):
            running_peak = portfolio_value

        drawdown = (running_peak - portfolio_value)/running_peak

        result.append(
            {
                "trading_date": record["date"],
                "portfolio_value": portfolio_value,
                "market_exposure":market_exposure,
                "drawdown": drawdown,
            }
        )

    return result


def build_persistence_payload(
    result: Mapping[str, Any],
    *,
    exchange_code: str,
    symbol:str,
    display_name: str,
    currency_code: str,
    asset_type: str,
    initial_cash: Decimal,
    strategy_version: str,
    engine_version: str,
) -> dict[str, Any]:

    raw_portfolio_values = result["portfolio_values"]
    # print(f"=TEST="*3, '\n{result["portfolio_values"]}',"\n", file=sys.stderr)
    if not raw_portfolio_values :
        raise ValueError("portfolio_values cannot be empty")
    asset = {
        "exchange_code": exchange_code,
        "symbol": symbol,#result["ticker"],
        "data_symbol":result["ticker"],
        "display_name": display_name,
        "currency_code": currency_code,
        "asset_type": asset_type,
    }

    strategy_parameters = {
        key: value
        for key, value in result.items()
        if key not in NON_STRATEGY_FIELDS
    }

    run = {
        "strategy_name": result["strategy"],
        "strategy_version": strategy_version,
        "start_date": raw_portfolio_values[0]["date"],
        "end_date": raw_portfolio_values[-1]["date"],
        "initial_cash": initial_cash,
        "parameters": strategy_parameters,
        "engine_version": engine_version,
    }

    output = build_backtest_output(result=result)
    return {
        "asset": asset,
        "symbol":symbol,
        # "data_symbol": result["ticker"],
        "run": run,
        "portfolio_values": output["portfolio_values"],
        "metrics": output['metrics'],
    }


def build_backtest_output(
    result: Mapping[str, Any],
) -> dict[str, Any]:
    metrics = {
        "final_value": to_decimal(result["final_value"]),
        "cumulative_return": to_decimal(result["cumulative_return"]),
        "cagr": to_decimal(result["cagr"]),
        "max_drawdown": to_decimal(result["max_drawdown"]),
        "daily_sharpe": to_optional_decimal(result["daily_sharpe"]),
        "calmar": to_optional_decimal(result["calmar"]),
        "market_exposure": to_decimal(result["market_exposure"]),
        "max_drawdown_duration_days": int(
            result["max_drawdown_duration_days"]
        ),
        "average_drawdown_duration_days": to_decimal(
            result["average_drawdown_duration_days"]
        ),
    }

    portfolio_values = build_portfolio_values(
        result["portfolio_values"]
    )

    return {
        "metrics": metrics,
        "portfolio_values": portfolio_values,
    }