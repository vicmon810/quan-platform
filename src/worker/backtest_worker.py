from typing import Any 
from psycopg import Connection

from src.domain.backtest_job import BacktestJob
from src.engine.engine import run_single
from src.persistence.backtest_adapter import build_backtest_output
from src.persistence.backtest_repository import (complete_backtest_run, 
                                                fail_backtest_run,
                                                claim_pending_backtest)
from strategies.buy_n_hold import BuyAndHold

STRATEGIES = {"BuyAndHold": BuyAndHold}

def execute_backtest_job(
        connection: Connection[Any],
        job:BacktestJob,
) -> None:
    try:
        strategy_cls = STRATEGIES[job.strategy_name]
        result = run_single(
            ticker=job.data_symbol,
            strategy_cls=strategy_cls,
            strategy_param=job.parameters,
            start_year=job.start_date.year,
            end_year=job.end_date.year,
            cash=float(job.initial_cash),
        )

        output = build_backtest_output(result)
        
        # complete_backtest_run(
        #     connection=connection,
        #     run_id = job.run_id,
        #     metrics = output['metrics'],
        #     portfolio_values=output['portfolio_values']
        # )
    except Exception as exc:
        fail_backtest_run(
            connection=connection, 
            run_id=job.run_id,
            error_message = f"{type(exc).__name__}:{exc}")
        return
    
    with connection.transaction():
                     complete_backtest_run(
                                connection=connection,
                                run_id = job.run_id,
                                metrics = output['metrics'],
                                portfolio_values=output['portfolio_values']
                            )
    
        
def process_next_job(
        connection: Connection[Any],
) -> bool:
    with connection.transaction():
        job = claim_pending_backtest(
            connection=connection,
        )

    if job is None:
        return False
    execute_backtest_job(
        connection=connection,
        job=job
    )
    return True