CREATE TABLE quant.backtest_metric (
    backtest_run_id BIGINT NOT NULL,
    final_value NUMERIC(20, 6) NOT NULL,
    cumulative_return NUMERIC(30, 15) NOT NULL,
    cagr NUMERIC(30, 15) NOT NULL,
    max_drawdown NUMERIC(30, 15) NOT NULL,
    daily_sharpe NUMERIC(30, 15),
    calmar NUMERIC(30, 15),
    market_exposure NUMERIC(30, 15) NOT NULL,
    max_drawdown_duration_days INTEGER NOT NULL,
    average_drawdown_duration_days NUMERIC(20, 6) NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT 
        pk_backtest_metric
    PRIMARY KEY 
        (backtest_run_id),

    CONSTRAINT 
        fk_backtest_metric_run
    FOREIGN KEY 
        (backtest_run_id)
    REFERENCES 
        quant.backtest_run (id)
    ON DELETE CASCADE,

    CONSTRAINT 
        ck_backtest_metric_final_value
    CHECK 
        (
            final_value > 0
            AND final_value <> 'NaN'::NUMERIC
        ),

    CONSTRAINT 
        ck_backtest_metric_cumulative_return
    CHECK 
        (
            cumulative_return > -1
            AND cumulative_return <> 'NaN'::NUMERIC
        ),

    CONSTRAINT 
        ck_backtest_metric_cagr
    CHECK  
        (
            cagr > -1
            AND cagr <> 'NaN'::NUMERIC
        ),

    CONSTRAINT 
        ck_backtest_metric_max_drawdown
    CHECK 
        (
            max_drawdown >= 0
            AND max_drawdown <= 1
            AND max_drawdown <> 'NaN'::NUMERIC
        ),

    CONSTRAINT 
        ck_backtest_metric_daily_sharpe
    CHECK
        (
            daily_sharpe IS NULL
            OR daily_sharpe <> 'NaN'::NUMERIC
        ),

    CONSTRAINT 
        ck_backtest_metric_calmar
    CHECK 
        (
            calmar IS NULL
            OR calmar <> 'NaN'::NUMERIC
        ),

    CONSTRAINT 
        ck_backtest_metric_market_exposure
    CHECK 
        (
            market_exposure >= 0
            AND market_exposure <> 'NaN'::NUMERIC
        ),

    CONSTRAINT 
        ck_backtest_metric_max_duration
    CHECK 
        (
            max_drawdown_duration_days >= 0
        ),

    CONSTRAINT 
        ck_backtest_metric_average_duration
    CHECK 
        (
            average_drawdown_duration_days >= 0
            AND average_drawdown_duration_days
                <= max_drawdown_duration_days
            AND average_drawdown_duration_days
                <> 'NaN'::NUMERIC
        )
);


COMMENT ON TABLE quant.backtest_metric IS
    'One immutable set of summary performance metrics per backtest run.';

COMMENT ON COLUMN quant.backtest_metric.backtest_run_id IS
    'Primary key and foreign key establishing a one-to-one relationship with backtest_run.';

COMMENT ON COLUMN quant.backtest_metric.final_value IS
    'Final portfolio value expressed in the asset or run currency.';

COMMENT ON COLUMN quant.backtest_metric.cumulative_return IS
    'Total decimal return; 0.10 represents 10 percent.';

COMMENT ON COLUMN quant.backtest_metric.cagr IS
    'Compound annual growth rate expressed as a decimal.';

COMMENT ON COLUMN quant.backtest_metric.max_drawdown IS
    'Maximum peak-to-trough drawdown stored as a positive decimal.';

COMMENT ON COLUMN quant.backtest_metric.daily_sharpe IS
    'Annualized Sharpe ratio calculated from daily returns; NULL when undefined.';

COMMENT ON COLUMN quant.backtest_metric.calmar IS
    'CAGR divided by maximum drawdown; NULL when maximum drawdown is zero.';

COMMENT ON COLUMN quant.backtest_metric.market_exposure IS
    'Average gross market exposure; values above one are permitted for leveraged strategies.';

COMMENT ON COLUMN quant.backtest_metric.max_drawdown_duration_days IS
    'Longest calendar-day period spent below a previous portfolio peak.';

COMMENT ON COLUMN quant.backtest_metric.average_drawdown_duration_days IS
    'Mean calendar-day duration across identified drawdown episodes.';