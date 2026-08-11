from datetime import date 
from decimal import Decimal
from typing import Any
from uuid import UUID 

import pytest

from psycopg import Connection 

from src.persistence.backtest_repository import(save_completed_backtest,)
from tests.integration.conftest import completed_backtest_payload


pytestmark = pytest.mark.integration


def test_save_completed_backtest_persist_full_result(
    db_connection:Connection[Any],
    unique_suffix:str,
) -> None:
    # completed_backtest_payload()
    payload = {
        "asset": {
            "exchange_code": "NYSEARCA",
            "symbol": f"SPY{unique_suffix}",
            "display_name": "SPDR S&P 500 ETF Trust",
            "currency_code": "USD",
            "asset_type": "ETF",
        },
        "run": {
            "strategy_name": "BuyAndHold",
            "strategy_version": "1.0.0",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "initial_cash": Decimal("100000.00"),
            "parameters": {},
            "engine_version": "integration-test",
        },
        "metrics": {
            "final_value": Decimal("110000.00"),
            "cumulative_return": Decimal("0.10"),
            "cagr": Decimal("0.10"),
            "max_drawdown": Decimal("0.05"),
            "daily_sharpe": Decimal("1.20"),
            "calmar": Decimal("2.00"),
            "market_exposure": Decimal("0.95"),
            "max_drawdown_duration_days": 12,
            "average_drawdown_duration_days": Decimal(
                "4.50"
            ),
        },
        "portfolio_values": [
                {
                    "trading_date": date(2024, 1, 2),
                    "portfolio_value": Decimal("100000.00"),
                    "market_exposure": Decimal("0.00"),
                    "drawdown": Decimal("0.00"),
                },
                {
                    "trading_date": date(2024, 1, 3),
                    "portfolio_value": Decimal("105000.00"),
                    "market_exposure": Decimal("0.95"),
                    "drawdown": Decimal("0.00"),
                },
                {
                    "trading_date": date(2024, 1, 4),
                    "portfolio_value": Decimal("103000.00"),
                    "market_exposure": Decimal("0.95"),
                    "drawdown": Decimal(
                        "0.019047619047619"
                    ),
                },
            ],
    }

    public_id = save_completed_backtest(connection=db_connection, payload=payload)

    assert isinstance(public_id, UUID)

    run = db_connection.execute(
        """
        SELECT 
            br.id,
            br.public_id,
            br.strategy_name,
            br.status,
            br.started_at,
            br.completed_at,
            a.exchange_code,
            a.symbol
        FROM 
            quant.backtest_run AS br
        JOIN 
            quant.asset AS a
        ON
            a.id = br.asset_id
        WHERE
            br.public_id = %(public_id)s;
        """,
        {
            "public_id":public_id
        }
    ).fetchone()

    assert run is not None 
    assert run['status'] == "COMPLETED"
    assert run['strategy_name'] == "BuyAndHold"
    assert run["exchange_code"] == "NYSEARCA"
    assert run["symbol"] == f"SPY{unique_suffix}"
    assert run["started_at"] is not None
    assert run["completed_at"] is not None

    metric = db_connection.execute(
        """
        SELECT 
            final_value,
            cagr,
            max_drawdown,
            daily_sharpe
        FROM
            quant.backtest_metric
        WHERE
            backtest_run_id = %(run_id)s;
        """,{
            "run_id":run["id"],
        }
    ).fetchone()
    
    assert metric is not None
    assert metric["final_value"] == Decimal(
        "110000.000000"
    )
    assert metric["cagr"] == Decimal(
        "0.100000000000000"
    )
    assert metric["max_drawdown"] == Decimal(
        "0.050000000000000"
    )
    assert metric["daily_sharpe"] == Decimal(
        "1.200000000000000"
    )


    portfolio_value_count = db_connection.execute(
        """
            SELECT
                COUNT(*) 
            AS
                count
            FROM
                quant.portfolio_value
            WHERE
                backtest_run_id = %(run_id)s
        """,
        {
            "run_id": run["id"],
        }
    ).fetchone()
    assert portfolio_value_count is not None
    assert portfolio_value_count["count"] == 3

