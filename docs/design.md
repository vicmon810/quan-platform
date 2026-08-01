# Strategy Evaluation and Walk-Forward Design

Date: 2026-08-01

## 1. Objective

Build a reliable evaluation layer for the quant platform before adding more strategies or news sentiment features.

The system must answer:

- Which strategy produces the highest cumulative and annualised return?
- Which strategy has the lowest maximum drawdown?
- Which strategy delivers the best return relative to drawdown?
- How much time does each strategy spend invested?
- How many trades does each strategy complete?
- Do parameters selected on the training period remain effective on unseen test data?

Initial strategies:

- BuyAndHold
- MovingAverageCross
- TimeSeriesMomentum

## 2. Scope

This phase includes:

1. A reusable metrics module.
2. Exposure-aware portfolio value recording.
3. A strategy comparison report.
4. Walk-forward validation with separate training and testing periods.
5. Automated tests for metrics and report inputs.

This phase excludes:

- News collection.
- Sentiment analysis.
- LLM-generated trading signals.
- Live trading.
- Portfolio optimisation across multiple simultaneous assets.

## 3. Architecture

### 3.1 `src/analyzers.py`

`PortfolioValueAnalyzer` records one row per trading day:

- `date`
- `value`
- `exposure`

For a single-asset long-only strategy:

- `exposure = position market value / portfolio value`
- `exposure = 0` while holding cash
- `exposure` is normally between 0 and 1

The analyzer records raw observations only. It does not calculate summary statistics.

### 3.2 `src/metrics.py`

This module accepts the daily portfolio observations and calculates:

- cumulative return
- CAGR
- maximum drawdown
- daily annualised Sharpe ratio
- Calmar ratio
- average market exposure
- completed trade count

Functions remain independent from Backtrader where possible. Inputs should be plain Python collections or pandas objects so the calculations can be tested without running a backtest.

### 3.3 `src/engine.py`

The engine remains responsible for:

- validating ticker and date inputs
- loading price data
- configuring Cerebro
- adding a strategy
- adding analyzers
- setting cash and commission
- executing the backtest
- returning raw backtest results

The engine should not contain reporting or plotting logic.

### 3.4 `backtests/run_strategy_report.py`

This script runs the three initial strategies over the same ticker, date range, starting capital and commission assumptions.

Outputs:

- `reports/strategy_summary.csv`
- `reports/strategy_equity_curve.png`
- `reports/strategy_drawdown.png`

The CSV contains one row per strategy with consistent fields.

### 3.5 `backtests/run_walk_forward.py`

This script performs two distinct phases:

Training period:

- evaluate candidate MovingAverageCross parameters
- evaluate candidate TimeSeriesMomentum parameters
- select parameters using Calmar ratio as the primary objective
- use daily Sharpe as a secondary diagnostic

Testing period:

- freeze the selected parameters
- run each strategy once on unseen data
- compare results with BuyAndHold

No test-period information may influence parameter selection.

## 4. Data Flow

```text
Price CSV
  -> engine.py
  -> Backtrader strategy execution
  -> PortfolioValueAnalyzer daily observations
  -> metrics.py
  -> summary DataFrame
  -> CSV and plots
```

Walk-forward data flow:

```text
Training data
  -> parameter candidates
  -> training metrics
  -> selected frozen parameters

Test data
  -> frozen strategy parameters
  -> out-of-sample metrics
  -> comparison with BuyAndHold
```

## 5. Metric Definitions

### Cumulative Return

`final_value / initial_value - 1`

### CAGR

`(final_value / initial_value) ** (365.25 / elapsed_days) - 1`

Return `None` when elapsed time is not positive or initial value is not positive.

### Maximum Drawdown

Calculate the running peak of portfolio value and the percentage decline from each peak. Report maximum drawdown as a positive percentage magnitude.

### Daily Sharpe Ratio

Calculate daily percentage returns from portfolio values.

`sqrt(252) * mean(daily_returns) / std(daily_returns)`

Initially use zero risk-free rate. Return `None` when there are fewer than two returns or volatility is zero.

### Calmar Ratio

`CAGR / maximum_drawdown`

Both values use decimal form internally. Return `None` when maximum drawdown is zero or unavailable.

### Market Exposure

Average daily exposure across the backtest period.

For the initial single-asset long-only implementation, exposure should normally be between 0 and 1.

### Trade Count

Number of closed trades from Backtrader TradeAnalyzer.

## 6. Error Handling

Raise clear errors at the platform boundary:

- empty ticker -> `ValueError`
- invalid year range -> `ValueError`
- missing CSV -> `FileNotFoundError`
- empty portfolio value series -> `ValueError` in metrics functions where calculation is impossible
- malformed observation rows -> `ValueError`
- no valid parameter candidates -> `RuntimeError`

Do not rely on deep Backtrader exceptions for expected input errors.

## 7. Testing Strategy

### Metrics unit tests

Use deterministic synthetic portfolio values to test:

- cumulative return
- CAGR
- maximum drawdown
- Sharpe handling for constant returns
- Calmar handling when drawdown is zero
- average exposure

### Analyzer integration tests

Use synthetic rising and falling OHLCV data to verify:

- daily observations are recorded
- exposure is zero before entry
- exposure becomes positive after entry
- portfolio values remain ordered by date

### Report integration test

Run the strategy report against temporary synthetic CSV files and verify:

- one summary row per strategy
- expected output columns exist
- output files are created

### Walk-forward tests

Verify:

- training and test periods do not overlap incorrectly
- selected parameters come only from training results
- test execution receives frozen parameters

## 8. Initial Experimental Configuration

Ticker: `SPY`

Comparison period: 2020-01-01 to 2025-01-01

Walk-forward split:

- training: 2020-01-01 to 2023-01-01
- testing: 2023-01-01 to 2025-01-01

Starting cash: 100,000

Commission: 0.1% per transaction

Candidate MovingAverageCross parameters:

- fast: 5, 10, 15, 20, 25, 30
- slow: 40, 50, 60, 70, 80, 90, 100
- reject combinations where fast >= slow

Candidate TimeSeriesMomentum parameters:

- lookback: 63, 126, 252
- threshold: 0.00, 0.05, 0.10, 0.15

## 9. Acceptance Criteria

The phase is complete when:

1. Metrics functions have deterministic automated tests.
2. All existing tests still pass.
3. The analyzer records portfolio value and exposure for every processed date.
4. The report compares BuyAndHold, MovingAverageCross and TimeSeriesMomentum using identical assumptions.
5. The report produces summary CSV, equity curve and drawdown plot.
6. Walk-forward parameter selection uses training data only.
7. Out-of-sample results are clearly separated from training results.
8. No strategy is declared successful solely because final value exceeds starting cash.

## 10. Future Extension

After this phase is validated, add news sentiment as a separate factor and compare:

- price-only momentum
- sentiment-only signal
- momentum plus sentiment

The sentiment feature must demonstrate incremental out-of-sample value over the price-only baseline.