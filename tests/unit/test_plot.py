from datetime import date 
import pytest 
import sys
from src.helper.plotting import build_drawdown_frame 
from src.helper.plotting import plot_drawdown_curves

def test_build_drawdown_frame():
    results = [
        {
            "strategy": "BuyAndHold",
            "portfolio_values": [
                {
                    "date": date(2024, 1, 1),
                    "value": 100.0,
                    "exposure": 0.0,
                },
                {
                    "date": date(2024, 1, 2),
                    "value": 120.0,
                    "exposure": 1.0,
                },
                {
                    "date": date(2024, 1, 3),
                    "value": 90.0,
                    "exposure": 1.0,
                },
                {
                    "date": date(2024, 1, 4),
                    "value": 96.0,
                    "exposure": 1.0,
                },
            ],
        },
        {
            "strategy": "Momentum",
            "portfolio_values": [
                {
                    "date": date(2024, 1, 1),
                    "value": 100.0,
                    "exposure": 0.0,
                },
                {
                    "date": date(2024, 1, 2),
                    "value": 110.0,
                    "exposure": 1.0,
                },
                {
                    "date": date(2024, 1, 3),
                    "value": 105.0,
                    "exposure": 1.0,
                },
            ],
        },
    ]

    frame = build_drawdown_frame(results)
    print("error:\n",frame, file=sys.stderr)
    assert frame.columns.tolist() == [
        "date",
        "drawdown",
        "strategy",
    ]

    buy_and_hold = frame [
        frame["strategy"] == "BuyAndHold"
    ]

    momentum = frame [frame["strategy"] == "Momentum"]
    assert buy_and_hold["drawdown"].tolist() == pytest.approx(
        [
            0.0,
            0.0,
            -0.25,
            -0.20,
        ]
    )
    
    assert momentum["drawdown"].tolist() == pytest.approx(
        [
            0.0,
            0.0,
            -(5.0 / 110.0),
        ]
    )


def test_plot_drawdown_curves_creates_file(
    tmp_path,
):
    results = [
        {
            "strategy": "BuyAndHold",
            "portfolio_values": [
                {
                    "date": date(2024, 1, 1),
                    "value": 100.0,
                    "exposure": 0.0,
                },
                {
                    "date": date(2024, 1, 2),
                    "value": 120.0,
                    "exposure": 1.0,
                },
                {
                    "date": date(2024, 1, 3),
                    "value": 90.0,
                    "exposure": 1.0,
                },
            ],
        }
    ]

    output_path = (
        tmp_path
        / "drawdown_comparison.png"
    )

    result_path = plot_drawdown_curves(
        results=results,
        output_path=output_path,
    )

    assert result_path == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0