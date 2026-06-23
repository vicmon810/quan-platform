from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def plot_equity_curves(results, output_path):
    plt.figure(figsize=(12, 6))

    for result_list in results:
        # result_list 是 [{"ticker": "SPY", ...}, {"ticker": "QQQ", ...}]
        for result in result_list:
            df = pd.DataFrame(result["portfolio_values"])
            df["date"] = pd.to_datetime(df["date"])

            if result["strategy"] == "ma_cross":
                label = f"{result['ticker']} MA({result['fast']}, {result['slow']})"
            else:
                label = f"{result['ticker']} Buy&Hold"

            plt.plot(df["date"], df["value"], label=label)

    plt.title("Strategy vs Buy & Hold")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)

    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True)

    plt.savefig(output_path, dpi=150)
    plt.close()