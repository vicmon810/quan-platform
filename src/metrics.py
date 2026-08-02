from collections.abc import Sequence
from datetime import date
import numpy as np
import math 
import statistics
from typing import Any
def calculate_cumulative_return(
        values: Sequence[float],
) -> float:
    """
    calcualte total return from the first to last value
    """

    if len(values) < 2:
        raise ValueError(
            "at least two portfolio values"
        )
    initial_value = float(values[0])
    if initial_value <= 0:
        raise ValueError(
            "initial portfolio value must be positive"
        )
    final_value = float(values[-1])

    return final_value/initial_value-1


def calculate_cagr(
        values:Sequence[float],
        years:float
) -> float:
    
    """Calculate compound annual growth rate""" 
    if years <= 0:
        raise ValueError(
            "years must be positive",
        )

    if len(values) < 2 :
        raise ValueError(
            "at least two portfolio values",
        )
    initial_value = float(values[0])

    if initial_value <= 0:
        raise ValueError(
            "initial portfolio value must be positive"
            )

    final_value = float(values[-1])
    
    return (
        final_value / initial_value
    ) ** (1/years) -1

def calculate_years_between_dates(
        start_date: date,
        end_date: date,
) -> float :
    """
    convert a calendar date range into fractinal years
    """
    if end_date <= start_date:
        raise ValueError(
             "end_date must be later than start_date"
        )
    days = (end_date - start_date).days
    return days / 365.25


def calculate_cagr_from_dates(
        values: Sequence[float],
        start_date:date,
        end_date:date
) -> float:
    """
    Calcualte CARG using actual calendar dates
    """

    years = calculate_years_between_dates(
        start_date=start_date,
        end_date=end_date
    )
    return calculate_cagr(
        values=values,
        years=years
    )


def calculate_max_drawdown(values: Sequence[float]):
    """
    Calculate maximum peak to troungh portfolio drawdown
    """
    if len(values) <= 1:
        raise ValueError(
            "at least two portfolio values"
        )

    if any(
        value <= 0
        for value in values
    ): raise ValueError(
        "portfolio values must be positive"
    )
    running_peak = float(values[0])
    values = np.asarray(values, dtype=float)

    running_peak = np.maximum.accumulate(values)
    drawdown = (running_peak - values) / running_peak

    return float(drawdown.max())



def calculate_daily_returns(
        values: Sequence[float]
) -> list[float]:
    """
    calculate simple return between consecutive values
    """

    if len(values) < 2:
        raise ValueError(
            "at least two portfolio values are required"
        )

    portfolio_values = [
        float(value)
        for value in values
    ]

    if any(
        value <= 0
        for value in values
    ): raise ValueError(
        "portfolio values must be positive"
        )


    return [
        current_value / previous_value -1 
        for previous_value,current_value in zip(
            portfolio_values,
            portfolio_values[1:]
        )
    ]


def calculate_daily_sharpe(
        values: Sequence[float],
        annual_risk_free_rate: float = 0.0,
        trading_days:int =  252,
) -> float | None : 
    """
    calcualte annualized sharp ratio from daily values
    """

    if len(values) < 3:
        raise ValueError("at least three portfolio values are required")

    if trading_days <= 0:
        raise ValueError("trading_days must be positive")
    if annual_risk_free_rate <= -1:
        raise ValueError("annual_risk_free_rate must be greater than -1")

    daily_returns = calculate_daily_returns(
        values=values
    )

    daily_risk_free_rate = (
        1 + annual_risk_free_rate
    ) ** (1/trading_days) -1

    excess_returns = [
        daily_return - daily_risk_free_rate
        for daily_return in daily_returns
    ]

    mean_excess_return = statistics.fmean(excess_returns)
    dail_volatility = statistics.stdev(excess_returns)

    if math.isclose(
        dail_volatility, 0.0, abs_tol=1e-15
    ): return None 

    return(mean_excess_return / dail_volatility * math.sqrt(trading_days))


def calculate_calmar_ratio(
        cagr: float,
        max_drawdowm:float,
) -> float | None:
    """
    calculate CAGR relative to maximum drawdowm
    """ 
    if max_drawdowm == 0:
        return None

    if max_drawdowm <= 0:
        raise ValueError("max_drawdowm cannot be negative")
    return cagr / max_drawdowm

def calculate_market_exposure(exposures: Sequence[float]) -> float|None: 
    if len(exposures) == 0:
        raise ValueError("at least one exposure value is required")

    exposure_values = [
        float(exposure)
        for exposure in exposures
    ]

    if any(
        exposure < 0 for exposure in exposures 
    ): raise ValueError("exposure values cannot be negative")

    return statistics.fmean(exposure_values)

def calculate_performance_metrics(portfolio_records: Sequence[dict[str, Any]]) -> dict[str,float | None]:
    """calculate all perofrmance metrics from portfolio records"""
    if len(portfolio_records) < 3 : raise ValueError("at least three portfolio are required")

    values = [float(record["value"]) for record in portfolio_records]

    expsoure = [float(record["exposure"]) for record in portfolio_records]

    dates = [record['date'] for record in portfolio_records]

    start_date = portfolio_records[0]["date"]
    end_date = portfolio_records[-1]["date"]

    cagr = calculate_cagr_from_dates(
        values=values,
        start_date=start_date,
        end_date=end_date
    )

    max_drawdown = calculate_max_drawdown(values=values)
    drawdown_series = calculate_drawdown_series(values=values)
    drawdown_duration_series = calculate_drawdown_duration_series(dates=dates, drawdowns=drawdown_series)

    max_drawdown_duration = calculate_max_drawdown_duration(drawdown_duration_series)

    average_drawdown_duration = calculate_average_duration(drawdown_duration_series)

    

    return {
        "cumulative_return":(
            calculate_cumulative_return(values=values)
        ),
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "max_drawdown_duration_days":max_drawdown_duration,
        "average_drawdown_duration_days": average_drawdown_duration,
        "daily_sharpe": calculate_daily_sharpe(values=values),
        "calmar": calculate_calmar_ratio(cagr=cagr,max_drawdowm=max_drawdown),
        "market_exposure": calculate_market_exposure(exposures=expsoure),
    }


def calculate_drawdown_series(values:Sequence[float],) -> list[float]:
    """calculate positive drawdown at each portfolio obs"""

    if not values: raise ValueError("at least one portfolio value is required")

    peak = float(values[0])
    drawdowns: list[float] = []

    for value in values:
        current_value = float(value)

        if current_value <= 0: raise ValueError("portfolio values must be positive")

        peak = max(peak, current_value)

        drawdown = (peak - current_value) /peak

        drawdowns.append(drawdown)
    return drawdowns


def calculate_drawdown_duration_series(dates:Sequence[date], drawdowns:Sequence[float]) -> list[int]:
    """
    calcualte the number of calendar days spent below the latest peak
    a drawdown zero means portfolio is at a peak, so duration reset to zero
    """
    if len(dates) != len(drawdowns):
        raise ValueError("dates and drawdown must have same length")

    if not dates or not drawdowns:
        raise ValueError("dates and drawdowns must not be empty")
    
    peak_date = dates[0]
    durations: list[int] = []

    for current_date, drawdown in zip(dates, drawdowns):
        if drawdown == 0:
            peak_date = current_date
            durations.append(0)
        else:
            duration_days = (current_date - peak_date).days
            durations.append(duration_days)

    return durations


def calculate_max_drawdown_duration(durations:Sequence[int]) -> int :
    """
    Calculate the longest drawdown duration (in days) from a series
    of daily drawdown durations.
    """
    if not durations: raise ValueError("at least one duration value is required")
    return max(durations)

def calculate_average_duration(durations:Sequence[int]) -> int:
    """
    Calculate the average length of drawdown episodes.

    Each episode is a run of consecutive nonzero durations (bounded by
    zeros, which mark a return to peak). The episode's length is taken
    as its maximum duration value, then averaged across all episodes.
    """
    if not durations:
        raise ValueError("at least one duration value is required")

    episode_maxes = []
    current_max = 0

    for duration in durations:
        if duration == 0:
            if current_max > 0:
                episode_maxes.append(current_max)
            current_max = 0 
        else:
            current_max = max(current_max, duration)
    # handle case where series ends mid-drawdown
    if current_max >0:
        episode_maxes.append(current_max)
    if not episode_maxes:return 0.0

    return statistics.fmean(episode_maxes)
    