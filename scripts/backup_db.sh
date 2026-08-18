#!/bin/sh
# Sauvegarde de la base Postgres — à lancer depuis la racine du projet sur le VPS.
# Usage : ./scripts/backup_db.sh
# Conserve les 14 dernières sauvegardes dans ./backups/ (hors du repo git).
set -e

cd "$(dirname "$0")/.."
mkdir -p backups

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="backups/logosite_${TIMESTAMP}.sql.gz"

DB_USER=$(grep -E '^DB_USER=' .env | cut -d= -f2)
DB_NAME=$(grep -E '^DB_NAME=' .env | cut -d= -f2)

docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U "${DB_USER:-logosite}" "${DB_NAME:-logosite}" | gzip > "$FILE"

echo "Sauvegarde créée : $FILE"

# Garde uniquement les 14 dernières sauvegardes
ls -t backups/logosite_*.sql.gz 2>/dev/null | tail -n +15 | xargs -r rm --
