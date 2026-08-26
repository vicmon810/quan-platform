from datetime import date 
from decimal import Decimal
from typing import Any 
from uuid import uuid4 

import os
import pytest 
import psycopg
from psycopg import Connection 

from src.domain.backtest_job import BacktestJob
from src.worker import backtest_worker
# from psycopg.pg import TransactionStatus
from psycopg.pq import TransactionStatus
from psycopg.rows import dict_row


pytestmark = [
    pytest.mark.integration,
    pytest.mark.e2e,
]

def test_execute_backtest_job_completes_existing_run(
        db_connection: Connection[Any],
        e2e_test_ticker: str,
) -> None: 
    suffix = uuid4().hex[:8].upper()
    symbol = f"E2E{suffix}"

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
        VALUES (
            'TEST',
            %(symbol)s,
            %(data_symbol)s,
            'Worker E2E Asset',
            'USD',
            'EQUITY'
        )
        RETURNING
            id;
        """,
        {
            "symbol": symbol,
            "data_symbol": e2e_test_ticker
        },
    ).fetchone()

    assert asset is not None 

    run = db_connection.execute(
        """
        INSERT INTO quant.backtest_run(
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
        VALUES(
            %(asset_id)s,
            'BuyAndHold',
            '1.0.0',
            DATE '2024-01-01',
            DATE '2025-01-01',
            10000,
            '{}'::jsonb,
            'RUNNING',
            CURRENT_TIMESTAMP
        )
        RETURNING
            id,
            public_id;
        """,
        {
            "asset_id": asset['id'],
        }
    ).fetchone()

    assert run is not None

    job = BacktestJob(
        run_id=run['id'],
        public_id=run['public_id'],
        data_symbol=e2e_test_ticker,
        strategy_name='BuyAndHold',
        parameters={},
        start_date=date(2024,1,1),
        end_date=date(2025,1,1),
        initial_cash=Decimal("10000.00")
    )

    backtest_worker.execute_backtest_job(
        connection = db_connection,
        job = job,
    )

    saved_run = db_connection.execute(
        """
        SELECT
            status,
            completed_at,
            error_message
        FROM
            quant.backtest_run
        WHERE
            id = %(run_id)s;
        """,
        {
            "run_id": run['id'],
        }
    ).fetchone()

    assert saved_run is not None 
    assert saved_run['status'] == "COMPLETED"
    assert saved_run['completed_at'] is not None
    assert saved_run['error_message'] is None

    metric = db_connection.execute(
        """
        SELECT 
            final_value,
            cumulative_return,
            max_drawdown
        FROM
            quant.backtest_metric
        WHERE
            backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run['id'],
        }
    ).fetchone()

    assert metric is not None
    assert metric["final_value"] > 0
    assert metric["max_drawdown"] >=0

    portfolio = db_connection.execute(
        """
        SELECT 
            COUNT(*) AS count
        FROM
            quant.portfolio_value
        WHERE
            backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run['id']
        }
    ).fetchone()

    assert portfolio is not None 
    assert portfolio['count'] > 0

    run_count = db_connection.execute(
        """
        SELECT 
            COUNT(*) AS count
        FROM
            quant.backtest_run
        WHERE
            asset_id = %(asset_id)s;
        """,
        {
            "asset_id": asset['id'],
        }
    ).fetchone()
    assert run_count is not None 
    assert run_count['count'] == 1



def test_execute_backtest_job_marks_run_failed_when_execution_fails(
        db_connection:Connection[Any],
) -> None:
    suffix = uuid4().hex[:8].upper()
    symbol = f"FAIL{suffix}"
    missing_data_symbol = f"MISSING_{suffix}"

    asset = db_connection.execute(
        """
        INSERT INTO 
            quant.asset (
                exchange_code,
                symbol,
                data_symbol,
                display_name,
                currency_code,
                asset_type
            )
        VALUES (
            'TEST',
            %(symbol)s,
            %(data_symbol)s,
            'Worker failure test asset',
            'USD',
            'EQUITY'
        )
        RETURNING id;
        """,{
            "symbol": symbol,
            "data_symbol": missing_data_symbol
        }
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
                DATE '2024-01-01',
                DATE '2025-01-01',
                10000,
                '{}'::jsonb,
                'RUNNING',
                CURRENT_TIMESTAMP
            )
            RETURNING
                id,
                public_id;
        """,
        {
            "asset_id": asset['id']
        }
    ).fetchone()

    assert run is not None 

    job = BacktestJob(
        run_id=run['id'],
        public_id=run['public_id'],
        data_symbol=missing_data_symbol,
        strategy_name='BuyAndHold',
        parameters={},
        start_date=date(2024,1,1),
        end_date=date(2025,1,1),
        initial_cash=Decimal("10000.00")
    )

    backtest_worker.execute_backtest_job(
        connection=db_connection,
        job=job
    )

    saved_run = db_connection.execute(
        """
        SELECT 
            status,
            completed_at,
            error_message
        FROM
            quant.backtest_run
        WHERE
            id = %(run_id)s;
        """,
        {
            "run_id": run['id']
        }
    ).fetchone()

    assert saved_run is not None 

    assert saved_run['status']=="FAILED"
    assert saved_run['completed_at'] is not None 
    assert saved_run['error_message'] is not None 
    assert 'Data file not found' in saved_run['error_message']

    metric_count = db_connection.execute(
        """
        SELECT 
            COUNT(*) AS count
        FROM 
            quant.backtest_metric
        WHERE
            backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run['id']
        },
    ).fetchone()

    assert metric_count is not None 
    assert metric_count["count"] == 0

    portfolio_count = db_connection.execute(
        """
        SELECT 
            COUNT(*) AS count
        FROM
            quant.portfolio_value
        WHERE
            backtest_run_id = %(run_id)s
        """,
        {
            "run_id": run['id']
        }
    ).fetchone()

    assert portfolio_count is not None
    assert portfolio_count["count"] == 0


def test_process_next_job_claims_and_completes_pending_backtest(
        db_connection: Connection[Any],
        e2e_test_ticker:str,
) -> None:
    suffix = uuid4().hex[:8].upper()
    symbol = f"PROCESS{suffix}"

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
            'TEST',
            %(symbol)s,
            %(data_symbol)s,
            'Process Job Test Asset',
            'USD',
            'EQUITY'
        )
        RETURNING
            id;
        """,
        {
            "symbol": symbol,
            "data_symbol": e2e_test_ticker
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
                status
            )
        VALUES(
            %(asset_id)s,
            'BuyAndHold',
            '1.0.0',
            DATE '2024-01-01',
            DATE '2025-01-01',
            10000,
            '{}'::jsonb,
            'PENDING'
        )
        RETURNING
            id, 
            public_id;
        """,
        {
            "asset_id":asset['id']
        },
    ).fetchone()
    assert run is not None 

    processed = backtest_worker.process_next_job(
        connection = db_connection
    )

    assert processed is True 

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
            id = %(run_id)s
        """,
        {
            "run_id": run['id']
        },
    ).fetchone()

    assert saved_run is not None 

    assert saved_run['status'] == 'COMPLETED'
    assert saved_run['started_at'] is not None 
    assert saved_run['completed_at'] is not None 
    assert saved_run['error_message'] is None 

    metric_count = db_connection.execute(
        """
        SELECT 
            COUNT(*) AS count
        FROM
            quant.backtest_metric
        WHERE
            backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run['id']
        }
    ).fetchone()

    assert metric_count is not None 
    assert metric_count["count"] == 1

    portfolio_count = db_connection.execute(
        """
        SELECT 
            COUNT(*) AS count
        FROM 
            quant.portfolio_value
        WHERE
            backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run['id']
        },
    ).fetchone()

    assert portfolio_count is not None
    assert portfolio_count['count'] > 0


def test_process_next_job_returns_false_when_queue_is_empty(
        db_connection:Connection[Any],
) -> None: 
    processed = backtest_worker.process_next_job(
        connection=db_connection
    )

    assert processed is False


def test_process_next_job_commits_claim_before_engine_execution(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_url = os.environ["TEST_DATABASE_URL"]

    setup_connectin = psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row
    )

    worker_connection = psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row
    )

    asset_id: int | None = None 
    run_id: int | None = None 

    try :
        suffix = uuid4().hex[:8].upper()
        symbol = f"TX{suffix}"

        asset = setup_connectin.execute(
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
                'TEST',
                %(symbol)s,
                %(data_symbol)s,
                'Transaction Boundary Test Asset',
                'USD',
                'EQUITY'
            )
            RETURNING 
                id;
            """,
            {
                "symbol": symbol,
                "data_symbol": 'TX_BOUNDARY_TEST'
            },
        ).fetchone()

        assert asset is not None 
        asset_id = asset['id']

        run = setup_connectin.execute(
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
                    status
                )
            VALUES (
                %(asset_id)s,
                'BuyAndHold',
                '1.0.0',
                DATE '2024-01-01',
                DATE '2025-01-01',
                10000,
                '{}'::jsonb,
                'PENDING'
            )
            RETURNING
                id;
            """,
            {
                "asset_id": asset_id
            },
        ).fetchone()

        assert run is not None 
        run_id = run['id']

        setup_connectin.commit()

        def fake_run_single(*arg, **kwargs):
            assert(
                worker_connection.info.transaction_status 
                == TransactionStatus.IDLE
            )
            raise RuntimeError("stop after transaction assertion")
        monkeypatch.setattr(
            backtest_worker,
            "run_single",
            fake_run_single,
        )

        processed = backtest_worker.process_next_job(
            connection=worker_connection,
        )
        assert processed is True
    finally:
        worker_connection.rollback()
        worker_connection.close()

        if run_id is not None:
            setup_connectin.execute(
                """
                DELETE FROM 
                    quant.backtest_run
                WHERE
                    id = %(run_id)s;
                """,
                {
                    "run_id":run_id,
                },
            )

        if asset_id is not None:
            setup_connectin.execute(
                """
                DELETE FROM
                    quant.asset
                WHERE
                    id = %(asset_id)s;
                """,
                {
                    "asset_id": asset_id,
                },
            )

        setup_connectin.commit()
        setup_connectin.close()


def test_execute_backtest_job_persists_result_inside_transaction(
        db_connection: Connection[Any],
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_rul = os.environ["TEST_DATABASE_URL"]
    connection = psycopg.connect(
        database_rul,
        autocommit=False,
        row_factory=dict_row
    )
    try:

        assert(
            connection.info.transaction_status
            == TransactionStatus.IDLE
        )

        job = BacktestJob(
            run_id=123,
            public_id=uuid4(),
            data_symbol="TEST",
            strategy_name="BuyAndHold",
            parameters={},
            start_date=date(2024,1,1),
            end_date=date(2025,1,1),
            initial_cash=Decimal("10000.00")
        )

        monkeypatch.setattr(
            backtest_worker,
            'run_single',
            lambda **kwargs: {
                "ticker": "TEST",
                "strategy": "BuyAndHold"
            },
        )

        monkeypatch.setattr(
            backtest_worker,
            'build_backtest_output',
            lambda result:{
                "metrics": {},
                "portfolio_values": [],
            },
        )

        monkeypatch.setattr(
            backtest_worker,
            'run_single',
            lambda **kwargs: fake_result
        )

        monkeypatch.setattr(
            backtest_worker,
            'build_backtest_output',
            lambda result:fake_output
        )

        def fake_complete_backtest_run(**kwargs):
            assert(db_connection.info.transaction_status
                == TransactionStatus.INTRANS)

        monkeypatch.setattr(
            backtest_worker,
            'complete_backtest_run',
            fake_complete_backtest_run
        )

        backtest_worker.execute_backtest_job(
            connection=db_connection,
            job=job
        )

        assert(
            connection.info.transaction_status
            == TransactionStatus.IDLE
        )
    finally:
        connection.rollback()
        connection.close()