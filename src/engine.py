from datetime import datetime
from pathlib import Path
from collections import defaultdict

import backtrader as bt

from strategies.moving_across import MovingAverageCross 
from strategies.buy_n_hold import BuyAndHold
from strategies.cross_momentum import CrossSectionalMomentum
from src.analyzers import PortfolioValueAnalyzer


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


def extract_result(strat, ticker, strategy_name, 
                 start_year, end_year, final_value, **strategy_params):
    return {
        "ticker": ticker,
        "strategy": strategy_name,
        "start_year": start_year,
        "end_year": end_year,
        "final_value": final_value,
        **strategy_params,
        "sharpe": strat.analyzers.sharpe.get_analysis().get("sharperatio"),
        "max_drawdown": strat.analyzers.drawdown.get_analysis()["max"]["drawdown"],
        "annual_return": strat.analyzers.returns.get_analysis().get("rnorm100"),
        "trades": strat.analyzers.trades.get_analysis(),
        "portfolio_values": strat.analyzers.portfolio_value.get_analysis(),
        "signal_history": getattr(strat, "signal_history", None)
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