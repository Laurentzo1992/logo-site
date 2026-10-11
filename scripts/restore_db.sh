#!/bin/sh
# Restaure une sauvegarde Postgres (fichier .sql.gz produit par backup_db.sh
# ou par pg_dump | gzip) — à lancer depuis la racine du projet sur le VPS.
# Usage : ./scripts/restore_db.sh backups/logosite_20261010_030000.sql.gz
#   VPS dédié : COMPOSE_FILE=docker-compose.standalone.yml ./scripts/restore_db.sh <fichier>
#
# ATTENTION : remplace TOUT le contenu actuel de la base par celui de la sauvegarde.
set -e

FILE="$1"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "Usage : $0 <fichier.sql.gz>" >&2
  exit 1
fi
FILE=$(realpath "$FILE")

cd "$(dirname "$0")/.."

DB_USER=$(grep -E '^DB_USER=' .env | cut -d= -f2)
DB_NAME=$(grep -E '^DB_NAME=' .env | cut -d= -f2)
DB_USER=${DB_USER:-logosite}
DB_NAME=${DB_NAME:-logosite}
COMPOSE="docker compose -f ${COMPOSE_FILE:-docker-compose.prod.yml}"

printf "La base %s va être remplacée par %s. Continuer ? [o/N] " "$DB_NAME" "$FILE"
read -r answer
[ "$answer" = "o" ] || [ "$answer" = "O" ] || { echo "Annulé."; exit 1; }

# Sauvegarde de sécurité de l'état actuel avant d'écraser quoi que ce soit.
mkdir -p backups
SAFETY="backups/avant_restauration_$(date +%Y%m%d_%H%M%S).sql.gz"
$COMPOSE exec -T db pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$SAFETY"
echo "État actuel sauvegardé dans $SAFETY"

# On coupe l'application pendant la restauration.
$COMPOSE stop web cron

$COMPOSE exec -T db psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
gunzip -c "$FILE" | $COMPOSE exec -T db psql -q -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 > /dev/null

# Au redémarrage, web applique les migrations éventuellement plus récentes.
$COMPOSE start web cron
echo "Restauration terminée depuis $FILE"
