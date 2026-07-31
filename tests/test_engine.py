from pathlib import Path 
import pandas as pd
import pytest
from src.engine import run_single, run_multipl
from strategies.buy_n_hold import BuyAndHold



def create_rising_price_data(output_path:Path, start_date="2023-01-02", periods=120 ) -> None: 
    """
    Desc: Create a increase trend of stock, test for Buy and Hold
    Param: Path of input file 
    return: serise of number with up trend
    """
    dates = pd.bdate_range(
        start=start_date,
        periods=periods,
    )

    close_price = [
        100 + index * 0.5
        for index in range(len(dates))
    ]

    data = pd.DataFrame({
        "Date": dates,
        "Open": close_price,
        "High": [price +1 for price in close_price],
        "Low" : [price -1 for price in close_price],
        "Close":close_price,
        "Adj close": close_price,
        "Volume": [1_000_000] * len(dates),
    })

    
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    data.to_csv(
        output_path,
        index=False
    )


def test_run_single_buy_and_hold_one_rising_market(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    csv_path = tmp_path / "data" / "raw" / "TEST.csv"
    create_rising_price_data(csv_path)
    initial_cash = 100_000

    result = run_single(
        ticker="TEST",
        strategy_cls=BuyAndHold,
        strategy_param={},
        start_year=2023,
        end_year=2024,
        cash=initial_cash
    )

    assert result["ticker"] == "TEST"
    assert result["strategy"] == "BuyAndHold"

    assert result["final_value"] > initial_cash

    assert result["annual_return"] is not None 
    assert result["max_drawdown"] >= 0 
    assert len(result["portfolio_values"]) > 0 


def test_run_multiple_buy_and_hold_on_rising_market(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


    tests = ["TEST1", "TEST2", "TEST3"]

    for test in tests:
        csv_paths = tmp_path / "data" / "raw" / f"{test}.csv"  
        create_rising_price_data(csv_paths)

    initial_cash = 100_000
    results = run_multipl(
        tickers=  tests,
        strategy_cls=BuyAndHold,
        strategy_param={},
        start_year=2023,
        end_year=2024,
        cash=initial_cash
    )
    assert isinstance(results, list)
    assert len(results) == len(tests)
    return_tickers = {result["ticker"] for result in results}
    assert return_tickers == set(tests)
    for result in results:
        assert result["strategy"] == "BuyAndHold"
        assert result["final_value"] > initial_cash
        assert result["annual_return"] is not None 
        assert result["max_drawdown"] >= 0 
        assert len(result["portfolio_values"]) > 0 



def test_run_single_raises_when_data_file_missing(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(
        FileNotFoundError,
        match="Data file not found",
    ):
        run_single(
            ticker="MISSING",
            strategy_cls=BuyAndHold,
            strategy_param={},
            start_year=2023,
            end_year=2024,
            cash=100_000,
        )

def test_run_single_rejects_invalid_year_range(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(
        ValueError,
        match="start_year must be eariler than end_year",
    ):
        run_single(
            ticker="TEST",
            strategy_cls=BuyAndHold,
            strategy_param={},
            start_year=2024,
            end_year=2023,
            cash=100_000,
        )

def test_run_multiple_respects_cash_argument(
        tmp_path,
        monkeypatch
):
    monkeypatch.chdir(tmp_path)

    tickers = ["TEST1", "TEST2"]
    initial_cash = 50_000

    for ticker in tickers:
        csv_path = (
            tmp_path
            / "data"
            / "raw"
            / f"{ticker}.csv"
        )

        create_rising_price_data(csv_path)

    results = run_multipl(
        tickers=tickers,
        strategy_cls= BuyAndHold,
        strategy_param= {},
        start_year=2023,
        end_year=2024,
        cash=initial_cash
    )

    assert len(results) ==2
    for result in results:
        portfolio_values = result["portfolio_values"]

        assert len(portfolio_values) > 0

        first_value = portfolio_values[0]["value"]

        assert first_value == pytest.approx(
            initial_cash,
            rel=1e-6
        )
        assert result["final_value"] > initial_cash


def test_run_multiple_rejects_empty_ticker_list():
    with pytest.raises(
        ValueError,
        match="tickers cannot be empty"
    ):
        run_multipl(
            tickers=[],
            strategy_cls=BuyAndHold,
            strategy_param={},
            start_year=2023,
            end_year=2024,
            cash=100
        )