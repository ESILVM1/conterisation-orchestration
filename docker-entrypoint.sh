#!/bin/bash
set -e

# Attendre que la base de données soit prête (si PostgreSQL)
if [ "$DATABASE" = "postgresql" ]; then
    echo "Waiting for postgres..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done
    echo "PostgreSQL started"
fi

# Exécuter les migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Exécuter la commande passée en argument
exec "$@"

