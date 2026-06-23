from pathlib import Path

import pandas as pd

from src.engine import optimize_ma, run_single_ma, run_buy_and_hold, run_multipl_ma, multiple_opt_ma, multiple_buy_and_hold
from src.plotting import plot_equity_curves


def remove_large_objects(row):
    clean = row.copy()
    clean.pop("portfolio_values", None)
    clean.pop("trades", None)
    return clean


def main():
    # ticker = [[]]
    tickers = ["SPY", "QQQ", "AAPL", "MSFT"]
    train_start = 2020
    train_end = 2023

    test_start = 2023
    test_end = 2025

    print("Optimizing on training period...")
    train_results = multiple_opt_ma(tickers=tickers, start_year=train_start, end_year=train_end) 
    #optimize_ma(tickers, train_start, train_end)
    # print("===")
    # print(type(train_results))
    # print(train_results[0]["ticker"])
    # print("===")
    best = train_results

    print("Best train parameter:")
    print(type(best))

    print("Testing MA strategy...")
    ma_test = run_multipl_ma (  #run_single_ma
        tickers=tickers,
        fast=best["fast"],
        slow=best["slow"],
        start_year=test_start,
        end_year=test_end,
    )

    print("Running benchmark...")
    benchmark = multiple_buy_and_hold(#run_buy_and_hold(
        tickers=tickers,
        start_year=test_start,
        end_year=test_end,
    )

    report_rows = [    ]
    for r in ma_test:
        report_rows.append({"phase": "test", **remove_large_objects(r)})
    for r in benchmark:
        report_rows.append({"phase": "benchmark", **remove_large_objects(r)})

    # report_rows.append({"phase", "benchmark", **best})
    report_rows.append({"phase": "train", **best})

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    df = pd.DataFrame(report_rows)
    df.to_csv(reports_dir / "walk_forward_summary.csv", index=False)

    plot_equity_curves(
        results=[ma_test, benchmark],
        output_path=reports_dir / "equity_curve_spy.png",
    )

    print(df)
    print("\nSaved:")
    print("reports/walk_forward_summary.csv")
    print("reports/equity_curve_spy.png")


if __name__ == "__main__":
    main()