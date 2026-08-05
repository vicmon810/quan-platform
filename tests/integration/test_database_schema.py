from typing import Any

import pytest
from psycopg import Connection


pytestmark = pytest.mark.integration


def test_flyway_migrations_v001_to_v004_succeeded(
    db_connection: Connection[Any],
) -> None:
    rows = db_connection.execute(
        """
        SELECT
            version,
            description,
            success
        FROM public.flyway_schema_history
        WHERE version IS NOT NULL
        ORDER BY installed_rank;
        """
    ).fetchall()

    versions = {
        int(row["version"])
        for row in rows
        if row["success"]
    }

    assert {1, 2, 3, 4}.issubset(versions)


def test_expected_quant_tables_exist(
    db_connection: Connection[Any],
) -> None:
    rows = db_connection.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'quant';
        """
    ).fetchall()

    table_names = {
        row["table_name"]
        for row in rows
    }

    assert {
        "asset",
        "backtest_run",
        "backtest_metric",
        "portfolio_value",
    }.issubset(table_names)