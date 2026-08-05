from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from psycopg import Connection
from psycopg.errors import (
    CheckViolation,
    ForeignKeyViolation,
    UniqueViolation,
)

from tests.integration.db_helpers import (
    insert_asset,
    insert_backtest_run,
)


pytestmark = pytest.mark.integration


@pytest.fixture
def asset_id(
    db_connection: Connection[Any],
    unique_suffix: str,
) -> int:
    return insert_asset(
        db_connection,
        symbol=f"RUN{unique_suffix}",
    )


def test_backtest_run_defaults_to_pending(
    db_connection: Connection[Any],
    asset_id: int,
) -> None:
    run_id = insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )

    row = db_connection.execute(
        """
        SELECT *
        FROM quant.backtest_run
        WHERE id = %(run_id)s;
        """,
        {"run_id": run_id},
    ).fetchone()

    assert row is not None
    assert row["status"] == "PENDING"
    assert row["started_at"] is None
    assert row["completed_at"] is None
    assert row["error_message"] is None
    assert row["parameters"] == {}
    assert isinstance(row["public_id"], UUID)


def test_backtest_runs_receive_unique_public_ids(
    db_connection: Connection[Any],
    asset_id: int,
) -> None:
    first_id = insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )

    second_id = insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )

    rows = db_connection.execute(
        """
        SELECT public_id
        FROM quant.backtest_run
        WHERE id IN (%(first_id)s, %(second_id)s);
        """,
        {
            "first_id": first_id,
            "second_id": second_id,
        },
    ).fetchall()

    public_ids = {
        row["public_id"]
        for row in rows
    }

    assert len(public_ids) == 2


def test_backtest_run_public_id_is_unique(
    db_connection: Connection[Any],
    asset_id: int,
) -> None:
    first_id = insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )

    row = db_connection.execute(
        """
        SELECT public_id
        FROM quant.backtest_run
        WHERE id = %(run_id)s;
        """,
        {"run_id": first_id},
    ).fetchone()

    assert row is not None
    public_id = row["public_id"]

    with pytest.raises(
        UniqueViolation
    ) as exception:
        db_connection.execute(
            """
            INSERT INTO quant.backtest_run (
                public_id,
                asset_id,
                strategy_name,
                start_date,
                end_date,
                initial_cash
            )
            VALUES (
                %(public_id)s,
                %(asset_id)s,
                'BuyAndHold',
                DATE '2020-01-01',
                DATE '2025-01-01',
                100000
            );
            """,
            {
                "public_id": public_id,
                "asset_id": asset_id,
            },
        )

    assert (
        exception.value.diag.constraint_name
        == "uq_backtest_run_public_id"
    )


@pytest.mark.parametrize(
    ("overrides", "constraint_name"),
    [
        (
            {"strategy_name": " "},
            "ck_backtest_run_strategy_name_not_blank",
        ),
        (
            {"strategy_version": " "},
            "ck_backtest_run_strategy_version_not_blank",
        ),
        (
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 1),
            },
            "ck_backtest_run_date_range",
        ),
        (
            {"initial_cash": Decimal("0")},
            "ck_backtest_run_initial_cash",
        ),
        (
            {"initial_cash": Decimal("-1")},
            "ck_backtest_run_initial_cash",
        ),
        (
            {"parameters": []},
            "ck_backtest_run_parameters_object",
        ),
    ],
)
def test_backtest_run_rejects_invalid_values(
    db_connection: Connection[Any],
    asset_id: int,
    overrides: dict[str, Any],
    constraint_name: str,
) -> None:
    arguments: dict[str, Any] = {
        "asset_id": asset_id,
    }

    arguments.update(overrides)

    with pytest.raises(
        CheckViolation
    ) as exception:
        insert_backtest_run(
            db_connection,
            **arguments,
        )

    assert (
        exception.value.diag.constraint_name
        == constraint_name
    )


def test_backtest_run_rejects_missing_asset(
    db_connection: Connection[Any],
) -> None:
    with pytest.raises(
        ForeignKeyViolation
    ):
        insert_backtest_run(
            db_connection,
            asset_id=9_999_999_999,
        )


@pytest.mark.parametrize(
    "status",
    [
        "DONE",
        "QUEUED",
        "CANCELLED",
    ],
)
def test_backtest_run_rejects_unknown_status(
    db_connection: Connection[Any],
    asset_id: int,
    status: str,
) -> None:
    with pytest.raises(CheckViolation):
        insert_backtest_run(
            db_connection,
            asset_id=asset_id,
            status=status,
        )


@pytest.mark.parametrize(
    "status",
    [
        "RUNNING",
        "COMPLETED",
        "FAILED",
    ],
)
def test_backtest_run_accepts_valid_lifecycle_states(
    db_connection: Connection[Any],
    asset_id: int,
    status: str,
) -> None:
    started_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=1)
    )

    completed_at = None
    error_message = None

    if status in {"COMPLETED", "FAILED"}:
        completed_at = (
            started_at
            + timedelta(minutes=1)
        )

    if status == "FAILED":
        error_message = "Test failure"

    run_id = insert_backtest_run(
        db_connection,
        asset_id=asset_id,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        error_message=error_message,
    )

    assert run_id > 0


@pytest.mark.parametrize(
    (
        "status",
        "has_started_at",
        "has_completed_at",
        "error_message",
    ),
    [
        ("PENDING", True, False, None),
        ("RUNNING", False, False, None),
        ("RUNNING", True, True, None),
        ("COMPLETED", True, False, None),
        ("FAILED", True, True, None),
        ("FAILED", True, True, " "),
    ],
)
def test_backtest_run_rejects_invalid_lifecycle(
    db_connection: Connection[Any],
    asset_id: int,
    status: str,
    has_started_at: bool,
    has_completed_at: bool,
    error_message: str | None,
) -> None:
    base_time = (
        datetime.now(timezone.utc)
        + timedelta(minutes=1)
    )

    started_at = (
        base_time
        if has_started_at
        else None
    )

    completed_at = (
        base_time + timedelta(minutes=1)
        if has_completed_at
        else None
    )

    with pytest.raises(CheckViolation):
        insert_backtest_run(
            db_connection,
            asset_id=asset_id,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
        )


def test_backtest_run_rejects_reversed_timestamps(
    db_connection: Connection[Any],
    asset_id: int,
) -> None:
    started_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=2)
    )

    completed_at = (
        started_at
        - timedelta(minutes=1)
    )

    with pytest.raises(
        CheckViolation
    ) as exception:
        insert_backtest_run(
            db_connection,
            asset_id=asset_id,
            status="COMPLETED",
            started_at=started_at,
            completed_at=completed_at,
        )

    assert (
        exception.value.diag.constraint_name
        == "ck_backtest_run_timestamp_order"
    )


def test_asset_delete_is_restricted_when_run_exists(
    db_connection: Connection[Any],
    asset_id: int,
) -> None:
    insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )

    with pytest.raises(
        ForeignKeyViolation
    ):
        db_connection.execute(
            """
            DELETE FROM quant.asset
            WHERE id = %(asset_id)s;
            """,
            {"asset_id": asset_id},
        )


def test_backtest_run_updated_at_trigger_runs(
    db_connection: Connection[Any],
    asset_id: int,
) -> None:
    run_id = insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )

    row = db_connection.execute(
        """
        UPDATE quant.backtest_run
        SET
            engine_version = 'updated-test',
            updated_at = TIMESTAMPTZ
                '2000-01-01 00:00:00+00'
        WHERE id = %(run_id)s
        RETURNING updated_at;
        """,
        {"run_id": run_id},
    ).fetchone()

    assert row is not None
    assert row["updated_at"].year > 2000


def test_backtest_run_expected_indexes_exist(
    db_connection: Connection[Any],
) -> None:
    rows = db_connection.execute(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'quant'
          AND tablename = 'backtest_run';
        """
    ).fetchall()

    indexes = {
        row["indexname"]
        for row in rows
    }

    assert {
        "idx_backtest_run_asset_created_at",
        "idx_backtest_run_status_created_at",
        "idx_backtest_run_strategy_created_at",
    }.issubset(indexes)