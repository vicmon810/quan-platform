from pathlib import Path
from plotnine import ggplot, aes, geom_line, labs, theme_minimal
import pandas as pd
import matplotlib.pyplot as plt


def plot_equity_curves(results, output_path):
    """
    Desc: Plot equity curves for an arbitrary list of backtest results.
          Each result must contain 'portfolio_values' (list of
          {"date": ..., "value": ...}) and a 'label' for the legend.
    Param: results (list[dict]) - flat list of backtest result dicts
           output_path (str | Path) - where to save the plot
    Return: None
    """
    # plt.figure(figsize=(12,6))
    frames = []
    for result in results:
        df = pd.DataFrame(result["portfolio_values"])
        df["date"] = pd.to_datetime(df["date"])
        df["label"] = result["strategy"]
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    plot = (
        ggplot(combined, aes(x="date", y="value", color="label"))
        + geom_line() 
        + labs(title="Strategy Comparison", x="Date", y="Portfolio Value")
        + theme_minimal()
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot.save(str(output_path), dpi=150, width=12, height=6)
    
    