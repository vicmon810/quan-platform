from dataclasses import dataclass
from datetime import date 
from decimal import Decimal
from typing import Any 
from uuid import UUID 

@dataclass(frozen=True)

class BacktestJob:
    run_id:int
    public_id: UUID 
    data_symbol:str
    strategy_name: str
    parameters: dict[str, Any]
    start_date: date 
    end_date: date 
    initial_cash: Decimal