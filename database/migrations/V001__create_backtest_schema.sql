CREATE SCHEMA IF NOT EXISTS quant;

CREATE TABLE quant.asset (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    exchange_code VARCHAR(16) NOT NULL,
    symbol VARCHAR(32) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    asset_type VARCHAR(16) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT 
        pk_asset 
    PRIMARY KEY 
    (id),
    
    CONSTRAINT
        uq_asset_exchange_symbol 
    UNIQUE 
        (exchange_code, symbol),

    CONSTRAINT
        ck_asset_exchange_code_not_blank 
    CHECK
        (BTRIM(exchange_code)<>''),
    
    CONSTRAINT 
        ck_asset_exchange_code_uppercase 
    CHECK
        (exchange_code = UPPER(exchange_code)),
    CONSTRAINT 
        ck_asset_symbol_not_blank 
    CHECK
        (BTRIM(symbol)<> ''), 
    CONSTRAINT 
        ck_asset_symbol_uppercase 
    CHECK 
        (symbol = UPPER(symbol)),
    CONSTRAINT 
        ck_asset_display_name_not_blank 
    CHECK 
        (BTRIM(display_name) <> ''),
    CONSTRAINT 
        ck_asset_currency_code 
    CHECK 
        (currency_code ~ '[A-Z]{3}$'),
    CONSTRAINT 
        ck_asset_type 
    CHECK 
        (asset_type IN ('EQUITY', 'ETF'))
);

CREATE INDEX idx_asset_symbol ON quant.asset(symbol);

CREATE FUNCTION 
    quant.set_updated_at() 
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at:=CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_asset_set_updated_at
BEFORE UPDATE ON quant.asset 
FOR EACH ROW 
EXECUTE FUNCTION quant.set_updated_at();

COMMENT ON TABLE quant.asset IS 
    'Canonical asset master shared across supported exchanges.';

COMMENT ON COLUMN quant.asset.exchange_code is 
    'Internal uppercase exchange identifier such as NZX, ASX, NASDAQ or NYSE';

COMMENT ON COLUMN quant.asset.symbol IS 
    'Exchange local uppercase trading symbol';

COMMENT ON COLUMN quant.asset.currency_code IS
    'ISO 4217 currency code such as NZD, AUD or USD.';

COMMENT ON COLUMN quant.asset.asset_type IS
    'Supported instrument classification: EQUITY or ETF.';

COMMENT ON COLUMN quant.asset.is_active IS
    'False when the instrument is delisted or no longer available.';