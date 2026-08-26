from datetime import date, datetime
from decimal import Decimal
from typing import Any 
import os
import pytest
import psycopg
from psycopg import Connection
from src.persistence import backtest_repository
from psycopg.rows import dict_row
from uuid import uuid4
from src.domain.backtest_job import BacktestJob

unique_suffix = uuid4().hex[:8].upper()
symbol = f"WT{unique_suffix}"
data_symbol = f"{symbol}.AX"

def test_claim_pending_backtest_claims_oldest_pending_job(
    
        db_connection: Connection[Any],
) -> None:
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
            'BHP',
            'BHP.AX',
            'BHP Group',
            'AUD',
            'EQUITY'
        )
        RETURNING
            id;
        """
    ).fetchone()

    assert asset is not None
    asset_id = asset['id']

    oldest = db_connection.execute(
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
                created_at
            )
        VALUES(
            %(asset_id)s,
            'BuyAndHold',
            '1.0.0',
            %(start_date)s,
            %(end_date)s,
            %(initial_cash)s,
            '{}'::jsonb,
            'PENDING',
            %(created_at)s
        )
        RETURNING
            id,
            public_id;
        """,
        {
            "asset_id": asset_id,
            "start_date": date(2020,1,1),
            "end_date": date(2025,1,1),
            "initial_cash": Decimal("10000.00"),
            "created_at":datetime(2026, 1, 1, 9, 0, 0),
        },
    ).fetchone()

    newest = db_connection.execute(
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
                created_at
            )
        VALUES(
            %(asset_id)s,
            'BuyAndHold',
            '1.0.0',
            %(start_date)s,
            %(end_date)s,
            %(initial_cash)s,
            '{}'::jsonb,
            'PENDING',
            %(created_at)s
        )
        RETURNING
            id,
            public_id
        """,
        {
            "asset_id":asset_id,
            "start_date":date(2021,1,1),
            "end_date": date(2025,1,1),
            "initial_cash": Decimal("20000.00"),
            "created_at": datetime(2026,1,1,10,0,0),
        },
    ).fetchone()

    assert oldest is not None
    assert newest is not None 

    job = backtest_repository.claim_pending_backtest(
        connection = db_connection,
    )

    assert job is not None 

    assert job.run_id == oldest['id']
    assert job.public_id == oldest["public_id"]
    assert job.data_symbol == "BHP.AX"
    assert job.strategy_name == "BuyAndHold"
    assert job.parameters == {}
    assert job.start_date == date(2020, 1, 1)
    assert job.end_date == date(2025, 1, 1)
    assert job.initial_cash == Decimal("10000.000000")

    statuses = db_connection.execute(
        """
        SELECT
            id,
            status,
            started_at
        FROM quant.backtest_run
        WHERE id IN (
            %(oldest_id)s,
            %(newest_id)s
        )
        ORDER BY id;
        """,
        {
            "oldest_id": oldest["id"],
            "newest_id": newest["id"],
        },
    ).fetchall()

    by_id = {
        row["id"]: row
        for row in statuses
    }

    assert by_id[oldest["id"]]["status"] == "RUNNING"
    assert by_id[oldest["id"]]["started_at"] is not None

    assert by_id[newest["id"]]["status"] == "PENDING"
    assert by_id[newest["id"]]["started_at"] is None



def test_claim_pending_backtest_returns_none_when_no_pending_jobs(
        db_connection: Connection[Any],
) -> None:
    job = backtest_repository.claim_pending_backtest(
        connection = db_connection,
    )
    assert job is None


def test_claim_pending_backtest_skips_job_locked_by_another_worker() -> None:
    database_url = os.environ["TEST_DATABASE_URL"]

    setup_connection = psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row,
    )   

    worker_a = psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row,
    )

    worker_b = psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row,
    )

    created_run_ids: list[int] = []
    asset_id: int | None = None 

    try:
        asset = setup_connection.execute(
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
                'worker test asset',
                'AUD',
                'EQUITY'
            )
            RETURNING
                id;
            """,
            {
                "symbol":symbol,
                "data_symbol":data_symbol,
            }
        ).fetchone()

        assert asset is not None 
        asset_id = asset['id']

        oldest = setup_connection.execute(
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
                    created_at
                )
            VALUES (
                %(asset_id)s,
                'BuyAndHold',
                '1.0.0',
                DATE '2020-01-01',
                DATE '2025-01-01',
                10000,
                '{}'::jsonb,
                'PENDING',
                TIMESTAMP '2026-01-01 09:00:00'
            )
            RETURNING 
                id;
            """,
            {
                'asset_id': asset_id,
            },
        ).fetchone()

        second = setup_connection.execute(
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
                created_at
            )
            VALUES (
                %(asset_id)s,
                'BuyAndHold',
                '1.0.0',
                DATE '2020-01-01',
                DATE '2025-01-01',
                10000,
                '{}'::jsonb,
                'PENDING',
                TIMESTAMP '2026-01-01 10:00:00'
            )
            RETURNING id;
            """,
            {
                "asset_id": asset_id,
            },
        ).fetchone()

        assert oldest is not None
        assert second is not None 

        created_run_ids.extend(
            [
                oldest['id'],
                second['id'],
            ]
        )
        # import 
        # other postgreSQL connectinos cannot see the setup rows
        # until they are commited

        setup_connection.commit()

        job_a = backtest_repository.claim_pending_backtest(
            connection = worker_a,
        )

        job_b = backtest_repository.claim_pending_backtest(
            connection = worker_b,
        )

        assert job_a is not None
        assert job_b is not None 

        assert job_a.run_id == oldest['id']
        assert job_b.run_id == second['id']

        assert job_b.run_id != job_a.run_id
        
    finally:
        worker_a.rollback()
        worker_b.rollback()

        worker_a.close()
        worker_b.close()

        #clean up 
        if created_run_ids:
            setup_connection.execute(
                """
                DELETE FROM
                    quant.backtest_run
                WHERE
                    id = ANY(%(run_id)s);
                """,
                {
                    "run_id":created_run_ids,
                },
            )

        if asset_id is not None:
            setup_connection.execute(
                """
                DELETE FROM
                    quant.asset
                WHERE
                    id = %(asset_id)s;
                """,
                {
                    "asset_id": asset_id,
                }
            )

        setup_connection.commit()
        setup_connection.close()