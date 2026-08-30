import os 
import psycopg
from psycopg.rows import dict_row
from src.worker.backtest_worker import run_worker

def main() -> None:
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE URL is not set"
        )

    with psycopg.connect(
        database_url,
        autocommit=False,
        row_factory=dict_row,
    ) as connection:
        run_worker(
            connection=connection,
            poll_interval_seconds=1.0,
        )


if __name__ == "__main__":
    main()