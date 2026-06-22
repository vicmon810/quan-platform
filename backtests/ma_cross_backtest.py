from datetime import datetime
import backtrader as bt
from pathlib import Path
import pandas as pd

class MovingAverageCross(bt.Strategy):
    params = (
        ("fast", 20),
        ("slow", 50),
    )

    def __init__(self):
        self.ma_fast = bt.ind.SMA(self.data.close, period=self.params.fast)
        self.ma_slow = bt.ind.SMA(self.data.close, period=self.params.slow)
        self.cross = bt.ind.CrossOver(self.ma_fast, self.ma_slow)

    def next(self):
        if not self.position:
            if self.cross > 0:
                self.buy()
        else:
            if self.cross < 0:
                self.sell()
    
class BuyAndHold(bt.Strategy):
    def next(self):
        if not self.position:
            self.buy


def run_one_ticker(ticker, start_year, end_year):
    cerebro = bt.Cerebro()

 
    data_path = Path(f"data/raw/{ticker}.csv")

    data = bt.feeds.YahooFinanceCSVData(
        dataname=str(data_path),    
        fromdate = datetime(start_year,1,1),
        todate = datetime(end_year,1,1),   
    )

    cerebro.adddata(data)
    cerebro.optstrategy(
        MovingAverageCross,
        fast=range(5,31,5),
        slow=range(40,101,10)
    )

    # cerebro.addstrategy(MovingAverageCross)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
 

    cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    cerebro.broker.setcash(100_000)
    cerebro.broker.setcommission(commission=0.001)

    print("Running Optimization...")



    # print(f"Starting portfolio value: {cerebro.broker.getvalue():.2f}")

    # cerebro.run()
    results = cerebro.run(maxcpus=10)
    rows = []

    for result in results:
        strat = result[0]
        rows.append({
            "ticker": ticker,
            "fast": strat.params.fast,
            "slow": strat.params.slow,
            "sharpe": strat.analyzers.sharpe.get_analysis().get("sharperatio"),
            "max_drawdown":strat.analyzers.drawdown.get_analysis()["max"]["drawdown"],
            "annual_returns":strat.analyzers.returns.get_analysis().get("rnorm100"),
        })

    rows = sorted(
        rows, 
        key=lambda x: x["sharpe"] if x["sharpe"] is not None else -999,
        reverse=True,
    )
    return rows
    # reports_dir = Path("reports")
    # reports_dir.mkdir(exist_ok=True)

    # df_results = pd.DataFrame(rows)

    # top_10 = df_results.head(10)

    # top_10_path = reports_dir/"top_10_param.csv"
    # top_10.to_csv(top_10_path, index=False)

    # print(f"\nParameter set saved to {top_10_path}")

    # print(f"Final portfolio value: {cerebro.broker.getvalue():.2f}\n")
    # print(f"\nSharpe Ratio: {strat.analyzers.sharpe.get_analysis()}\n")
    # print(f"\nDrawdown: {strat.analyzers.drawdown.get_analysis()}\n")
    # print(f"\nReturns: {strat.analyzers.returns.get_analysis()}\n")
    # print(f"\nTrades:{strat.analyzers.trades.get_analysis()}\n")
    # print("\n")
        # cerebro.plot()

    
    # df.to_csv(RAW_DIR/f"{ticker}.csv", index=False)


def run_all():
    tickers = ["SPY", "QQQ", "AAPL", "MSFT"]
    all_rows = []

    for ticker in tickers:
        print(f"Running {ticker}....")
        # all_rows.extend(run_one_ticker(ticker))
        all_rows.extend(run_one_ticker(ticker, 2020,2025))


    df = pd.DataFrame(all_rows)

    df = df.sort_values(
        "sharpe",
        ascending=False,
        na_position="last"
    )

    Path("reports").mkdir(exist_ok=True)

    df.to_csv("reports/all_opt_results.csv", index=False)
    df.head(10).to_csv("reports/top_10_all_tickers.csv", index=False)
    print("\nTop 10:")
    print(df.head(10))
    print("\nSaved to reports/all_optimization_results.csv")
    

def walk_forward_validation():
    ticker = "SPY"
    
    train_results = run_one_ticker(ticker=ticker, 
                                   start_year=2020,
                                   end_year=2023)
    best_train = train_results[0]
    
    test_result = run_single_strategy(
        ticker=ticker,
        fast=best_train["fast"],
        slow=best_train["slow"],
        start_year=2023, 
        end_year=2025,
    )

    benchmark_result = run_buy_and_hold(
        ticker=ticker,
        start_year=2023,
        end_year=2025
    )
   
    df = pd.DataFrame([
        {
            "phase":"train",
            "startegy": "ma_cross",
            **best_train,
            "start_year":2020,
            "end_year":2023,
        },
        {
            "phase":"test",
            **test_result,
        },
        benchmark_result,
    ])

    Path("reports").mkdir(exist_ok=True)
    df.to_csv("reports/walk_forward_spy_with_benchmark.csv", index=False)
    print(df)
    print("\nSaved to reports/walk_forward_spy_with_benchmark.csv")

def run_single_strategy(ticker, fast, slow, start_year, end_year):
    cerebro = bt.Cerebro()

    data_path = Path(f"data/raw/{ticker}.csv")

    data = bt.feeds.YahooFinanceCSVData(
        dataname=str(data_path),
        fromdate=datetime(start_year, 1, 1),
        todate=datetime(end_year, 1, 1),
        reverse=False,
    )

    cerebro.adddata(data)

    cerebro.addstrategy(
        MovingAverageCross,
        fast=fast,
        slow=slow,
    )

    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

    cerebro.broker.setcash(100_000)
    cerebro.broker.setcommission(commission=0.001)

    results = cerebro.run(maxcpus=1)
    strat = results[0]
    
    
    return {
        "ticker": ticker,
        "fast": fast,
        "slow": slow,
        "start_year": start_year,
        "end_year": end_year,
        "final_value": cerebro.broker.getvalue(),
        "sharpe": strat.analyzers.sharpe.get_analysis().get("sharperatio"),
        "max_drawdown": strat.analyzers.drawdown.get_analysis()["max"]["drawdown"],
        "annual_return": strat.analyzers.returns.get_analysis().get("rnorm100"),
        "trade":  strat.analyzers.trades.get_analysis(),
    }


def run_buy_and_hold(ticker, start_year, end_year):
    cerebro = bt.Cerebro()

    data_path = Path(f"data/raw/{ticker}.csv")

    data = bt.feeds.YahooFinanceCSVData(
        dataname=str(data_path),
        fromdate=datetime(start_year, 1, 1),
        todate=datetime(end_year, 1, 1),
        reverse=False,
    )

    cerebro.adddata(data)
    cerebro.addstrategy(BuyAndHold)

    cerebro.addsizer(bt.sizers.PercentSizer, percents=95)

    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

    cerebro.broker.setcash(100_000)
    cerebro.broker.setcommission(commission=0.001)

    results = cerebro.run(maxcpus=1)
    strat = results[0]

    return {
        "phase": "benchmark",
        "strategy": "buy_and_hold",
        "ticker": ticker,
        "fast": None,
        "slow": None,
        "start_year": start_year,
        "end_year": end_year,
        "final_value": cerebro.broker.getvalue(),
        "max_drawdown": strat.analyzers.drawdown.get_analysis()["max"]["drawdown"],
        "annual_return": strat.analyzers.returns.get_analysis().get("rnorm100"),
        "trade": strat.analyzers.trades.get_analysis(),
    }

if __name__ == "__main__":
    # run_all()
    walk_forward_validation()