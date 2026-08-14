from datetime import date 
from decimal import Decimal 

from src.persistence import backtest_adapter

def test_build_persistence_payload_maps_asset_and_run_metadate():
    """
    adapter should map engine result and explict asset metadata
    into the persistence asset and run structures.
    """

    result = {
        "ticker":"BHP",
        "strategy":"MovingAverageCross",
        "start_year":2024,
        "end_year":2024,
        "final_value":110000.00,

        #engine/report output

        "trades":{"total":5,},

        "singal_history": None,

        "porfolio_values":[
            {
                "date":date(2024,1,2),
                "value":100000.00,
                "exposure": 0.0
            },
            {
                "date":date(2024,6,3),
                "value":100500.00,
                "exposure":0.95,
            },
            {
                "date":date(2024,12,31),
                "value":110000.00,
                "exposure":0.95,
            },
        ],

        #performance metrics
        "cumulative_return":0.10,
        "cagr":0.10,
        "max_drawdown":0.05,
        "daily_sharpe":1.20,
        "market_exposure": 0.80,
        "max_drawdown_duration_days":12,
        "average_drawdown_duration_days":4.5,
    }

    payload = (
        backtest_adapter.build_persistence_payload(
            result = result,
            exchange_code = "ASX",
            display_name = "BHP Group",
            currency_code = "AUD",
            asset_type = "EQUITY",
            initial_cash = Decimal("100000.00"),
            strategy_version = "1.0.0",
            engine_version = "integration-test",
        )
    )

    assert payload["asset"] == {
        "exchange_code": "ASX",
        "symbol": "BHP",
        "display_name": "AUD",
        "asset_type": "EQUITY",
    }

    assert payload["run"] == {
        "strategy_name": "MovingAverageCross",
        "strategy_version": "1.0.0",
        "start_date":date(2024,1,2),
        "end_date":date(2024,12,31),
        "asset_type":"EQUITY",

        "initial_cash": Decimal("100000.00"),

        "parameters": {
            "fast": 20,
            "slow": 50,
        },
        "engine_version":"integration-test"
    }

    