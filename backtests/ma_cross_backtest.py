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


def run_one_ticker(ticker):
    cerebro = bt.Cerebro()

 
    data_path = Path(f"data/raw/{ticker}.csv")

    data = bt.feeds.YahooFinanceCSVData(
        dataname=str(data_path),
        reverse=False,
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
        all_rows.extend(run_one_ticker(ticker))


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
    

if __name__ == "__main__":
    run_all()