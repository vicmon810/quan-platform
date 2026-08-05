from typing import Any

import pytest
from psycopg import Connection
from psycopg.errors import (
    CheckViolation,
    UniqueViolation,
)

from tests.integration.db_helpers import (
    insert_asset,
)


pytestmark = pytest.mark.integration


def test_asset_accepts_valid_row_and_defaults(
    db_connection: Connection[Any],
    unique_suffix: str,
) -> None:
    asset_id = insert_asset(
        db_connection,
        exchange_code="NZX",
        symbol=f"FPH{unique_suffix}",
        display_name=(
            "Fisher & Paykel Healthcare Test"
        ),
        currency_code="NZD",
        asset_type="EQUITY",
    )

    row = db_connection.execute(
        """
        SELECT *
        FROM quant.asset
        WHERE id = %(asset_id)s;
        """,
        {"asset_id": asset_id},
    ).fetchone()

    assert row is not None
    assert row["exchange_code"] == "NZX"
    assert row["currency_code"] == "NZD"
    assert row["asset_type"] == "EQUITY"
    assert row["is_active"] is True
    assert row["created_at"] is not None
    assert row["updated_at"] is not None


def test_asset_rejects_duplicate_exchange_symbol(
    db_connection: Connection[Any],
    unique_suffix: str,
) -> None:
    symbol = f"DUP{unique_suffix}"

    insert_asset(
        db_connection,
        exchange_code="ASX",
        symbol=symbol,
    )

    with pytest.raises(
        UniqueViolation
    ) as exception:
        insert_asset(
            db_connection,
            exchange_code="ASX",
            symbol=symbol,
            display_name="Duplicate Asset",
        )

    assert (
        exception.value.diag.constraint_name
        == "uq_asset_exchange_symbol"
    )


def test_asset_allows_same_symbol_on_different_exchanges(
    db_connection: Connection[Any],
    unique_suffix: str,
) -> None:
    symbol = f"TEST{unique_suffix}"

    first_id = insert_asset(
        db_connection,
        exchange_code="NZX",
        symbol=symbol,
        currency_code="NZD",
    )

    second_id = insert_asset(
        db_connection,
        exchange_code="ASX",
        symbol=symbol,
        currency_code="AUD",
    )

    assert first_id != second_id


@pytest.mark.parametrize(
    ("overrides", "constraint_name"),
    [
        (
            {"exchange_code": " "},
            "ck_asset_exchange_code_not_blank",
        ),
        (
            {"exchange_code": "asx"},
            "ck_asset_exchange_code_uppercase",
        ),
        (
            {"symbol": " "},
            "ck_asset_symbol_not_blank",
        ),
        (
            {"symbol": "aapl"},
            "ck_asset_symbol_uppercase",
        ),
        (
            {"display_name": " "},
            "ck_asset_display_name_not_blank",
        ),
        (
            {"currency_code": "US"},
            "ck_asset_currency_code",
        ),
        (
            {"currency_code": "usd"},
            "ck_asset_currency_code",
        ),
        (
            {"asset_type": "CRYPTO"},
            "ck_asset_type",
        ),
    ],
)
def test_asset_rejects_invalid_values(
    db_connection: Connection[Any],
    unique_suffix: str,
    overrides: dict[str, str],
    constraint_name: str,
) -> None:
    arguments = {
        "exchange_code": "NASDAQ",
        "symbol": f"BAD{unique_suffix}",
        "display_name": "Invalid Test Asset",
        "currency_code": "USD",
        "asset_type": "EQUITY",
    }

    arguments.update(overrides)

    with pytest.raises(
        CheckViolation
    ) as exception:
        insert_asset(
            db_connection,
            **arguments,
        )

    assert (
        exception.value.diag.constraint_name
        == constraint_name
    )


def test_asset_updated_at_trigger_runs(
    db_connection: Connection[Any],
    unique_suffix: str,
) -> None:
    asset_id = insert_asset(
        db_connection,
        symbol=f"UPDATE{unique_suffix}",
    )

    row = db_connection.execute(
        """
        UPDATE quant.asset
        SET
            display_name = 'Updated Asset',
            updated_at = TIMESTAMPTZ
                '2000-01-01 00:00:00+00'
        WHERE id = %(asset_id)s
        RETURNING updated_at;
        """,
        {"asset_id": asset_id},
    ).fetchone()

    assert row is not None
    assert row["updated_at"].year > 2000


def test_asset_symbol_index_exists(
    db_connection: Connection[Any],
) -> None:
    rows = db_connection.execute(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'quant'
          AND tablename = 'asset';
        """
    ).fetchall()

    indexes = {
        row["indexname"]
        for row in rows
    }

    assert "idx_asset_symbol" in indexes