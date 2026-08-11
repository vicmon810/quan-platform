from copy import deepcopy
from decimal import Decimal
from typing import Any 

import pytest 
from psycopg import Connection
from psycopg.errors import CheckViolation

from src.persistence.backtest_services import(
    persist_completed_backtest,
)

def test_persist_completed_backtest_rolls_back_all_change_on_failure(
        db_connection: Connection[Any],
        completed_backtest_payload: dict[str, Any],
) -> None: 
    """
    A failed backtest persistence operation must bu atomic

    IF any porfolio value is invalid, asset, run, metrics,
    and profolio values created by that operation must all
    be rolled back
    """

    payload = deepcopy(
        completed_backtest_payload
    )

    asset = payload["asset"]

    payload["run"]["engine_version"] = (
        "rollback-interation-test"
    )

    ## First two row are valid
    ## thrid row must violate V004
    payload["portfolio_values"][2]["portfolio_value"] = Decimal("-1.00")  

    # establish an outer transaction owned by the test 
    #persist_completed_backtest will later create its own
    #transaction boundary, which becomes a savepoint
    #when nested inside this transaction 
    db_connection.execute("SELECT 1;")

    with pytest.raises(
        CheckViolation
    ) as exception:
        persist_completed_backtest(
            connection = db_connection,
            payload = payload
        )

    assert(exception.value.diag.constraint_name == "ck_portfolio_value_positive")

    # The connection must be still be usable here
    asset_count = db_connection.execute(
        """
            SELECT 
                COUNT(*) as count
            FROM 
                quant.asset
            WHERE
                exchange_code = %(exchange_code)s
            AND
                symbol = %(symbol)s
            
        """,
        {
            "exchange_code":asset["exchange_code"],
            "symbol": asset["symbol"] 
        },
    ).fetchone()

    assert (exception.value.diag.constraint_name 
            ==  "ck_portfolio_value_positive")

    assert asset_count is not None
    assert asset_count["count"] == 0

    run_count = db_connection.execute(
        """
            SELECT 
                COUNT(*) as count
            FROM 
                quant.backtest_run
            WHERE
                engine_version =
                'rollback-integration-test';
        """
    ).fetchone()

    assert run_count is not None
    assert run_count["count"] == 0

    metric_count = db_connection.execute(
        """
            SELECT 
                COUNT(*) as count 
            from 
                quant.backtest_metric AS bm 
            JOIN
                quant.backtest_run as br 
            ON 
                br.id = bm.backtest_run_id
            WHERE
                br.engine_version =
                'rollback-integration-test';
        """
    ).fetchone()

    assert metric_count is not None 
    assert metric_count["count"] == 0 

    portfolio_value_count =(
        db_connection.execute(
            """
                SELECT 
                    COUNT(*) AS count
                FROM
                    quant.portfolio_value AS pv 
                JOIN
                    quant.backtest_run AS br 
                ON 
                    br.id = pv.backtest_run_id
                WHERE
                    br.engine_version ='rollback-integration-test';
            """
        ).fetchone()
    )

    assert portfolio_value_count is not None
    assert portfolio_value_count["count"] == 0