from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from psycopg import Connection

from src.engine import run_single
from src.persistence.backtest_adapter import (
    build_persistence_payload,
)
from src.persistence.backtest_services import (
    persist_completed_backtest,
)
from strategies.buy_n_hold import BuyAndHold


pytestmark = [
    pytest.mark.integration,
    pytest.mark.e2e,
]


def test_backtest_runs_and_persists_to_database(
    db_connection: Connection[Any],
    e2e_test_ticker: str,
) -> None:
    """
    A deterministic market-data fixture should travel through
    the complete quant pipeline and be persisted to PostgreSQL.
    """

    result = run_single(
        ticker=e2e_test_ticker,
        strategy_cls=BuyAndHold,
        strategy_param={},
        start_year=2024,
        end_year=2025,
        cash=100_000,
    )

    payload = build_persistence_payload(
        result=result,
        exchange_code="TEST",
        display_name="E2E Test Asset",
        currency_code="USD",
        asset_type="EQUITY",
        initial_cash=Decimal("100000.00"),
        strategy_version="1.0.0",
        engine_version="e2e-test",
    )

    public_id = persist_completed_backtest(
        connection=db_connection,
        payload=payload,
    )

    assert isinstance(
        public_id,
        UUID,
    )

    run = db_connection.execute(
        """
        SELECT
            br.id,
            br.public_id,
            br.strategy_name,
            br.status,
            br.start_date,
            br.end_date,
            br.initial_cash,
            a.exchange_code,
            a.symbol
        FROM quant.backtest_run AS br
        JOIN quant.asset AS a
          ON a.id = br.asset_id
        WHERE br.public_id = %(public_id)s;
        """,
        {
            "public_id": public_id,
        },
    ).fetchone()

    assert run is not None

    assert run["public_id"] == public_id

    assert run["strategy_name"] == "BuyAndHold"

    assert run["status"] == "COMPLETED"

    assert run["exchange_code"] == "TEST"

    assert run["symbol"] == e2e_test_ticker

    assert run["initial_cash"] == Decimal(
        "100000.000000"
    )

    metric = db_connection.execute(
        """
        SELECT
            final_value,
            cumulative_return,
            cagr,
            max_drawdown,
            daily_sharpe,
            calmar,
            market_exposure
        FROM quant.backtest_metric
        WHERE backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run["id"],
        },
    ).fetchone()

    assert metric is not None

    assert metric["final_value"] > 0

    assert metric["max_drawdown"] >= 0

    assert metric["market_exposure"] >= 0

    portfolio_summary = db_connection.execute(
        """
        SELECT
            COUNT(*) AS row_count,
            MIN(trading_date) AS first_date,
            MAX(trading_date) AS last_date,
            MIN(portfolio_value) AS minimum_value
        FROM quant.portfolio_value
        WHERE backtest_run_id = %(run_id)s;
        """,
        {
            "run_id": run["id"],
        },
    ).fetchone()

    assert portfolio_summary is not None

    assert portfolio_summary[
        "row_count"
    ] > 0

    assert portfolio_summary[
        "minimum_value"
    ] > 0

    assert portfolio_summary[
        "first_date"
    ] == run["start_date"]

    assert portfolio_summary[
        "last_date"
    ] == run["end_date"]