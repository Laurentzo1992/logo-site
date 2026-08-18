#!/bin/sh
set -e

if [ -n "$DB_HOST" ]; then
  echo "Waiting for database at $DB_HOST:${DB_PORT:-5432}..."
  until python - <<PYEOF
import os, socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect((os.environ["DB_HOST"], int(os.environ.get("DB_PORT", 5432))))
except OSError:
    sys.exit(1)
PYEOF
  do
    sleep 1
  done
  echo "Database is up."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
