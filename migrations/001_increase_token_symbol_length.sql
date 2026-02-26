-- Migration: Increase token_symbol column length to support IBC denoms
-- Date: 2026-02-26
-- Description: IBC token denoms are 68 characters long (e.g., ibc/0025F8A87464A471E66B234C4F93AEC5B4DA3D42D7986451A059273426290DD5)
--              Increasing from VARCHAR(50) to VARCHAR(100) to accommodate them

-- Increase token_symbol length in balances table
ALTER TABLE balances ALTER COLUMN token_symbol TYPE VARCHAR(100);

-- Increase token_symbol length in balance_history table
ALTER TABLE balance_history ALTER COLUMN token_symbol TYPE VARCHAR(100);

-- Verify the changes
SELECT 
    table_name, 
    column_name, 
    character_maximum_length
FROM 
    information_schema.columns
WHERE 
    table_name IN ('balances', 'balance_history') 
    AND column_name = 'token_symbol';
