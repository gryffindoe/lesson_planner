#!/usr/bin/env sh
set -e

# Entry point: wait for DB, migrate, collectstatic, then run CMD
echo "Entrypoint starting"

MAX_RETRIES=${DB_WAIT_RETRIES:-30}
RETRY_DELAY=${DB_WAIT_DELAY:-1}
ATTEMPT=0

echo "Waiting for database (max ${MAX_RETRIES} attempts)..."
until python manage.py migrate --noinput 2>/dev/null; do
  ATTEMPT=$((ATTEMPT+1))
  if [ "$ATTEMPT" -ge "$MAX_RETRIES" ]; then
    echo "Reached max retries ($MAX_RETRIES) for database migrations; exiting"
    exit 1
  fi
  echo "Database unavailable - sleeping ${RETRY_DELAY}s (attempt ${ATTEMPT}/${MAX_RETRIES})"
  sleep ${RETRY_DELAY}
  # exponential backoff with cap
  RETRY_DELAY=$((RETRY_DELAY * 2))
  if [ $RETRY_DELAY -gt 30 ]; then
    RETRY_DELAY=30
  fi
done

echo "Database ready - migrations applied"

# Collect static files (non-fatal)
echo "Collecting static files"
python manage.py collectstatic --noinput || echo "collectstatic failed — continuing"

echo "Starting application: $@"
exec "$@"
