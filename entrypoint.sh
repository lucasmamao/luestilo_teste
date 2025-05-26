#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z luestilo_database 5432; do
  sleep 0.5
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
poetry run alembic upgrade head
echo "Migrations complete!"

echo "Starting FastAPI application..."
exec poetry run uvicorn luestilo_api.app:app --host 0.0.0.0 --port 8000