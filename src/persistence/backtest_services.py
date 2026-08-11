from collections.abc import Mapping
from typing import Any 
from uuid import UUID 

from psycopg import Connection

from src.persistence.backtest_repository import(
    save_completed_backtest,
)

def persist_completed_backtest(connection:Connection[Any], payload:Mapping[str,Any],) -> UUID:
    """
        persist one completed backtest atomically
        all database changes successd together or 
        are rolled back together when an expection
        occurs
    """

    with connection.transaction():
        return save_completed_backtest(
            connection=connection,
            payload=payload
        )