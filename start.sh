#!/bin/sh

# Always copy the latest DB from the image to the persistent volume on deploy
echo "Syncing database to persistent volume..."
cp /app/nuclear_reactors.db /data/nuclear_reactors.db

exec gunicorn app:app --bind 0.0.0.0:8080 --workers 2 --timeout 120
