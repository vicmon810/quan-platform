import pytest
from datetime import date
from src.helper import metrics
import math 


def test_calculate_cumulative_return():
    portfiolio_values = [
        100_000,
        110_000,
        120_000,
    ]

    result = metrics.calculate_cumulative_return(
        portfiolio_values
    )

    assert result == pytest.approx(0.20)




def test_cumulative_return_requires_two_values():
    with pytest.raises(
        ValueError,
        match="at least two portfolio values"
    ):
        metrics.calculate_cumulative_return([100_000])

def test_cumulative_return_rejects_non_positive_initial_value():
    with pytest.raises(
        ValueError,
        match="initial portfolio value must be positive",
    ):
        metrics.calculate_cumulative_return(
            [0, 100_000]
        )

def test_calculate_cagr_over_two_years():
    portfolio_values = [
        100_000,
        121_000,
    ]

    result = metrics.calculate_cagr(
        values = portfolio_values,
        years = 2,
    )
    assert result == pytest.approx(0.10)



def test_cagr_requires_positive_years():
    with pytest.raises(
        ValueError,
        match="years must be positive",
    ):
        metrics.calculate_cagr(
            values=[100_000, 121_000],
            years=0,
        )


def test_cagr_requires_two_values():
    with pytest.raises(
        ValueError,
        match="at least two portfolio values",
    ):
        metrics.calculate_cagr(
            values=[100_000],
            years=2,
        )

def test_cagr_rejects_non_positive_initial_value():
    with pytest.raises(
        ValueError,
        match="initial portfolio value must be positive",
    ):
        metrics.calculate_cagr(
            values=[0, 121_000],
            years=2,
        )

def test_calculate_years_between_date():
    result = metrics.calculate_years_between_dates(
        start_date=date(2022,1,1),
        end_date = date(2024,1,1)
    )

    assert result == pytest.approx(730/365.25)


def test_calculate_years_rejects_same_date():
    with pytest.raises(
        ValueError,
        match="end_date must be later than start_date"
    ):
        metrics.calculate_years_between_dates(
            start_date=date(2024,1,1),
            end_date=date(2024,1,1)
        )

def test_calculate_years_rejects_reversed_dates():
    with pytest.raises(
        ValueError,
        match="end_date must be later than start_date",
    ):
        metrics.calculate_years_between_dates(
            start_date=date(2025, 1, 1),
            end_date=date(2024, 1, 1),
        )

def test_calculate_cagr_from_dates():
    result = metrics.calculate_cagr_from_dates(
        values=[100_000,121_000],
        start_date=date(2022,1,1),
        end_date=date(2024,1,1)
    )

    assert result == pytest.approx(
        0.10,
        abs=0.001,
    )

def test_calculate_max_drawdown():
      portfolio_values = [
        100_000,
        120_000,
        90_000,
        110_000,
        80_000,
        130_000,
     ]
      result = metrics.calculate_max_drawdown(
          portfolio_values
      )

      assert result == pytest.approx(
          1 - 80_000 / 120_000
      )


def test_max_drawdown_is_zero_for_rising_values():
    result = metrics.calculate_max_drawdown(
        [
            100_000,
            110_000,
            120_000,
            130_000
        ]
    )

    assert result == pytest.approx(0.0)


def test_max_drawdown_requires_two_values():
    with pytest.raises(
        ValueError,
        match="at least two portfolio values"
    ):
        metrics.calculate_max_drawdown(
            [1000]
        )

@pytest.mark.parametrize(
    "portfolio_values",
    [
        [100_000, 0],
        [100_000, -10_000],
        [0, 100_000],
    ],
)
def test_max_drawdown_rejects_non_positive_values(
    portfolio_values,
):
    with pytest.raises(
        ValueError,
        match="portfolio values must be positive",
    ):
        metrics.calculate_max_drawdown(
            portfolio_values
        )


def test_calculate_daily_returns():
    portfolio_values = [
        100.0,
        110.0,
        99.0
    ]

    result = metrics.calculate_daily_returns(
        portfolio_values
    )

    assert result == pytest.approx([
        0.10,
        -0.10
    ])


def test_calculate_daily_sharpe():
    portfolio_values = [
    100.0,
    101.0,       # +1%
    99.99,       # -1%
    101.9898,    # +2%
    ]

    result = metrics.calculate_daily_sharpe(
        portfolio_values
    )

    assert result == pytest.approx(
        4 * math.sqrt(3)
    )

def test_daily_sharpe_requires_three_values():
    with pytest.raises(
        ValueError,
        match="at least three portfolio values",
    ):
        metrics.calculate_daily_sharpe([
            100_000,
            101_000,
        ])


def test_daily_sharpe_returns_none_for_zero_volatility():
    result = metrics.calculate_daily_sharpe([
        100.0,
        110.0,
        121.0,
    ])

    assert result is None

def test_daily_sharpe_reject_non_positive_trading_days():
    with pytest.raises(
        ValueError,
        match="trading_days must be positive"
    ):
        metrics.calculate_daily_sharpe(
            values=[
                100.0,
                101.0,
                102.0
            ],
            trading_days=0
        )

def test_daily_sharpe_decreases_with_risk_free_rate():
    portfolio_values = [
        100.0,
        101.0,
        99.99,
        101.8999
    ]
    zero_rate_sharpe = metrics.calculate_daily_sharpe(
        values=portfolio_values,
        annual_risk_free_rate=0.0
    )

    positive_rate_sharpe = metrics.calculate_daily_sharpe(
        values=portfolio_values,
        annual_risk_free_rate=0.05,
    )

    assert zero_rate_sharpe is not None
    assert positive_rate_sharpe is not None 
    assert positive_rate_sharpe < zero_rate_sharpe


def test_calculated_calmar_ratio():
    result = metrics.calculate_calmar_ratio(
        cagr = 0.12,
        max_drawdowm = 0.20
    )

    assert result == pytest.approx(0.60)

def test_calmar_returns_non_when_drawdowm_is_zero():
    result = metrics.calculate_calmar_ratio(
        cagr=0.12,
        max_drawdowm=0.0,
    ) 
    assert result is None

def test_calmar_rejects_negtive_drawdowm():
    with pytest.raises(
        ValueError,
        match="max_drawdowm cannot be negative"
    ):
        metrics.calculate_calmar_ratio(
            cagr=0.12,
            max_drawdowm=-0.20
        )

def test_calmar_can_be_negative():
    result = metrics.calculate_calmar_ratio(
        cagr=-0.10,
        max_drawdowm=0.05
    )
    assert result == pytest.approx(-2)


def test_calculate_market_exposure():
    exposures = [
        0.0,
        0.5,
        1.0,
    ]
    result = metrics.calculate_market_exposure(
        exposures
    )

    assert result == pytest.approx(0.5)

def test_market_exposure_requires_values():
    with pytest.raises(
        ValueError,
        match=("at least one exposure value")
    ):
        metrics.calculate_market_exposure([])

def test_market_exposure_reject_negative_values():
    with pytest.raises(
        ValueError,
        match="exposure values cannot be negative",
    ):
        metrics.calculate_market_exposure([0.5,-9])


def test_calculate_performance_metrics():
    portfolio_records = [
        {
            "date":date(2022,1,1),
            "value":100_000,
            "exposure": 0.0,
        },
        {
            "date":date(2023,1,1),
            "value": 110_000,
            "exposure": 0.5,
        },
        {
            "date":date(2024,1,1),
            "value":121_000,
            "exposure":1.0,
        },
    ]

    result = metrics.calculate_performance_metrics(
        portfolio_records
    )
    assert result["cumulative_return"] == pytest.approx(0.21)

    assert result["cagr"] == pytest.approx(
        0.10,
        abs=0.001,
    )

    assert result["max_drawdown"] == pytest.approx(
        0.0
    )

    assert result["daily_sharpe"] is None
    assert result["calmar"] is None

    assert result["market_exposure"] == pytest.approx(
        0.5
    )

def test_performance_metrics_requires_three_records():
    portfolio_records = [
        {
            "date": date(2023, 1, 1),
            "value": 100_000,
            "exposure": 0.0,
        },
        {
            "date": date(2024, 1, 1),
            "value": 110_000,
            "exposure": 0.95,
        },
    ]

    with pytest.raises(
        ValueError,
        match="at least three portfolio are required",
    ):
        metrics.calculate_performance_metrics(
            portfolio_records
        )


def test_calculate_drawdown_series():
    values = [
        100.0,
        120.0,
        90.0,
        96.0,
        130.0,
    ]

    result = metrics.calculate_drawdown_series(values)

    assert result == pytest.approx(
        [
            0.0,
            0.0,
            0.25,
            0.20,
            0.0,
        ]
    )

def test_calculate_drawdown_duration_series():
    dates = [
        date(2024, 1, 1),
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 4),
        date(2024, 1, 5),
    ]

    drawdowns = [
        0.0,
        0.10,
        0.20,
        0.05,
        0.0,
    ]

    result = metrics.calculate_drawdown_duration_series(
        dates=dates,
        drawdowns=drawdowns,
    )

    assert result == [
        0,
        1,
        2,
        3,
        0,
    ]


def test_calculate_drawdown_duration_series_reject_mismatech_lengths():
    dates =[
        date(2024,1,1),
        date(2024,1,2),
        date(2024,1,3)
    ]

    drawdowns = [0.0,0.1]

    with pytest.raises(ValueError, match="dates and drawdown must have same length"):
        metrics.calculate_drawdown_duration_series(dates=dates, drawdowns=drawdowns,)


def test_calculate_drawdown_duration_series_rejects_empty_input():
    with pytest.raises(
        ValueError,
        match="dates and drawdowns must not be empty",
    ):
        metrics.calculate_drawdown_duration_series(
            dates=[],
            drawdowns=[],
        )



def test_calculate_max_drawdown_duration():
    duration = [ 0,
        1,
        2,
        3,
        0,
        1,
        2,
        0,]
    result = metrics.calculate_max_drawdown_duration(duration)
    assert result == 3

def test_calculate_max_drawdown_duration_rejects_empty_input():
    with pytest.raises(
        ValueError,
        match="at least one duration value is required",
    ):
        metrics.calculate_max_drawdown_duration([])


def test_calculate_average_drawdown_duration():
    durations = [
        0,
        1,
        2,
        3,
        0,
        1,
        2,
        0,
    ]
    result = metrics.calculate_average_duration(durations)
    assert result == pytest.approx(2.5)

def test_calculate_performance_metrics_includes_drawdown_durations():
    portfolio_records = [
        {
            "date": date(2024, 1, 1),
            "value": 100.0,
            "exposure": 1.0,
        },
        {
            "date": date(2024, 1, 2),
            "value": 90.0,
            "exposure": 1.0,
        },
        {
            "date": date(2024, 1, 3),
            "value": 80.0,
            "exposure": 1.0,
        },
        {
            "date": date(2024, 1, 4),
            "value": 70.0,
            "exposure": 1.0,
        },
        {
            "date": date(2024, 1, 5),
            "value": 100.0,
            "exposure": 1.0,
        },
        {
            "date": date(2024, 1, 6),
            "value": 90.0,
            "exposure": 1.0,
        },
        {
            "date": date(2024, 1, 7),
            "value": 80.0,
            "exposure": 1.0,
        },
        {
            "date": date(2024, 1, 8),
            "value": 100.0,
            "exposure": 1.0,
        },
    ]

    result = metrics.calculate_performance_metrics(
        portfolio_records=portfolio_records
    )

    assert result["max_drawdown_duration_days"] == 3

    assert result[
        "average_drawdown_duration_days"
    ] == pytest.approx(2.5)


def test_calculate_average_drawdown_returns_zero_without_drawdown():
    durations = [0,0,0,0,0]
    result = metrics.calculate_average_duration(durations=durations)
    assert result == pytest.approx(0.0)


def test_calculate_rolling_volatility():
    values = [100.0,110.0,99.0,108.9]

    result = metrics.calculate_rolling_volatility(values=values, window=2, trading_days=252)

    expected_volatility = math.sqrt(0.02 * 252)

    assert result[0] is None 
    assert result[1] == pytest.approx(expected_volatility)
    assert result[2] == pytest.approx(expected_volatility)


def test_calculate_rolling_sharpe():
    values = [
        100.0,
        102.0,
        103.02,
        106.1106,
    ]

    result = metrics.calculate_rolling_sharpe(
        values=values,
        window=2,
        annual_risk_free_rate=0.0,
        trading_days=252,
    )

    assert len(result) == 3
    assert result[0] is None

    assert result[1] == pytest.approx(
        33.67491648096547
    )

    assert result[2] == pytest.approx(
        22.449944320643652
    )