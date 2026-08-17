from __future__ import annotations

import argparse
import os
from decimal import Decimal
from typing import Any 

import psycopg
from psycopg.rows import dict_row

# from src.engine import run_single
from src.engine import run_single
from src.persistence.backtest_adapter import build_persistence_payload
from src.persistence.backtest_services import persist_completed_backtest
from strategies.buy_n_hold import BuyAndHold

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a real market backtest persistence smoke test"
    )

    parser.add_argument("--ticker", required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--exchange", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--currency", required=True)
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--end-year", type=int, required=True)


    parser.add_argument("--cash", type=Decimal, default=Decimal("10000.00"))
    return parser.parse_args()

def verify_persisted_run(
        connection:psycopg.Connection[Any],
        public_id:Any,
) -> dict_row[str, Any]:
    row = connection.execute(
        """
         SELECT
            br.id,
            br.public_id,
            br.status,
            br.strategy_name,
            br.start_date,
            br.end_date,
            br.initial_cash,
            bm.final_value,
            bm.cumulative_return,
            bm.cagr,
            bm.max_drawdown,
            bm.daily_sharpe,
            bm.calmar,
            bm.market_exposure,
            COUNT(pv.trading_date) AS portfolio_rows
        FROM 
            quant.backtest_run AS br
        JOIN 
            quant.backtest_metric AS bm
          ON 
            bm.backtest_run_id = br.id
        JOIN 
            quant.portfolio_value AS pv
          ON 
            pv.backtest_run_id = br.id
        WHERE 
            br.public_id = %(public_id)s
        GROUP BY
            br.id,
            bm.backtest_run_id;
        """,
        {"public_id":public_id},
    ).fetchone()

    if row is None: raise RuntimeError(f"Persisted backtest not found: {public_id}")

    return row


def main() -> None:
    args = parse_args()
    database_url = os.environ.get("TEST_DATABASE_URL")

    if not database_url:
        raise RuntimeError("TEST DATABASE URL NOT FOUND")

    result = run_single(
        ticker=args.ticker,
        strategy_cls=BuyAndHold,
        strategy_param={},
        start_year=args.start_year,
        end_year = args.end_year,
        cash=float(args.cash),
    )

    payload = build_persistence_payload(
        result=result,
        exchange_code=args.exchange,
        symbol=args.symbol,
        display_name=args.display_name,
        currency_code=args.currency,
        asset_type="EQUITY",
        initial_cash=args.cash,
        strategy_version="1.0.0",
        engine_version="smoke_test",
    )

    with psycopg.connect(
        database_url,
        autocommit = False,
        row_factory=dict_row,
    ) as connection:
        # start an outer transcation before the persistence service
        # the service transactin therefore a savepoint

        connection.execute("SELECT 1;")
        print("line 124")
        try:
            public_id = persist_completed_backtest(
                connection=connection,
                payload=payload
            )

            persisted = verify_persisted_run(
                connection=connection,
                public_id=public_id
            )

            print("="*20)
            print("Smoke test passed")
            print("-"*20)
            print(f"public_id:       {persisted['public_id']}")
            print(f"status:          {persisted['status']}")
            print(f"strategy:        {persisted['strategy_name']}")
            print(
                f"period:          "
                f"{persisted['start_date']} -> "
                f"{persisted['end_date']}"
            )
            print(f"initial_cash:    {persisted['initial_cash']}")
            print(f"final_value:     {persisted['final_value']}")
            print(f"return:          {persisted['cumulative_return']}")
            print(f"CAGR:            {persisted['cagr']}")
            print(f"max_drawdown:    {persisted['max_drawdown']}")
            print(f"daily_sharpe:    {persisted['daily_sharpe']}")
            print(f"calmar:          {persisted['calmar']}")
            print(f"exposure:        {persisted['market_exposure']}")
            print(f"portfolio_rows:  {persisted['portfolio_rows']}")
        finally:
            connection.rollback()


if __name__ == "__main__":
    main()