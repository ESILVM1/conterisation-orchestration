#!/bin/bash
set -e

# Ensure db directory exists with correct permissions for SQLite
mkdir -p /app/db
chmod 777 /app/db 2>/dev/null || true

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

exec "$@"
