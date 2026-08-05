from datetime import date, datetime
from decimal import Decimal
from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb


def insert_asset(
    connection: Connection[Any],
    *,
    exchange_code: str = "NYSEARCA",
    symbol: str = "SPY_TEST",
    display_name: str = "Test Asset",
    currency_code: str = "USD",
    asset_type: str = "ETF",
) -> int:
    row = connection.execute(
        """
        INSERT INTO quant.asset (
            exchange_code,
            symbol,
            display_name,
            currency_code,
            asset_type
        )
        VALUES (
            %(exchange_code)s,
            %(symbol)s,
            %(display_name)s,
            %(currency_code)s,
            %(asset_type)s
        )
        RETURNING id;
        """,
        {
            "exchange_code": exchange_code,
            "symbol": symbol,
            "display_name": display_name,
            "currency_code": currency_code,
            "asset_type": asset_type,
        },
    ).fetchone()

    assert row is not None

    return int(row["id"])


def insert_backtest_run(
    connection: Connection[Any],
    *,
    asset_id: int,
    strategy_name: str = "BuyAndHold",
    strategy_version: str = "1.0.0",
    start_date: date = date(2020, 1, 1),
    end_date: date = date(2025, 1, 1),
    initial_cash: Decimal = Decimal(
        "100000.00"
    ),
    parameters: object = None,
    status: str = "PENDING",
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
    error_message: str | None = None,
) -> int:
    parameter_value = (
        {}
        if parameters is None
        else parameters
    )

    row = connection.execute(
        """
        INSERT INTO quant.backtest_run (
            asset_id,
            strategy_name,
            strategy_version,
            start_date,
            end_date,
            initial_cash,
            parameters,
            status,
            engine_version,
            started_at,
            completed_at,
            error_message
        )
        VALUES (
            %(asset_id)s,
            %(strategy_name)s,
            %(strategy_version)s,
            %(start_date)s,
            %(end_date)s,
            %(initial_cash)s,
            %(parameters)s,
            %(status)s,
            'integration-test',
            %(started_at)s,
            %(completed_at)s,
            %(error_message)s
        )
        RETURNING id;
        """,
        {
            "asset_id": asset_id,
            "strategy_name": strategy_name,
            "strategy_version": strategy_version,
            "start_date": start_date,
            "end_date": end_date,
            "initial_cash": initial_cash,
            "parameters": Jsonb(
                parameter_value
            ),
            "status": status,
            "started_at": started_at,
            "completed_at": completed_at,
            "error_message": error_message,
        },
    ).fetchone()

    assert row is not None

    return int(row["id"])


def insert_backtest_metric(
    connection: Connection[Any],
    *,
    backtest_run_id: int,
    final_value: Decimal = Decimal(
        "150000.00"
    ),
    cumulative_return: Decimal = Decimal(
        "0.50"
    ),
    cagr: Decimal = Decimal("0.10"),
    max_drawdown: Decimal = Decimal("0.20"),
    daily_sharpe: Decimal | None = Decimal(
        "0.80"
    ),
    calmar: Decimal | None = Decimal("0.50"),
    market_exposure: Decimal = Decimal(
        "0.95"
    ),
    max_drawdown_duration_days: int = 100,
    average_drawdown_duration_days: Decimal = (
        Decimal("20.00")
    ),
) -> None:
    connection.execute(
        """
        INSERT INTO quant.backtest_metric (
            backtest_run_id,
            final_value,
            cumulative_return,
            cagr,
            max_drawdown,
            daily_sharpe,
            calmar,
            market_exposure,
            max_drawdown_duration_days,
            average_drawdown_duration_days
        )
        VALUES (
            %(backtest_run_id)s,
            %(final_value)s,
            %(cumulative_return)s,
            %(cagr)s,
            %(max_drawdown)s,
            %(daily_sharpe)s,
            %(calmar)s,
            %(market_exposure)s,
            %(max_duration)s,
            %(average_duration)s
        );
        """,
        {
            "backtest_run_id": backtest_run_id,
            "final_value": final_value,
            "cumulative_return": (
                cumulative_return
            ),
            "cagr": cagr,
            "max_drawdown": max_drawdown,
            "daily_sharpe": daily_sharpe,
            "calmar": calmar,
            "market_exposure": market_exposure,
            "max_duration": (
                max_drawdown_duration_days
            ),
            "average_duration": (
                average_drawdown_duration_days
            ),
        },
    )


def insert_portfolio_value(
    connection: Connection[Any],
    *,
    backtest_run_id: int,
    trading_date: date = date(2024, 1, 2),
    portfolio_value: Decimal = Decimal(
        "100000.00"
    ),
    market_exposure: Decimal = Decimal(
        "0.95"
    ),
    drawdown: Decimal = Decimal("0.00"),
) -> None:
    connection.execute(
        """
        INSERT INTO quant.portfolio_value (
            backtest_run_id,
            trading_date,
            portfolio_value,
            market_exposure,
            drawdown
        )
        VALUES (
            %(backtest_run_id)s,
            %(trading_date)s,
            %(portfolio_value)s,
            %(market_exposure)s,
            %(drawdown)s
        );
        """,
        {
            "backtest_run_id": backtest_run_id,
            "trading_date": trading_date,
            "portfolio_value": portfolio_value,
            "market_exposure": market_exposure,
            "drawdown": drawdown,
        },
    )