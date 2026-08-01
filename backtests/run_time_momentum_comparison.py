"""
Desc: Compare BuyAndHold, MovingAverageCross, and TimeSeriseMomentum
      strategies on the same ticker and time range, then save a
      summary CSV and an equity curve plot to the reports/ directory.
"""

from pathlib import Path 
import pandas as pd 

from src.engine import run_single
from strategies.buy_n_hold import BuyAndHold
from strategies.moving_across import MovingAverageCross
from strategies.time_serise_momentum import TimeSeriseMomentum
from src.plotting import plot_equity_curves

def remove_large_fieldes(result:dict) -> dict:
    """
    Desc: Strip large, non-tabular fields from a backtest result so it
          can be safely converted into a single row of a summary
          DataFrame (portfolio_values and trades are too large/nested
          for a flat CSV row).
    Param: result (dict) - a single backtest result, as returned by
           run_single / extract_result
    Return: dict - a shallow copy of result with large fields removed
    """
    clean_result = result.copy()

    clean_result.pop("portfolio_values", None)
    clean_result.pop("trades", None)

    return clean_result


def main():
    """
    Desc: Run BuyAndHold, MovingAverageCross, and TimeSeriseMomentum
          backtests on the same ticker/date range/cash, then:
          1) write a summary CSV comparing key metrics per strategy
          2) plot equity curves for all three strategies on one chart
          3) print a condensed comparison table to stdout
    Param: None (ticker, date range, and strategy params are hardcoded
           below; edit these constants to change what gets compared)
    Return: None
    """

    ticker = "SPY"
    start_year = 2018
    end_year = 2025
    initial_cash = 100_000
    # Baseline: passive buy-and-hold, no strategy parameters needed
    buy_hold_result  = run_single(
        ticker=ticker,
        strategy_cls=BuyAndHold,
        strategy_param={},
        start_year=start_year,
        end_year=end_year,
        cash= initial_cash
    )
    # Trend-following via fast/slow moving average crossover

    ma_result = run_single(
        ticker=ticker,
        strategy_cls=MovingAverageCross,
        strategy_param={
            "fast": 30,
            "slow": 35,
        },
        start_year=start_year,
        end_year=end_year,
        cash=initial_cash
    )
    # Trend-following via trailing return over a lookback window
    momentum_result = run_single(
        ticker=ticker,
        strategy_cls=TimeSeriseMomentum,
        strategy_param={
            "lookback": 30,
            "threshold": 0.03,
            "target_percent": 0.95,
        },
        start_year=start_year,
        end_year=end_year,
        cash=initial_cash
    )

    results = [
        buy_hold_result,
        ma_result, 
        momentum_result,
    ]

    report_dir = Path("reports")
    report_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = pd.DataFrame(
        remove_large_fieldes(result=result)
        for result in results
    )

    summary.to_csv(
        report_dir / "time_momentum_comparison.csv"
    )

    plot_equity_curves(
        results=results,
        output_path=report_dir/ "time_momentum_comparison.png"
    )

    columns = [
        "strategy",
        "final_value",
        "annual_return",
        "sharpe",
    ]

    print(summary[columns].to_string(index=False))

    print(f"Saved: {report_dir / 'time_momentum_comparison.csv'}")
    print(f"Saved: {report_dir / 'time_momentum_comparison.png'}")


if __name__ == "__main__":
    main()