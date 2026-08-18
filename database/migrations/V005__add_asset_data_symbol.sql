ALTER TABLE 
    quant.asset
ADD 
    COLUMN data_symbol TEXT;
    
UPDATE 
    quant.asset
SET 
    data_symbol = symbol 
WHERE
    data_symbol IS NULL;


ALTER TABLE 
    quant.asset
ALTER COLUMN 
    data_symbol SET NOT NULL;

ALTER TABLE
    quant.asset
ADD CONSTRAINT
    ck_asset_data_symbol_non_blank
CHECK
    (btrim(data_symbol)<>'');