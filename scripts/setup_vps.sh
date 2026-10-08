#!/bin/sh
# Préparation d'un VPS Ubuntu 26.04 neuf pour héberger le site
# (docker-compose.standalone.yml). À lancer une seule fois, en root ou via sudo :
#   sudo sh scripts/setup_vps.sh
# Idempotent : peut être relancé sans risque.
set -e

if [ "$(id -u)" -ne 0 ]; then
  echo "À lancer en root (sudo sh scripts/setup_vps.sh)" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get upgrade -y

# Docker et le plugin "docker compose" depuis les dépôts Ubuntu.
apt-get install -y docker.io docker-compose-v2 git ufw unattended-upgrades
systemctl enable --now docker

# Utilisateur qui a lancé sudo -> groupe docker (pas besoin de sudo ensuite).
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
  usermod -aG docker "$SUDO_USER"
fi

# Pare-feu : SSH + HTTP/HTTPS (443/udp pour HTTP/3). On autorise SSH AVANT
# d'activer ufw pour ne pas couper la session en cours.
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp
ufw --force enable

# Mises à jour de sécurité automatiques.
dpkg-reconfigure -f noninteractive unattended-upgrades

echo
echo "VPS prêt. Docker : $(docker --version)"
echo "Déconnecte-toi puis reconnecte-toi pour utiliser docker sans sudo."
