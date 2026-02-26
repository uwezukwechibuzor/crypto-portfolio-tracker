#!/bin/bash
# Apply database migration to increase token_symbol column length

set -e

echo "====================================="
echo "Database Migration: Increase token_symbol length"
echo "====================================="
echo ""

# Check if we're running in Docker
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container..."
    DB_HOST="postgres"
else
    echo "Running on host machine..."
    DB_HOST="localhost"
fi

# Database connection details
DB_USER="${POSTGRES_USER:-postgres}"
DB_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
DB_NAME="${POSTGRES_DB:-crypto_portfolio}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "Connecting to database: $DB_NAME on $DB_HOST:$DB_PORT"
echo ""

# Apply migration
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -f /app/migrations/001_increase_token_symbol_length.sql

echo ""
echo "✅ Migration completed successfully!"
echo ""
