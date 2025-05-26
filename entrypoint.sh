#!/bin/bash
set -e

echo "Running database migrations..."
poetry run alembic upgrade head 
echo "Migrations complete!"

echo "Starting FastAPI application..."
exec poetry run uvicorn luestilo_api.app:app --host 0.0.0.0 --port 8000