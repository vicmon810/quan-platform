CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE quant.backtest_run(
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    public_id UUID NOT NULL DEFAULT gen_random_uuid(),
    asset_id BIGINT NOT NULL,
    strategy_name VARCHAR(128) NOT NULL,
    strategy_version VARCHAR(64) NOT NULL DEFAULT '1',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL, 
    initial_cash NUMERIC(20,6) NOT NULL, 
    parameters JSONB NOT NULL DEFAULT '{}'::JSONB,
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
    engine_version VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,

    CONSTRAINT 
        pk_backtest_run 
    PRIMARY KEY 
        (id),

    CONSTRAINT 
        uq_backtest_run_public_id 
    UNIQUE 
        (public_id),

    CONSTRAINT 
        fk_backtest_run_asset 
    FOREIGN KEY 
        (asset_id) 
    REFERENCES 
        quant.asset(id)
    ON DELETE 
        RESTRICT,

    CONSTRAINT 
        ck_backtest_run_strategy_name_not_blank 
    CHECK
        (BTRIM(strategy_name)<>''),

    CONSTRAINT 
        ck_backtest_run_strategy_version_not_blank 
    CHECK
        (BTRIM(strategy_version)<>''),

    CONSTRAINT 
        ck_backtest_run_date_range 
    CHECK 
        (end_date > start_date),

    CONSTRAINT 
        ck_backtest_run_initial_cash 
    CHECK 
        (initial_cash > 0),

    CONSTRAINT 
        ck_backtest_run_parameters_object 
    CHECK 
        (JSONB_TYPEOF(parameters) = 'object'),

    CONSTRAINT 
        ck_backtest_run_status 
    CHECK 
        (
                                        status IN  
                                            (
                                                'PENDING',
                                                'RUNNING',
                                                'COMPLETED',
                                                'FAILED'
                                            )
                                        ),
    
    CONSTRAINT 
        ck_backtest_run_timestamp_order 
    CHECK(
                                                        (
                                                            started_at IS NULL 
                                                            OR started_at >= created_at
                                                        )
                                                        AND
                                                        (
                                                            completed_at IS NULL 
                                                            OR started_at IS NOT NULL
                                                        )
                                                        AND
                                                        (
                                                            completed_at IS NULL 
                                                            OR completed_at >= started_at
                                                        )
                                                    ),

    CONSTRAINT 
        ck_backtest_run_status_lifecycle
    CHECK 
        (
            (
                status = 'PENDING'
                AND started_at IS NULL
                AND completed_at IS NULL
                AND error_message IS NULL
            )
            OR 
            (
                status = 'RUNNING'
                AND started_at IS NOT NULL
                AND completed_at IS NULL 
                and error_message IS NULL 
            )
            OR
            (
                status = 'COMPLETED'
                AND started_at IS NOT NULL 
                AND completed_at IS NOT NULL 
                AND error_message IS NULL 
            )
            OR 
            (
                status = 'FAILED'
                AND started_at IS NOT NULL 
                AND completed_at IS NOT NULL 
                AND BTRIM
                    (
                     COALESCE(error_message, '')) <> ''
                    
            )
        )   
);


CREATE INDEX 
    idx_backtest_run_asset_created_at 
ON 
    quant.backtest_run(asset_id, created_at DESC);

CREATE INDEX
     idx_backtest_run_status_created_at 
ON 
    quant.backtest_run(status, created_at);

CREATE INDEX
     idx_backtest_run_strategy_created_at
ON 
    quant.backtest_run(strategy_name, created_at DESC);

CREATE TRIGGER 
    trg_backtest_run_set_updated_at 
BEFORE UPDATE ON 
    quant.backtest_run
FOR EACH ROW EXECUTE FUNCTION 
    quant.set_updated_at();

COMMENT ON TABLE
    quant.backtest_run 
IS
    'Configuration and execution lifecycle of one strategy backtest.';

COMMENT ON COLUMN
    quant.backtest_run.public_id 
IS
    'Non-sequential identifier safe to expose through an external API.';

COMMENT ON COLUMN 
    quant.backtest_run.asset_id 
IS
    'Canonical asset tested by this backtest run.';

COMMENT ON COLUMN
    quant.backtest_run.strategy_name 
IS
    'Stable machine-readable strategy identifier.';

COMMENT ON COLUMN 
    quant.backtest_run.strategy_version 
IS
    'Version of the strategy implementation used for reproducibility.';

COMMENT ON COLUMN 
    quant.backtest_run.parameters
IS
    'Strategy-specific parameters stored as a JSON object.';

COMMENT ON COLUMN 
    quant.backtest_run.engine_version 
IS
    'Application version or Git commit used to run the backtest.';

COMMENT ON COLUMN 
    quant.backtest_run.status 
IS
    'Execution state: PENDING, RUNNING, COMPLETED or FAILED.';

COMMENT ON COLUMN 
    quant.backtest_run.error_message 
IS
    'Failure reason; required only when status is FAILED.';