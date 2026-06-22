from datetime import datetime
from pathlib import Path

import backtrader as bt

from src.strategies import MovingAverageCross, BuyAndHold
from src.analyzers import PortfolioValueAnalyzer


def add_standard_analyzers(cerebro):
    cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    cerebro.addanalyzer(PortfolioValueAnalyzer, _name="portfolio_value")


def make_data_feed(ticker, start_year, end_year):
    data_path = Path(f"data/raw/{ticker}.csv")

    return bt.feeds.YahooFinanceCSVData(
        dataname=str(data_path),
        fromdate=datetime(start_year, 1, 1),
        todate=datetime(end_year, 1, 1),
        reverse=False,
    )


def extract_result(strat, ticker, strategy_name, fast, slow, start_year, end_year, final_value):
    return {
        "ticker": ticker,
        "strategy": strategy_name,
        "fast": fast,
        "slow": slow,
        "start_year": start_year,
        "end_year": end_year,
        "final_value": final_value,
        "sharpe": strat.analyzers.sharpe.get_analysis().get("sharperatio"),
        "max_drawdown": strat.analyzers.drawdown.get_analysis()["max"]["drawdown"],
        "annual_return": strat.analyzers.returns.get_analysis().get("rnorm100"),
        "trades": strat.analyzers.trades.get_analysis(),
        "portfolio_values": strat.analyzers.portfolio_value.get_analysis(),
    }


def run_single_ma(ticker, fast, slow, start_year, end_year, cash=100_000):
    cerebro = bt.Cerebro()
    cerebro.adddata(make_data_feed(ticker, start_year, end_year))

    cerebro.addstrategy(MovingAverageCross, fast=fast, slow=slow)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    add_standard_analyzers(cerebro)

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)

    results = cerebro.run(maxcpus=1)
    strat = results[0]

    return extract_result(
        strat=strat,
        ticker=ticker,
        strategy_name="ma_cross",
        fast=fast,
        slow=slow,
        start_year=start_year,
        end_year=end_year,
        final_value=cerebro.broker.getvalue(),
    )


def run_buy_and_hold(ticker, start_year, end_year, cash=100_000):
    cerebro = bt.Cerebro()
    cerebro.adddata(make_data_feed(ticker, start_year, end_year))

    cerebro.addstrategy(BuyAndHold)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    add_standard_analyzers(cerebro)

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)

    results = cerebro.run(maxcpus=1)
    strat = results[0]

    return extract_result(
        strat=strat,
        ticker=ticker,
        strategy_name="buy_and_hold",
        fast=None,
        slow=None,
        start_year=start_year,
        end_year=end_year,
        final_value=cerebro.broker.getvalue(),
    )


def optimize_ma(ticker, start_year, end_year, cash=100_000):
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