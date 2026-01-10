#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h db -U gymbot; do
  sleep 1
done

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
