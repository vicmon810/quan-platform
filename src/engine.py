from datetime import datetime
from pathlib import Path
from collections import defaultdict

import backtrader as bt

from strategies.moving_across import MovingAverageCross 
from strategies.buy_n_hold import BuyAndHold
from strategies.cross_momentum import CrossSectionalMomentum
from src.analyzers import PortfolioValueAnalyzer
from src.metrics import calculate_market_exposure, calculate_performance_metrics
from collections.abc import Sequence
from typing import Any
def add_standard_analyzers(cerebro):
    cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    cerebro.addanalyzer(PortfolioValueAnalyzer, _name="portfolio_value")


def make_data_feed(ticker, start_year, end_year):
    if not ticker:
        raise ValueError("Ticker cannot be empty")

    if start_year >= end_year:
        raise ValueError("start_year must be eariler than end_year")

    data_path = Path(f"data/raw/{ticker}.csv")

    if not data_path.is_file():
        raise FileNotFoundError(
            f"Data file not found: {data_path}"
        )
    
    return bt.feeds.YahooFinanceCSVData(
        dataname=str(data_path),
        fromdate=datetime(start_year, 1, 1),
        todate=datetime(end_year, 1, 1),
        reverse=False,
    )

# def market_exposure(portfolio_values: Sequence[dict[str, Any]])-> float:
#         """
#         Desc: Compute the average market exposure from a strategy's
#             recorded portfolio value history.
#         Param: portfolio_values (list[dict]) - each record must contain
#             an "exposure" field
#         Return: float - average market exposure (see calculate_market_exposure)
#         """    
#         exposures = [
#             record["exposure"]
#             for record in portfolio_values
#         ]
    
#         return calculate_market_exposure(exposures=exposures)
    
def performance_metric(portfolio_value:Sequence[dict[str,Any]]) -> dict[str,float|None]:
    """Calculate all performance metrics."""

    return calculate_performance_metrics(portfolio_record=portfolio_value)

def extract_result(strat, ticker, strategy_name, 
                 start_year, end_year, final_value, **strategy_params):
    """
    Desc: Package a completed backtrader strategy run into a flat
          result dict, pulling metrics from the strategy's analyzers
          and computing derived stats like market exposure.
    Param: strat - the finished backtrader strategy instance
           ticker (str) - the ticker being tested
           strategy_name (str) - name of the strategy class used
           start_year (int), end_year (int) - backtest date range
           final_value (float) - final portfolio value from the broker
           **strategy_params - any additional strategy parameters to
           include in the result (e.g. fast, slow, lookback)
    Return: dict - flat summary of the backtest result
    """
    
    portfolio_value = strat.analyzers.portfolio_value.get_analysis()
    metrics = performance_metric(portfolio_value=portfolio_value)
    return {
        "ticker": ticker,
        "strategy": strategy_name,
        "start_year": start_year,
        "end_year": end_year,
        "final_value": final_value,
        **strategy_params,
        "trades": strat.analyzers.trades.get_analysis(),
        "portfolio_values": strat.analyzers.portfolio_value.get_analysis(),
        "signal_history": getattr(strat, "signal_history", None),
        **metrics
    }


def run_single(ticker, strategy_cls, strategy_param, start_year, end_year, cash=100_000):
    cerebro = bt.Cerebro()
    cerebro.adddata(make_data_feed(ticker, start_year, end_year))

    cerebro.addstrategy(strategy_cls, **strategy_param)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    add_standard_analyzers(cerebro)

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)

    results = cerebro.run(maxcpus=1)
    strat = results[0]

    return extract_result(
        strat=strat,
        ticker=ticker,
        strategy_name=strategy_cls.__name__,
        start_year=start_year,
        end_year=end_year,
        final_value=cerebro.broker.getvalue(),
        **strategy_param,
    )

def run_multipl(tickers, 
                strategy_cls, 
                strategy_param,
                start_year, 
                end_year, 
                cash=100_000):
    if not tickers:
        raise ValueError("tickers cannot be empty")
    return [
        run_single(
                ticker, 
                strategy_cls, 
                strategy_param,
                start_year, 
                end_year,
                cash=cash
        )
        for ticker in tickers
    ]


def run_buy_and_hold(ticker, start_year, end_year, cash=100_000):
    return run_single(
        ticker=ticker,
        strategy_cls=BuyAndHold,
        strategy_param={},
        start_year=start_year,
        end_year=end_year,
        cash=cash,
    )

def multiple_buy_and_hold(tickers, start_year, end_year, cash=100_000):
    return run_multipl(
        tickers=tickers,
        strategy_cls=BuyAndHold,
        strategy_param={},
        start_year=start_year,
        end_year=end_year,
        cash=cash 
    ) 

def optimize(ticker, start_year, end_year, cash=100_000):
    cerebro = bt.Cerebro()
    cerebro.adddata(make_data_feed(ticker, start_year, end_year))

    cerebro.optstrategy(
        MovingAverageCross,
        fast=range(5, 31, 5),
        slow=range(40, 101, 10),
    )

    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
    add_standard_analyzers(cerebro)

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)

    results = cerebro.run(maxcpus=1)

    rows = []

    for result in results:
        strat = result[0]

        rows.append({
            "ticker": ticker,
            "strategy": "ma_cross",
            "fast": strat.params.fast,
            "slow": strat.params.slow,
            "start_year": start_year,
            "end_year": end_year,
            "sharpe": strat.analyzers.sharpe.get_analysis().get("sharperatio"),
            "max_drawdown": strat.analyzers.drawdown.get_analysis()["max"]["drawdown"],
            "annual_return": strat.analyzers.returns.get_analysis().get("rnorm100"),
        })

    rows = sorted(
        rows,
        key=lambda x: x["sharpe"] if x["sharpe"] is not None else -999,
        reverse=True,
    )

    return rows


def multiple_optimize(tickers, start_year, end_year, cash=100_000):
    results = []
    for ticker in tickers:
        results.append(
            optimize(
                ticker=ticker,
                start_year=start_year,
                end_year=end_year,
                cash=cash
            )
        )

    all_results = [item for sublist in results for item in sublist]
    param_scores = defaultdict(list)
    for r in all_results:
        if r["sharpe"] is not None: 
            key = (r["fast"], r["slow"])
            param_scores[key].append(r["sharpe"])

    best_key = max(
        param_scores,
        # key=lambda k :sum(param_scores[k]/ len(param_scores[k]))
        key=lambda k: sum(param_scores[k])/len(param_scores[k])
    )
    best = {"fast": best_key[0], "slow": best_key[1]}
    print(f"testing best {type(best)}")
    return best