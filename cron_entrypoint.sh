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

INTERVAL="${FETCH_NEWS_INTERVAL_SECONDS:-3600}"
echo "Veille blog : récupération des flux RSS toutes les ${INTERVAL}s"

while true; do
  python manage.py fetch_news || echo "fetch_news a échoué, nouvel essai au prochain cycle"
  sleep "$INTERVAL"
done
