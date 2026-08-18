from datetime import date,datetime
from uuid import UUID 
from typing import Any 

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from collections.abc import Mapping


def save_completed_backtest(
        connection: Connection[Any],
        payload: dict[str, Any],
) -> UUID:
    """
    Persist one completed backtest using the caller transation
    this function does not commit or roll back, transaction ownership
    belongs to the service or caller
    """
    asset = payload["asset"]
    run = payload["run"]
    metrics = payload["metrics"]
    portfolio_values = payload["portfolio_values"]

    asset_id = _upsert_asset(
        connection = connection,
        asset = asset 
    )

    run_id, public_id = _insert_pending_run(
        connection=connection,
        asset_id = asset_id,
        run = run,
    )

    _mark_run_running(
        connection = connection,
        run_id = run_id, 
    )

    _insert_backtest_metric(
        connection = connection,
        run_id = run_id,
        metrics = metrics
    )
    _insert_portfolio_values(
        connection=connection,
        run_id=run_id,
        portfolio_values=portfolio_values
    )
    _mark_run_completed(
        connection = connection,
        run_id = run_id,
    )

    return public_id


def _upsert_asset(
        connection:Connection[Any],
        asset: Mapping[str, Any]
) -> int:
    """
    Insert and asset or update its mutable metadata
    the cannoical identiry is exchane_code + symbol
    """

    with connection.cursor(
        row_factory=dict_row
    ) as cursor:
        cursor.execute(
        """
            INSERT INTO
                quant.asset 
                (
                    exchange_code,
                    symbol,
                    data_symbol,
                    display_name,
                    currency_code,
                    asset_type
                )
            VALUES
                (
                    %(exchange_code)s,
                    %(symbol)s,
                    %(data_symbol)s,
                    %(display_name)s,
                    %(currency_code)s,
                    %(asset_type)s
                )
            ON CONFLICT
                (
                    exchange_code,
                    symbol
                )
            DO UPDATE SET 
                data_symbol = EXCLUDED.data_symbol,
                display_name = EXCLUDED.display_name,
                currency_code = EXCLUDED.currency_code,
                asset_type = EXCLUDED.asset_type
            RETURNING id;
        """,
        {
            "exchange_code": asset["exchange_code"],
            "symbol": asset["symbol"],
            "data_symbol": asset["data_symbol"],
            "display_name": asset["display_name"],
            "currency_code": asset["currency_code"],
            "asset_type":asset["asset_type"],
        },
        )

        row = cursor.fetchone()   

    if row is None:
        raise RuntimeError("asset upsert did not return an id")

    return int(row["id"])


def _insert_pending_run(
        connection: Connection[Any],
        asset_id: int,
        run: Mapping[str,Any],
) -> tuple[int, UUID]:
    """Create a PENDING bactest run"""

    with connection.cursor(
        row_factory=dict_row 
    )as cursor:
        cursor.execute(
            """
                INSERT INTO 
                    quant.backtest_run
                    (
                        asset_id,
                        strategy_name,
                        strategy_version,
                        start_date,
                        end_date,
                        initial_cash,
                        parameters,
                        engine_version,
                        status
                    )
                VALUES
                (
                    %(asset_id)s,
                    %(strategy_name)s,
                    %(strategy_version)s,
                    %(start_date)s,
                    %(end_date)s,
                    %(initial_cash)s,
                    %(parameters)s,
                    %(engine_version)s,
                    'PENDING'
                )
                RETURNING
                    id,
                    public_id;
            """,
            {
                "asset_id": asset_id,
                "strategy_name": run[
                    "strategy_name"
                ],
                "strategy_version": run[
                    "strategy_version"
                ],
                "start_date": run["start_date"],
                "end_date": run["end_date"],
                "initial_cash": run[
                    "initial_cash"
                ],
                "parameters": Jsonb(
                    run["parameters"]
                ),
                "engine_version": run.get(
                    "engine_version"
                ),
            }
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("backtest run insert did not return an id")

    return(int(row['id']), row['public_id'])


def _mark_run_running(
        connection: Connection[Any],
        run_id: int,
) -> None: 
    """transition a PENDING run to RUNNING"""

    with connection.cursor(
        row_factory=dict_row
    ) as cursor:
        cursor.execute(
            """
                UPDATE 
                    quant.backtest_run
                SET
                    status = 'RUNNING',
                    started_at = clock_timestamp()
                WHERE
                    id = %(run_id)s
                AND 
                    Status = 'PENDING'
                RETURNING id;
            """,
            {
                "run_id":run_id
            },
        )
        row = cursor.fetchone()

    if row is None:
        raise RuntimeError("backtest run could not transition from PENDING to RUNNING")


def _insert_backtest_metric(
        connection:Connection[Any],
        run_id:int,
        metrics:Mapping[str,Any]
) -> None:
    """
    Persist the summary metrics for one run 
    """

    connection.execute(
        """
            INSERT INTO 
                quant.backtest_metric
                (
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
            VALUES
            (
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
            "backtest_run_id": run_id,
            "final_value": metrics[
                "final_value"
            ],
            "cumulative_return": metrics[
                "cumulative_return"
            ],
            "cagr": metrics["cagr"],
            "max_drawdown": metrics[
                "max_drawdown"
            ],
            "daily_sharpe": metrics[
                "daily_sharpe"
            ],
            "calmar": metrics["calmar"],
            "market_exposure": metrics[
                "market_exposure"
            ],
            "max_duration": metrics[
                "max_drawdown_duration_days"
            ],
            "average_duration": metrics[
                "average_drawdown_duration_days"
            ],
        }
    )


def _insert_portfolio_values(
        connection:Connection[Any],
        run_id:int,
        portfolio_values:list[Mapping[str,Any]],
) -> None:
    """Bulk inset daily portfolio observation"""

    rows =[
        {
            "backtest_run_id": run_id,
            "trading_date": record["trading_date"],
            "portfolio_value":record["portfolio_value"],
            "market_exposure": record["market_exposure"],
            "drawdown": record["drawdown"],
        }
        for record in portfolio_values
    ]

    with connection.cursor() as cusor:
        cusor.executemany(
            """
                INSERT INTO 
                    quant.portfolio_value
                        (
                            backtest_run_id,
                            trading_date,
                            portfolio_value,
                            market_exposure,
                            drawdown
                        )
                VALUES
                    (
                        %(backtest_run_id)s,
                        %(trading_date)s,
                        %(portfolio_value)s,
                        %(market_exposure)s,
                        %(drawdown)s
                    )
            """,
            rows,
        )

def _mark_run_completed(
        connection:Connection[Any],
        run_id:int,
) -> None:
    """transition a RUNNING to COMPLETED"""

    with connection.cursor(
        row_factory=dict_row
    ) as cursor:
        cursor.execute(
            """
            UPDATE 
                quant.backtest_run
            SET
                status = 'COMPLETED',
                completed_at = clock_timestamp()
            WHERE
                 id = %(run_id)s
            AND 
                status = 'RUNNING'
            RETURNING 
                id;
            """,
            {
                "run_id":run_id
            },
        )
        row = cursor.fetchone()
    if row is None:
        raise RuntimeError("backtest run could not transtition from RUNNING to COMPLETED")


def claim_pending_backtest(
        connection : Connection[Any],
) -> None| dict[str, Any]:
    """
    claim the oldest pending backtest job
    the selected job is locked and transitioned from PENDING
    to RUNNING atomically. locked jobs are skipped so mutiple
    workers can safely claim different jobs
    """
    
    row = connection.execute(
        """
        WITH 
            candidate
        AS(
        SELECT
            id
        FROM 
            quant.backtest_run
        WHERE
            status = 'PENDING'
        ORDER BY 
            created_at ASC,
            id ASC
        FOR UPDATE SKIP LOCKED LIMIT 1
        ),
        claimed AS(
            UPDATE 
                quant.backtest_run as br 
            SET 
                status = 'RUNNING',
                started_at = CURRENT_TIMESTAMP
            FROM
                candidate
            WHERE
                br.id = candidate.id
            RETURNING
                br.id AS run_id,
                br.public_id,
                br.asset_id,
                br.strategy_name,
                br.parameters,
                br.start_date,
                br.end_date,
                br.initial_cash
        )
        SELECT 
            claimed.run_id,
            claimed.public_id,
            asset.data_symbol,
            claimed.strategy_name,
            claimed.parameters,
            claimed.start_date,
            claimed.end_date,
            claimed.initial_cash
        FROM
            claimed
        JOIN
            quant.asset 
        AS 
            asset
        ON
            asset.id = claimed.asset_id;
        """
    ).fetchone()

    return row