from pathlib import Path


from src.engine import run_single
from src.reporting import build_strategy_comparison
from strategies.buy_n_hold import BuyAndHold
from strategies.moving_across import MovingAverageCross
from strategies.time_serise_momentum import (
    TimeSeriseMomentum,
)


def main():
    ticker = "SPY"
    start_year = 2020
    end_year = 2025
    cach = 100_000


    results = [
        run_single(
            ticker=ticker,
            start_year=start_year,
            end_year=end_year,
            strategy_cls=BuyAndHold,
            strategy_param={},
            cash=cach
        ),
        run_single(
            ticker=ticker,
            start_year=start_year,
            end_year=end_year,
            strategy_cls=MovingAverageCross,
            strategy_param={
                "fast":15,
                "slow":45,
            },
            cash=cach
        ),
        run_single(
            ticker=ticker,
            start_year=start_year,
            end_year=end_year,
            strategy_cls=TimeSeriseMomentum,
            strategy_param={
                "lookback":126,
                "threshold":0.05,
            },
            cash=cach
        ),
    ]

    comparison = build_strategy_comparison(results=results)

    report_dir = Path("reports")

    report_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    comparison.to_csv(
        report_dir / "strategy_comparisoin.csv",
        index=False,
    )

    dispay_table = comparison.copy()

    percentage_columns = [
        "cumulative_return",
        "cagr",
        "max_drawdown",
        "market_exposure",
    ]
    for column in percentage_columns:
        dispay_table[column] = (dispay_table[column].map(lambda value: f"value:.2%"))

    numeric_columns = [
        "final_value",
        "daily_sharpe",
        "calmar",
    ]

    for column in numeric_columns:
        dispay_table[column] = (
            dispay_table[column]
            .map(
                lambda value : (
                    "N/A"
                    if value is None
                    else f"{value:.2f}"
                )
            )
        )

    print(dispay_table.to_string(index=False))

    print(
        "\nSaved:"
        "\nreports/strategy_comparison.csv"
    )

if __name__ == "__main__":
    main()