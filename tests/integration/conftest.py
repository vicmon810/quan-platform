from datetime import date
from decimal import Decimal
import os
from collections.abc import Iterator
from typing import Any
from uuid import uuid4

import psycopg
import pytest
from psycopg import Connection
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row


EXPECTED_MIGRATIONS = {1, 2, 3, 4}

EXPECTED_TABLES = {
    "asset",
    "backtest_run",
    "backtest_metric",
    "portfolio_value",
}


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = os.environ.get("TEST_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "TEST_DATABASE_URL must be set"
        )

    connection_info = conninfo_to_dict(
        database_url
    )

    database_name = connection_info.get(
        "dbname"
    )

    if database_name != "quant_platform_test":
        raise RuntimeError(
            "integration tests must use "
            "quant_platform_test"
        )

    return database_url


@pytest.fixture(scope="session", autouse=True)
def verify_test_database(
    test_database_url: str,
) -> None:
    """
    Verify that the test database exists and V001-V004
    have been applied before running integration tests.
    """

    with psycopg.connect(
        test_database_url,
        autocommit=True,
        row_factory=dict_row,
        connect_timeout=5,
    ) as connection:
        migration_rows = connection.execute(
            """
            SELECT version
            FROM public.flyway_schema_history
            WHERE success = TRUE
              AND version IS NOT NULL;
            """
        ).fetchall()

        applied_versions = {
            int(row["version"])
            for row in migration_rows
        }

        missing_versions = (
            EXPECTED_MIGRATIONS
            - applied_versions
        )

        if missing_versions:
            pytest.fail(
                "test database is missing Flyway "
                f"migrations: {sorted(missing_versions)}"
            )

        table_rows = connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'quant';
            """
        ).fetchall()

        existing_tables = {
            row["table_name"]
            for row in table_rows
        }

        missing_tables = (
            EXPECTED_TABLES
            - existing_tables
        )

        if missing_tables:
            pytest.fail(
                "test database is missing tables: "
                f"{sorted(missing_tables)}"
            )


@pytest.fixture
def db_connection(
    test_database_url: str,
) -> Iterator[Connection[Any]]:
    """
    Provide one transactional PostgreSQL connection.

    All changes are rolled back after each test.
    """

    connection = psycopg.connect(
        test_database_url,
        autocommit=False,
        row_factory=dict_row,
        connect_timeout=5,
    )

    try:
        yield connection
    finally:
        if not connection.closed:
            connection.rollback()
            connection.close()


@pytest.fixture
def unique_suffix() -> str:
    """Return a unique uppercase identifier for test rows."""

    return uuid4().hex[:10].upper()


@pytest.fixture
def completed_backtest_payload(unique_suffix:str, ) -> dict[str, Any]:
    
    return{
        "asset": {
            "exchange_code": "NYSEARCA",
            "symbol": f"SPY{unique_suffix}",
            "display_name": "SPDR S&P 500 ETF Trust",
            "currency_code": "USD",
            "asset_type": "ETF",
        },
        "run": {
            "strategy_name": "BuyAndHold",
            "strategy_version": "1.0.0",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "initial_cash": Decimal("100000.00"),
            "parameters": {},
            "engine_version": "integration-test",
        },
        "metrics": {
            "final_value": Decimal("110000.00"),
            "cumulative_return": Decimal("0.10"),
            "cagr": Decimal("0.10"),
            "max_drawdown": Decimal("0.05"),
            "daily_sharpe": Decimal("1.20"),
            "calmar": Decimal("2.00"),
            "market_exposure": Decimal("0.95"),
            "max_drawdown_duration_days": 12,
            "average_drawdown_duration_days": Decimal("4.50"),
        },
        "portfolio_values": [
            {
                "trading_date": date(2024, 1, 2),
                "portfolio_value": Decimal("100000.00"),
                "market_exposure": Decimal("0.00"),
                "drawdown": Decimal("0.00"),
            },
            {
                "trading_date": date(2024, 1, 3),
                "portfolio_value": Decimal("105000.00"),
                "market_exposure": Decimal("0.95"),
                "drawdown": Decimal("0.00"),
            },
            {
                "trading_date": date(2024, 1, 4),
                "portfolio_value": Decimal("103000.00"),
                "market_exposure": Decimal("0.95"),
                "drawdown": Decimal("0.019047619047619"),
            },
        ],
    }