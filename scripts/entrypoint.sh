#!/bin/bash
set -e

echo "Starting Crypto Portfolio Tracker..."

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
