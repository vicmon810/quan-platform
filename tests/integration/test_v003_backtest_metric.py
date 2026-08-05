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
    insert_backtest_metric,
    insert_backtest_run,
)


pytestmark = pytest.mark.integration


@pytest.fixture
def run_id(
    db_connection: Connection[Any],
    unique_suffix: str,
) -> int:
    asset_id = insert_asset(
        db_connection,
        symbol=f"METRIC{unique_suffix}",
    )

    return insert_backtest_run(
        db_connection,
        asset_id=asset_id,
    )


def test_backtest_metric_accepts_valid_values(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_backtest_metric(
        db_connection,
        backtest_run_id=run_id,
    )

    row = db_connection.execute(
        """
        SELECT *
        FROM quant.backtest_metric
        WHERE backtest_run_id = %(run_id)s;
        """,
        {"run_id": run_id},
    ).fetchone()

    assert row is not None
    assert row["final_value"] == Decimal(
        "150000.000000"
    )
    assert row["max_drawdown"] == Decimal(
        "0.200000000000000"
    )


def test_backtest_metric_allows_null_sharpe_and_calmar(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_backtest_metric(
        db_connection,
        backtest_run_id=run_id,
        daily_sharpe=None,
        calmar=None,
    )

    row = db_connection.execute(
        """
        SELECT daily_sharpe, calmar
        FROM quant.backtest_metric
        WHERE backtest_run_id = %(run_id)s;
        """,
        {"run_id": run_id},
    ).fetchone()

    assert row is not None
    assert row["daily_sharpe"] is None
    assert row["calmar"] is None


def test_backtest_metric_is_one_to_one_with_run(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_backtest_metric(
        db_connection,
        backtest_run_id=run_id,
    )

    with pytest.raises(
        UniqueViolation
    ) as exception:
        insert_backtest_metric(
            db_connection,
            backtest_run_id=run_id,
        )

    assert (
        exception.value.diag.constraint_name
        == "pk_backtest_metric"
    )


def test_backtest_metric_rejects_missing_run(
    db_connection: Connection[Any],
) -> None:
    with pytest.raises(
        ForeignKeyViolation
    ):
        insert_backtest_metric(
            db_connection,
            backtest_run_id=9_999_999_999,
        )


@pytest.mark.parametrize(
    ("overrides", "constraint_name"),
    [
        (
            {"final_value": Decimal("0")},
            "ck_backtest_metric_final_value",
        ),
        (
            {"final_value": Decimal("NaN")},
            "ck_backtest_metric_final_value",
        ),
        (
            {
                "cumulative_return": Decimal(
                    "-1"
                )
            },
            "ck_backtest_metric_cumulative_return",
        ),
        (
            {
                "cumulative_return": Decimal(
                    "NaN"
                )
            },
            "ck_backtest_metric_cumulative_return",
        ),
        (
            {"cagr": Decimal("-1")},
            "ck_backtest_metric_cagr",
        ),
        (
            {"cagr": Decimal("NaN")},
            "ck_backtest_metric_cagr",
        ),
        (
            {"max_drawdown": Decimal("-0.01")},
            "ck_backtest_metric_max_drawdown",
        ),
        (
            {"max_drawdown": Decimal("1.01")},
            "ck_backtest_metric_max_drawdown",
        ),
        (
            {"max_drawdown": Decimal("NaN")},
            "ck_backtest_metric_max_drawdown",
        ),
        (
            {"daily_sharpe": Decimal("NaN")},
            "ck_backtest_metric_daily_sharpe",
        ),
        (
            {"calmar": Decimal("NaN")},
            "ck_backtest_metric_calmar",
        ),
        (
            {
                "market_exposure": Decimal(
                    "-0.01"
                )
            },
            "ck_backtest_metric_market_exposure",
        ),
        (
            {
                "market_exposure": Decimal(
                    "NaN"
                )
            },
            "ck_backtest_metric_market_exposure",
        ),

        (
            {
                "average_drawdown_duration_days": -1
            },
            "ck_backtest_metric_average_duration",
        ),
        (
            {
                "average_drawdown_duration_days":
                    Decimal("NaN")
            },
            "ck_backtest_metric_average_duration",
        ),
    ],
)
def test_backtest_metric_rejects_invalid_values(
    db_connection: Connection[Any],
    run_id: int,
    overrides: dict[str, object],
    constraint_name: str,
) -> None:
    arguments: dict[str, object] = {
        "backtest_run_id": run_id,
    }

    arguments.update(overrides)

    with pytest.raises(
        CheckViolation
    ) as exception:
        insert_backtest_metric(
            db_connection,
            **arguments,
        )

    assert (
        exception.value.diag.constraint_name
        == constraint_name
    )


def test_backtest_metric_allows_leveraged_exposure(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_backtest_metric(
        db_connection,
        backtest_run_id=run_id,
        market_exposure=Decimal("1.50"),
    )

    exposure = db_connection.execute(
        """
        SELECT market_exposure
        FROM quant.backtest_metric
        WHERE backtest_run_id = %(run_id)s;
        """,
        {"run_id": run_id},
    ).fetchone()["market_exposure"]

    assert exposure == Decimal(
        "1.500000000000000"
    )


def test_deleting_run_cascades_to_metric(
    db_connection: Connection[Any],
    run_id: int,
) -> None:
    insert_backtest_metric(
        db_connection,
        backtest_run_id=run_id,
    )

    db_connection.execute(
        """
        DELETE FROM quant.backtest_run
        WHERE id = %(run_id)s;
        """,
        {"run_id": run_id},
    )

    count = db_connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM quant.backtest_metric
        WHERE backtest_run_id = %(run_id)s;
        """,
        {"run_id": run_id},
    ).fetchone()["count"]

    assert count == 0