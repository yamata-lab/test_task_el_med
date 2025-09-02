#!/bin/sh

# This script serves as the Docker container's entrypoint.
# Its primary function is to ensure the database is available
# before applying migrations and starting the main application process.
# This approach prevents a common race condition in docker-compose setups.

DB_HOST=${DATABASE_HOST:-db}
DB_PORT=${DATABASE_PORT:-5432}

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

# Block execution until the database TCP connection is successfully established.
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "PostgreSQL started"

# Apply database migrations.
echo "Running database migrations..."
python manage.py migrate --noinput

# Replace the current shell process with the command passed to the script (e.g., gunicorn).
# Using 'exec' is crucial for ensuring that the main application process becomes PID 1,
# allowing it to receive signals (like SIGTERM) from the Docker daemon correctly.
exec "$@"
