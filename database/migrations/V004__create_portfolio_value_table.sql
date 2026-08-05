CREATE TABLE IF NOT EXISTS quant.portfolio_value(
    backtest_run_id BIGINT NOT NULL,
    trading_date DATE NOT NULL, 

    portfolio_value NUMERIC(20,6) NOT NULL, 
    market_exposure NUMERIC(30,15) NOT NULL, 
    drawdown NUMERIC(30,15) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_portfolio_value_backtest_run
    FOREIGN KEY (backtest_run_id)
    REFERENCES quant.backtest_run(id)
    ON DELETE CASCADE,

    CONSTRAINT ck_portfolio_value_positive
    CHECK (portfolio_value > 0 
    AND portfolio_value <> 'NaN'::NUMERIC),

    CONSTRAINT ck_portfolio_value_market_exposure
    CHECK( market_exposure >= 0
    AND market_exposure <> 'NaN'::NUMERIC),

    CONSTRAINT ck_portfolio_value_drawdown
    CHECK (drawdown >= 0
    AND drawdown <=1
    AND drawdown <> 'NaN'::NUMERIC),

    CONSTRAINT uq_portfolio_value_run_date
    UNIQUE (backtest_run_id, trading_date)
);

COMMENT ON TABLE quant.portfolio_value IS
    'Daily portfolio value, gross market exposure and drawdown for a backtest run.';

COMMENT ON COLUMN quant.portfolio_value.backtest_run_id IS
    'Backtest run that generated this daily portfolio observation.';

COMMENT ON COLUMN quant.portfolio_value.trading_date IS
    'Trading date represented by this portfolio observation.';

COMMENT ON COLUMN quant.portfolio_value.portfolio_value IS
    'End-of-day portfolio value in the backtest run currency.';

COMMENT ON COLUMN quant.portfolio_value.market_exposure IS
    'Gross market exposure stored as a decimal; values above one are allowed.';

COMMENT ON COLUMN quant.portfolio_value.drawdown IS
    'Positive drawdown from the previous portfolio peak; 0.25 represents 25 percent.';

COMMENT ON COLUMN quant.portfolio_value.created_at IS
    'Timestamp when this result row was persisted.';