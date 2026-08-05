from datetime import date
from decimal import Decimal
from typing import Any

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
    insert_portfolio_value,
)


pytestmark = pytest.mark.integration


@pytest.fixture
def run_id(
    db_connection: Connection[Any],
    unique_suffix: str,
) -> int:
    asset_id = insert_asset(
        db_connection,
        symbol=f"VALUE{unique_suffix}",
    )

    return insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )


def test_portfolio_value_accepts_valid_row(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_portfolio_value(
        db_connection,
        backtest_run_id=run_id,
        trading_date=date(2024, 1, 2),
        portfolio_value=Decimal("100000"),
        market_exposure=Decimal("0.95"),
        drawdown=Decimal("0"),
    )

    row = db_connection.execute(
        """
        SELECT *
        FROM quant.portfolio_value
        WHERE backtest_run_id = %(run_id)s
          AND trading_date = DATE '2024-01-02';
        """,
        {"run_id": run_id},
    ).fetchone()

    assert row is not None
    assert row["portfolio_value"] == Decimal(
        "100000.000000"
    )
    assert row["market_exposure"] == Decimal(
        "0.950000000000000"
    )
    assert row["drawdown"] == Decimal(
        "0.000000000000000"
    )


def test_portfolio_value_rejects_duplicate_run_date(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    trading_date = date(2024, 1, 2)

    insert_portfolio_value(
        db_connection,
        backtest_run_id=run_id,
        trading_date=trading_date,
    )

    with pytest.raises(
        UniqueViolation
    ) as exception:
        insert_portfolio_value(
            db_connection,
            backtest_run_id=run_id,
            trading_date=trading_date,
        )

    assert (
        exception.value.diag.constraint_name
        == "uq_portfolio_value_run_date"
    )


def test_portfolio_value_allows_same_date_for_different_runs(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    row = db_connection.execute(
        """
        INSERT INTO quant.backtest_run (
            asset_id,
            strategy_name,
            start_date,
            end_date,
            initial_cash
        )
        SELECT
            asset_id,
            'MovingAverageCross',
            start_date,
            end_date,
            initial_cash
        FROM quant.backtest_run
        WHERE id = %(run_id)s
        RETURNING id;
        """,
        {"run_id": run_id},
    ).fetchone()

    assert row is not None
    second_run_id = row["id"]

    trading_date = date(2024, 1, 2)

    insert_portfolio_value(
        db_connection,
        backtest_run_id=run_id,
        trading_date=trading_date,
    )

    insert_portfolio_value(
        db_connection,
        backtest_run_id=second_run_id,
        trading_date=trading_date,
    )

    row = db_connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM quant.portfolio_value
        WHERE trading_date = %(trading_date)s;
        """,
        {"trading_date": trading_date},
    ).fetchone()

    assert row is not None
    count = row["count"]
    assert count == 2


def test_portfolio_value_rejects_missing_run(
    db_connection: Connection[Any],
) -> None:
    with pytest.raises(
        ForeignKeyViolation
    ):
        insert_portfolio_value(
            db_connection,
            backtest_run_id=9_999_999_999,
        )


@pytest.mark.parametrize(
    ("overrides", "constraint_name"),
    [
        (
            {"portfolio_value": Decimal("0")},
            "ck_portfolio_value_positive",
        ),
        (
            {
                "portfolio_value": Decimal(
                    "-1"
                )
            },
            "ck_portfolio_value_positive",
        ),
        (
            {
                "portfolio_value": Decimal(
                    "NaN"
                )
            },
            "ck_portfolio_value_positive",
        ),
        (
            {
                "market_exposure": Decimal(
                    "-0.01"
                )
            },
            "ck_portfolio_value_market_exposure",
        ),
        (
            {
                "market_exposure": Decimal(
                    "NaN"
                )
            },
            "ck_portfolio_value_market_exposure",
        ),
        (
            {"drawdown": Decimal("-0.01")},
            "ck_portfolio_value_drawdown",
        ),
        (
            {"drawdown": Decimal("1.01")},
            "ck_portfolio_value_drawdown",
        ),
        (
            {"drawdown": Decimal("NaN")},
            "ck_portfolio_value_drawdown",
        ),
    ],
)
def test_portfolio_value_rejects_invalid_values(
    db_connection: Connection[Any],
    run_id: int,
    overrides: dict[str, Any],
    constraint_name: str,
) -> None:
    arguments: dict[str, Any] = {
        "backtest_run_id": run_id,
    }

    arguments.update(overrides)

    with pytest.raises(
        CheckViolation
    ) as exception:
        insert_portfolio_value(
            db_connection,
            **arguments,
        )

    assert (
        exception.value.diag.constraint_name
        == constraint_name
    )


@pytest.mark.parametrize(
    "drawdown",
    [
        Decimal("0"),
        Decimal("1"),
    ],
)
def test_portfolio_value_accepts_drawdown_boundaries(
    db_connection: Connection[Any],
    run_id: int,
    drawdown: Decimal,
) -> None:
    insert_portfolio_value(
        db_connection,
        backtest_run_id=run_id,
        drawdown=drawdown,
    )


def test_portfolio_value_allows_leveraged_exposure(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_portfolio_value(
        db_connection,
        backtest_run_id=run_id,
        market_exposure=Decimal("1.75"),
    )

    row = db_connection.execute(
        """
        SELECT market_exposure
        FROM quant.portfolio_value
        WHERE backtest_run_id = %(run_id)s;
        """,
        {"run_id": run_id},
    ).fetchone()
    assert row is not None
    exposure = row["market_exposure"]
    assert exposure == Decimal(
        "1.750000000000000"
    )


def test_deleting_run_cascades_to_portfolio_values(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_portfolio_value(
        db_connection,
        backtest_run_id=run_id,
        trading_date=date(2024, 1, 2),
    )

    insert_portfolio_value(
        db_connection,
        backtest_run_id=run_id,
        trading_date=date(2024, 1, 3),
    )

    db_connection.execute(
        """
        DELETE FROM quant.backtest_run
        WHERE id = %(run_id)s;
        """,
        {"run_id": run_id},
    )

    row = db_connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM quant.portfolio_value
        WHERE backtest_run_id = %(run_id)s;
        """,
        {"run_id": run_id},
    ).fetchone()
    assert row is not None
    count = row["count"]
    assert count == 0


def test_portfolio_values_can_be_read_in_date_order(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    dates = [
        date(2024, 1, 4),
        date(2024, 1, 2),
        date(2024, 1, 3),
    ]

    for trading_date in dates:
        insert_portfolio_value(
            db_connection,
            backtest_run_id=run_id,
            trading_date=trading_date,
        )

    rows = db_connection.execute(
        """
        SELECT trading_date
        FROM quant.portfolio_value
        WHERE backtest_run_id = %(run_id)s
        ORDER BY trading_date;
        """,
        {"run_id": run_id},
    ).fetchall()

    assert [
        row["trading_date"]
        for row in rows
    ] == sorted(dates)