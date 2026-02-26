# Database Migration Guide

## Issue
IBC token denoms (e.g., `ibc/0025F8A87464A471E66B234C4F93AEC5B4DA3D42D7986451A059273426290DD5`) are 68 characters long, but the `token_symbol` column was limited to 50 characters, causing insertion errors.

## Solution
1. Increase `token_symbol` column length from 50 to 100 characters
2. Only fetch USD prices for native tokens (ATOM, TIA, ETH, SOL, etc.)
3. Store IBC tokens with their full denom identifier

## Migration Steps

### Option 1: Automatic Migration (Docker)

If using Docker, the easiest way is to recreate the containers:

```bash
# Stop and remove containers (data will be lost - see backup section below)
docker compose down -v

# Rebuild and start with updated schema
docker compose up --build -d
```

### Option 2: Manual Migration (Preserve Data)

If you want to keep existing data:

```bash
# Step 1: Backup existing data (optional but recommended)
docker exec crypto_portfolio_postgres pg_dump -U postgres crypto_portfolio > backup_$(date +%Y%m%d_%H%M%S).sql

# Step 2: Copy migration file to container
docker cp migrations/001_increase_token_symbol_length.sql crypto_portfolio_postgres:/tmp/

# Step 3: Run migration
docker exec -it crypto_portfolio_postgres psql -U postgres -d crypto_portfolio -f /tmp/001_increase_token_symbol_length.sql

# Step 4: Restart app container to apply model changes
docker compose restart app
```

### Option 3: Direct PostgreSQL Migration (Local Development)

If running PostgreSQL locally:

```bash
psql -U postgres -d crypto_portfolio -f migrations/001_increase_token_symbol_length.sql
```

## What Changed

### Database Schema
- `balances.token_symbol`: `VARCHAR(50)` → `VARCHAR(100)`
- `balance_history.token_symbol`: `VARCHAR(50)` → `VARCHAR(100)`

### Application Logic
- Only native tokens (ATOM, TIA, ETH, SOL, USDC, USDT, DAI, WETH, WBTC) get USD price lookups
- IBC tokens are stored with their full `ibc/` identifier without USD prices
- This prevents unnecessary CoinGecko API calls for unknown tokens

## Verification

After migration, test with a Cosmos wallet:

```bash
# Create a Cosmos wallet
curl -X POST http://localhost:8000/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "address": "cosmos1ufv79qxxndxsjlfn8ff5vte9pvzl84pcx6fz4d",
    "chain": "cosmos",
    "label": "Test Cosmos Wallet"
  }'

# Fetch balances (should now work with IBC tokens)
curl -X POST http://localhost:8000/api/v1/wallets/<WALLET_ID>/fetch \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": true}'
```

Expected result:
- Native token (ATOM) will have `usd_value`
- IBC tokens will have `usd_value: null` but will be stored successfully
- No database errors

## Rollback (if needed)

If you need to rollback:

```sql
-- Restore from backup
psql -U postgres -d crypto_portfolio < backup_YYYYMMDD_HHMMSS.sql

-- Or just reduce column size (may fail if IBC tokens exist)
ALTER TABLE balances ALTER COLUMN token_symbol TYPE VARCHAR(50);
ALTER TABLE balance_history ALTER COLUMN token_symbol TYPE VARCHAR(50);
```
