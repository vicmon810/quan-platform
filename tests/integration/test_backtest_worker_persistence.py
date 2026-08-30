from datetime import date
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest
from psycopg import Connection

from src.persistence import backtest_repository
from src.domain.backtest_job import BacktestJob

pytestmark = pytest.mark.integration


def test_complete_backtest_run_persists_result_into_existing_run(
    db_connection: Connection[Any],
) -> None:
    suffix = uuid4().hex[:8].upper()
    symbol = f"WT{suffix}"

    asset = db_connection.execute(
        """
        INSERT INTO quant.asset (
            exchange_code,
            symbol,
            data_symbol,
            display_name,
            currency_code,
            asset_type
        )
        VALUES (
            'ASX',
            %(symbol)s,
            %(data_symbol)s,
            'Worker Test Asset',
            'AUD',
            'EQUITY'
        )
        RETURNING id;
        """,
        {
            "symbol": symbol,
            "data_symbol": f"{symbol}.AX",
        },
    ).fetchone()

    assert asset is not None

    run = db_connection.execute(
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
            started_at
        )
        VALUES (
            %(asset_id)s,
            'BuyAndHold',
            '1.0.0',
            DATE '2020-01-01',
            DATE '2025-01-01',
            10000,
            '{}'::jsonb,
            'RUNNING',
            CURRENT_TIMESTAMP
        )
        RETURNING id, public_id;
        """,
        {
            "asset_id": asset["id"],
        },
    ).fetchone()

    assert run is not None

    metrics = {
        "final_value": Decimal("11000.00"),
        "cumulative_return": Decimal("0.10"),
        "cagr": Decimal("0.024"),
        "max_drawdown": Decimal("0.05"),
        "daily_sharpe": Decimal("1.20"),
        "calmar": Decimal("0.48"),
        "market_exposure": Decimal("0.95"),
        "max_drawdown_duration_days": 3,
        "average_drawdown_duration_days": Decimal("1.5"),
    }

    portfolio_values = [
        {
            "trading_date": date(2020, 1, 2),
            "portfolio_value": Decimal("10000.00"),
            "market_exposure": Decimal("0"),
            "drawdown": Decimal("0"),
        },
        {
            "trading_date": date(2020, 1, 3),
            "portfolio_value": Decimal("11000.00"),
            "market_exposure": Decimal("0.95"),
            "drawdown": Decimal("0"),
        },
    ]

    backtest_repository.complete_backtest_run(
        connection=db_connection,
        run_id=run["id"],
        metrics=metrics,
        portfolio_values=portfolio_values,
    )

    saved_run = db_connection.execute(
        """
        SELECT
            status,
            completed_at,
            error_message
        FROM quant.backtest_run
        WHERE id = %(run_id)s;
        """,
        {
            "run_id": run["id"],
        },
    ).fetchone()

    assert saved_run is not None
    assert saved_run["status"] == "COMPLETED"
    assert saved_run["completed_at"] is not None
    assert saved_run["error_message"] is None

    saved_metric = db_connection.execute(
        """
        SELECT
            final_value,
            cumulative_return
        FROM quant.backtest_metric
        WHERE backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run["id"],
        },
    ).fetchone()

    assert saved_metric is not None
    assert saved_metric["final_value"] == Decimal("11000.000000")
    assert saved_metric["cumulative_return"] == Decimal("0.100000000000000")

    portfolio_count = db_connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM quant.portfolio_value
        WHERE backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run["id"],
        },
    ).fetchone()

    assert portfolio_count is not None
    assert portfolio_count["count"] == 2

    run_count = db_connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM quant.backtest_run
        WHERE asset_id = %(asset_id)s;
        """,
        {
            "asset_id": asset["id"],
        },
    ).fetchone()

    assert run_count is not None

    # Worker must complete the existing job,
    # not create another backtest_run.
    assert run_count["count"] == 1

def test_fail_backtest_run_marks_existing_run_failed(
        db_connection: Connection[Any]
) -> None:
    suffix =uuid4().hex[:8].upper()
    symbol = f"WT{suffix}"

    asset = db_connection.execute(
        """
        INSERT INTO
            quant.asset(
                exchange_code,
                symbol,
                data_symbol,
                display_name,
                currency_code,
                asset_type
            )
        VALUES(
            'ASX',
            %(symbol)s,
            %(data_symbol)s,
            'worker failure Test Asset',
            'AUD',
            'EQUITY'
        )
        RETURNING
        id;
        """,
        {
            "symbol": symbol,
            "data_symbol": f"{symbol}.AX"
        },
    ).fetchone()

    assert asset is not None 


    run = db_connection.execute(
        """
        INSERT INTO 
            quant.backtest_run(
                asset_id,
                strategy_name,
                strategy_version,
                start_date,
                end_date,
                initial_cash,
                parameters,
                status,
                started_at
            )
        VALUES (
            %(asset_id)s,
            'BuyAndHold',
            '1.0.0',
            DATE '2020-01-01',
            DATE '2025-01-01',
            10000,
            '{}'::jsonb,
            'RUNNING',
            CURRENT_TIMESTAMP
        )
        RETURNING
            id, 
            public_id;
        """,{
            "asset_id": asset['id'],
        },
    ).fetchone()

    assert run is not None 

    backtest_repository.fail_backtest_run(
        connection = db_connection,
        run_id = run['id'],
        error_message = "market data file not found"
    )

    saved_run = db_connection.execute(
        """
            SELECT 
                status,
                started_at,
                completed_at,
                error_message
            FROM 
                quant.backtest_run
            WHERE
                id = %(run_id)s;
        """,
        {
            "run_id": run['id']
        },
    ).fetchone()

    assert saved_run is not None 

    assert saved_run['status'] == 'FAILED'
    assert saved_run['started_at'] is not None 
    assert saved_run['completed_at'] is not None 
    assert saved_run['error_message']  == "market data file not found"