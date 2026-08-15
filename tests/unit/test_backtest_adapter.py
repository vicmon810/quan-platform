from copy import deepcopy
from datetime import date
from decimal import Decimal
import sys
from src.persistence import backtest_adapter


def test_build_persistence_payload_maps_asset() -> None:
    """
    Adapter should map engine result and explicit asset metadata
    into the persistence asset and run structures.
    """

    result = {
        "ticker": "BHP",
        "strategy": "MovingAverageCross",
        "start_year": 2024,
        "end_year": 2024,
        "final_value": 110000.0,

        # Strategy-specific parameters
        "fast": 20,
        "slow": 50,

        # Engine/reporting output
        "trades": {
            "total": 5,
        },
        "signal_history": None,

        "portfolio_values": [
            {
                "date": date(2024, 1, 2),
                "value": 100000.0,
                "exposure": 0.0,
            },
            {
                "date": date(2024, 6, 3),
                "value": 105000.0,
                "exposure": 0.95,
            },
            {
                "date": date(2024, 12, 31),
                "value": 110000.0,
                "exposure": 0.95,
            },
        ],

        # Performance metrics
        "cumulative_return": 0.10,
        "cagr": 0.10,
        "max_drawdown": 0.05,
        "daily_sharpe": 1.20,
        "calmar": 2.00,
        "market_exposure": 0.80,
        "max_drawdown_duration_days": 12,
        "average_drawdown_duration_days": 4.5,
    }

    payload = backtest_adapter.build_persistence_payload(
        result=result,
        exchange_code="ASX",
        display_name="BHP Group",
        currency_code="AUD",
        asset_type="EQUITY",
        initial_cash=Decimal("100000.00"),
        strategy_version="1.0.0",
        engine_version="integration-test",
    )

    assert payload["asset"] == {
        "exchange_code": "ASX",
        "symbol": "BHP",
        "display_name": "BHP Group",
        "currency_code": "AUD",
        "asset_type": "EQUITY",
    }




def test_build_persistence_payload_maps_run() -> None:
    """
    Adapter should map engine result and explicit asset metadata
    into the persistence asset and run structures.
    """

    result = {
        "ticker": "BHP",
        "strategy": "MovingAverageCross",
        "start_year": 2024,
        "end_year": 2024,
        "final_value": 110000.0,

        # Strategy-specific parameters
        "fast": 20,
        "slow": 50,

        # Engine/reporting output
        "trades": {
            "total": 5,
        },
        "signal_history": None,

        "portfolio_values": [
            {
                "date": date(2024, 1, 2),
                "value": 100000.0,
                "exposure": 0.0,
            },
            {
                "date": date(2024, 6, 3),
                "value": 105000.0,
                "exposure": 0.95,
            },
            {
                "date": date(2024, 12, 31),
                "value": 110000.0,
                "exposure": 0.95,
            },
        ],

        # Performance metrics
        "cumulative_return": 0.10,
        "cagr": 0.10,
        "max_drawdown": 0.05,
        "daily_sharpe": 1.20,
        "calmar": 2.00,
        "market_exposure": 0.80,
        "max_drawdown_duration_days": 12,
        "average_drawdown_duration_days": 4.5,
    }

    payload = backtest_adapter.build_persistence_payload(
        result=result,
        exchange_code="ASX",
        display_name="BHP Group",
        currency_code="AUD",
        asset_type="EQUITY",
        initial_cash=Decimal("100000.00"),
        strategy_version="1.0.0",
        engine_version="integration-test",
    )



    assert payload["run"] == {
        "strategy_name": "MovingAverageCross",
        "strategy_version": "1.0.0",
        "start_date": date(2024, 1, 2),
        "end_date": date(2024, 12, 31),
        "initial_cash": Decimal("100000.00"),
        "parameters": {
            "fast": 20,
            "slow": 50,
        },
        "engine_version": "integration-test",
    }




def test_build_persistence_payload_portfolio_values() -> None:
    """
    Adapter should map engine result and explicit asset metadata
    into the persistence asset and run structures.
    """

    result = {
        "ticker": "BHP",
        "strategy": "MovingAverageCross",
        "start_year": 2024,
        "end_year": 2024,
        "final_value": 110000.0,

        # Strategy-specific parameters
        "fast": 20,
        "slow": 50,

        # Engine/reporting output
        "trades": {
            "total": 5,
        },
        "signal_history": None,

        "portfolio_values": [
            {
                "date": date(2024, 1, 2),
                "value": 100000.0,
                "exposure": 0.0,
            },
            {
                "date": date(2024, 6, 3),
                "value": 105000.0,
                "exposure": 0.95,
            },
            {
                "date": date(2024, 12, 31),
                "value": 110000.0,
                "exposure": 0.95,
            },
        ],

        # Performance metrics
        "cumulative_return": 0.10,
        "cagr": 0.10,
        "max_drawdown": 0.05,
        "daily_sharpe": 1.20,
        "calmar": 2.00,
        "market_exposure": 0.80,
        "max_drawdown_duration_days": 12,
        "average_drawdown_duration_days": 4.5,
    }

    payload = backtest_adapter.build_persistence_payload(
        result=result,
        exchange_code="ASX",
        display_name="BHP Group",
        currency_code="AUD",
        asset_type="EQUITY",
        initial_cash=Decimal("100000.00"),
        strategy_version="1.0.0",
        engine_version="integration-test",
        # portfolio_values="portfolio_values",
    )


    # print(f"test {payload["portfolio_values"]}", file=sys.stderr)
    assert payload["portfolio_values"] == [
        {
                        "trading_date": date(2024, 1, 2),
                        "portfolio_value": Decimal('100000.0'),
                        "market_exposure": Decimal('0.0'),
                        'drawdown': Decimal('0'),
                    },
                    {
                        "trading_date": date(2024, 6, 3),
                        "portfolio_value": Decimal('105000.0'),
                        "market_exposure": Decimal('0.95'),
                        'drawdown': Decimal('0')
                    },
                    {
                        "trading_date": date(2024, 12, 31),
                        "portfolio_value": Decimal('110000.0'),
                        "market_exposure": Decimal('0.95'),
                        'drawdown': Decimal('0')
                    },
    ]


def test_build_persistence_payload_metrics() -> None:
    """
    Adapter should map engine result and explicit asset metadata
    into the persistence asset and run structures.
    """

    result = {
        "ticker": "BHP",
        "strategy": "MovingAverageCross",
        "start_year": 2024,
        "end_year": 2024,
        "final_value": 110000.0,

        # Strategy-specific parameters
        "fast": 20,
        "slow": 50,

        # Engine/reporting output
        "trades": {
            "total": 5,
        },
        "signal_history": None,

        "portfolio_values": [
            {
                "date": date(2024, 1, 2),
                "value": 100000.0,
                "exposure": 0.0,
            },
            {
                "date": date(2024, 6, 3),
                "value": 105000.0,
                "exposure": 0.95,
            },
            {
                "date": date(2024, 12, 31),
                "value": 110000.0,
                "exposure": 0.95,
            },
        ],

        # Performance metrics
        "cumulative_return": 0.10,
        "cagr": 0.10,
        "max_drawdown": 0.05,
        "daily_sharpe": 1.20,
        "calmar": 0.53,
        "market_exposure": 0.80,
        "max_drawdown_duration_days": 12,
        "average_drawdown_duration_days": 4.5,
    }

    payload = backtest_adapter.build_persistence_payload(
        result=result,
        exchange_code="ASX",
        display_name="BHP Group",
        currency_code="AUD",
        asset_type="EQUITY",
        initial_cash=Decimal("100000.00"),
        strategy_version="1.0.0",
        engine_version="integration-test",
        # portfolio_values="portfolio_values",
    )


    # print(f"test {payload["portfolio_values"]}", file=sys.stderr)
    assert payload["metrics"] == {
        "final_value": Decimal("110000.0"),
        "cumulative_return": Decimal("0.1"),
        "cagr": Decimal("0.10"),
        "max_drawdown": Decimal("0.05"),
        "daily_sharpe": Decimal("1.2"),
        "calmar": Decimal("0.53"),
        "market_exposure": Decimal("0.8"),
        "max_drawdown_duration_days": Decimal("12"),
        "average_drawdown_duration_days": Decimal(
            "4.5"
        ),
        }





def test_build_persistence_payload_maps_portfolio_values_and_computes_drawdown() -> None:
    result = {
        "ticker": "BHP",
        "strategy": "BuyAndHold",
        "start_year": 2024,
        "end_year": 2024,
        "final_value": 110000.0,

        "trades": {},
        "signal_history": None,

        "portfolio_values": [
            {
                "date": date(2024, 1, 2),
                "value": 100000.0,
                "exposure": 0.0,
            },
            {
                "date": date(2024, 1, 3),
                "value": 105000.0,
                "exposure": 0.95,
            },
            {
                "date": date(2024, 1, 4),
                "value": 103000.0,
                "exposure": 0.95,
            },
            {
                "date": date(2024, 1, 5),
                "value": 110000.0,
                "exposure": 0.95,
            },
        ],

        "cumulative_return": 0.10,
        "cagr": 0.10,
        "max_drawdown": 0.05,
        "daily_sharpe": 1.20,
        "calmar": 2.00,
        "market_exposure": 0.80,
        "max_drawdown_duration_days": 12,
        "average_drawdown_duration_days": 4.5,
    }

    payload = backtest_adapter.build_persistence_payload(
        result=result,
        exchange_code="ASX",
        display_name="BHP Group",
        currency_code="AUD",
        asset_type="EQUITY",
        initial_cash=Decimal("100000.00"),
        strategy_version="1.0.0",
        engine_version="test",
    )

    expected_drawdown = (
        Decimal("105000.0")
        - Decimal("103000.0")
    ) / Decimal("105000.0")

    assert payload["portfolio_values"] == [
        {
            "trading_date": date(2024, 1, 2),
            "portfolio_value": Decimal("100000.0"),
            "market_exposure": Decimal("0.0"),
            "drawdown": Decimal("0"),
        },
        {
            "trading_date": date(2024, 1, 3),
            "portfolio_value": Decimal("105000.0"),
            "market_exposure": Decimal("0.95"),
            "drawdown": Decimal("0"),
        },
        {
            "trading_date": date(2024, 1, 4),
            "portfolio_value": Decimal("103000.0"),
            "market_exposure": Decimal("0.95"),
            "drawdown": expected_drawdown,
        },
        {
            "trading_date": date(2024, 1, 5),
            "portfolio_value": Decimal("110000.0"),
            "market_exposure": Decimal("0.95"),
            "drawdown": Decimal("0"),
        },
    ]


def make_valid_result() -> dict:
    return {
        "ticker": "BHP",
        "strategy": "MovingAverageCross",
        "start_year": 2024,
        "end_year": 2024,
        "final_value": 110000.0,

        "fast": 20,
        "slow": 50,

        "trades": {
            "total": 5,
        },

        "signal_history": None,

        "portfolio_values": [
            {
                "date": date(2024, 1, 2),
                "value": 100000.0,
                "exposure": 0.0,
            },
            {
                "date": date(2024, 6, 3),
                "value": 105000.0,
                "exposure": 0.95,
            },
            {
                "date": date(2024, 12, 31),
                "value": 110000.0,
                "exposure": 0.95,
            },
        ],

        "cumulative_return": 0.10,
        "cagr": 0.10,
        "max_drawdown": 0.05,
        "daily_sharpe": 1.20,
        "calmar": 2.00,
        "market_exposure": 0.80,
        "max_drawdown_duration_days": 12,
        "average_drawdown_duration_days": 4.5,
    }


import pytest
def test_build_persistence_payload_reject_empty_portfolio_vales() ->None:
    result = make_valid_result()

    result["portfolio_values"] = []

    with pytest.raises(
        ValueError,
        match="portfolio_values cannot be empty"
    ):
        backtest_adapter.build_persistence_payload(
            result=result,
            exchange_code="ASX",
            currency_code="AUD",
            asset_type="EQUITY",
            display_name="BHP Group",
            initial_cash=Decimal("10000.00"),
            strategy_version="1.0.0",
            engine_version="test",
        )

def test_build_persistence_payload_preserves_none_optional_metrics()->None:
    result = make_valid_result()

    result["daily_sharpe"] = None
    result["calmar"] = None 

    payload = backtest_adapter.build_persistence_payload(
         result=result,
                    exchange_code="ASX",
                    currency_code="AUD",
                    asset_type="EQUITY",
                    display_name="BHP Group",
                    initial_cash=Decimal("10000.00"),
                    strategy_version="1.0.0",
                    engine_version="test",
    )

    assert payload["metrics"]["daily_sharpe"] is None
    assert payload["metrics"]["calmar"] is None


def test_build_persistence_palyload_does_not_modify_input_result() -> None:
    result = make_valid_result()
    og_result = deepcopy(result)

    backtest_adapter.build_persistence_payload(
         result=result,
                    exchange_code="ASX",
                    currency_code="AUD",
                    asset_type="EQUITY",
                    display_name="BHP Group",
                    initial_cash=Decimal("10000.00"),
                    strategy_version="1.0.0",
                    engine_version="test",
    )
    assert result == og_result