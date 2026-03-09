#!/bin/sh

# Seed the persistent volume with the DB on first deploy
if [ ! -f /data/nuclear_reactors.db ]; then
    echo "First deploy: copying database to volume..."
    cp /app/nuclear_reactors.db /data/nuclear_reactors.db
fi

exec gunicorn app:app --bind 0.0.0.0:8080 --workers 2 --timeout 120
