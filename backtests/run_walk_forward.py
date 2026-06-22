from pathlib import Path

import pandas as pd

from src.engine import optimize_ma, run_single_ma, run_buy_and_hold
from src.plotting import plot_equity_curves


def remove_large_objects(row):
    clean = row.copy()
    clean.pop("portfolio_values", None)
    clean.pop("trades", None)
    return clean


def main():
    ticker = "SPY"

    train_start = 2020
    train_end = 2023

    test_start = 2023
    test_end = 2025

    print("Optimizing on training period...")
    train_results = optimize_ma(ticker, train_start, train_end)
    best = train_results[0]

    print("Best train parameter:")
    print(best)

    print("Testing MA strategy...")
    ma_test = run_single_ma(
        ticker=ticker,
        fast=best["fast"],
        slow=best["slow"],
        start_year=test_start,
        end_year=test_end,
    )

    print("Running benchmark...")
    benchmark = run_buy_and_hold(
        ticker=ticker,
        start_year=test_start,
        end_year=test_end,
    )

    report_rows = [
        {
            "phase": "train",
            **best,
        },
        {
            "phase": "test",
            **remove_large_objects(ma_test),
        },
        {
            "phase": "benchmark",
            **remove_large_objects(benchmark),
        },
    ]

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