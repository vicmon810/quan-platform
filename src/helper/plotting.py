from pathlib import Path
from mizani.formatters import percent_format
from plotnine import geom_hline, ggplot, aes, geom_line, labs, scale_y_continuous, theme_minimal
import pandas as pd
import matplotlib.pyplot as plt
from collections.abc import Sequence
from typing import Any 
from src.helper.metrics import calculate_drawdown_series

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
    
def build_drawdown_frame(results:Sequence[dict[str,Any]],)->pd.DataFrame:
    """
    Convert strategy backtest results into a drawdown DataFrame.

    Drawdowns are represented as negative values for plotting.
    """

    if not results: raise ValueError("at least one strategy result is required")

    frames: list[pd.DataFrame] = []

    for result in results: 
        strategy = result.get("strategy")
        portfolio_values = result.get("portfolio_values")

        if not strategy: raise ValueError(  "each result must contain a strategy name")

        if not portfolio_values: raise ValueError(f"{strategy} has no protfolio value records")

        dates = [record["date"] for record in portfolio_values]
        values = [ float(record["value"])for record in portfolio_values]
        positive_drawdowns = calculate_drawdown_series(values=values)
        frame = pd.DataFrame(
            {
                "date": pd.to_datetime(dates),
                "drawdown":[-drawdown for drawdown in positive_drawdowns],
                "strategy": strategy,
            }
        )

        frames.append(frame)
    return pd.concat(frames, ignore_index=True) 

def plot_drawdown_curves(results:Sequence[dict[str,Any]], output_path:str | Path) -> Path:
    """
    Plot strategy drawdown curves and save them as an image.

    Return the generated image path.
    """
    drawdown_frame = build_drawdown_frame(results=results)

    path = Path(output_path)

    path.parent.mkdir(parents=True,exist_ok=True)

    plot = (
        ggplot(drawdown_frame, aes(x="date",y="drawdown", color="strategy"),)
        +geom_line() 
        +geom_hline(
            yintercept=0,
            linetype='dashed',
            alpha=0.5,
        )+scale_y_continuous(
            labels=percent_format()
        )+labs(
            title="Strategy Drawdown Comparison",
            x="Date",
            y="Drawdown",
            color="Strategy"
        )+theme_minimal()
    )

    plot.save(
        filename=str(path),
        width=12,
        height=6,
        dpi=150,
        verbose=False
    )
    return path