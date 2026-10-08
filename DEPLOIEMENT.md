# Déploiement sur un VPS Ubuntu 26.04 dédié

Procédure manuelle pour installer logo-services.com sur le nouveau VPS
(`139.99.209.66`) et y migrer les données de l'ancien serveur (VPS kbot,
`51.178.251.73`). Toutes les commandes se tapent à la main.

Les commandes notées **[PC]** se lancent dans PowerShell sur ton ordinateur,
**[ANCIEN]** sur l'ancien VPS, **[NOUVEAU]** sur le nouveau.

Remplace `ubuntu` par ton nom d'utilisateur réel si besoin.

---

## 0. La veille : baisser le TTL DNS

Chez ton registrar (OVH…), passe le TTL des enregistrements `A` de
`logo-services.com` et `www.logo-services.com` à 300 secondes. La bascule
du jour J se propagera ainsi en quelques minutes.

---

## 1. Préparer le nouveau VPS

**[PC]**
```
ssh ubuntu@139.99.209.66
```

**[NOUVEAU]** Cloner le dépôt et lancer le script d'installation
(Docker, docker compose, pare-feu ufw, mises à jour de sécurité auto) :
```
sudo apt-get update && sudo apt-get install -y git
sudo mkdir -p /opt/logo-site && sudo chown $USER:$USER /opt/logo-site
git clone https://github.com/Laurentzo1992/logo-site.git /opt/logo-site
cd /opt/logo-site
sudo sh scripts/setup_vps.sh
exit
```
> Dépôt privé ? GitHub demandera un identifiant : utilise ton nom
> d'utilisateur et un *personal access token* (lecture seule) comme mot de passe.

Reconnecte-toi (nécessaire pour utiliser `docker` sans `sudo`) puis vérifie :
```
ssh ubuntu@139.99.209.66
docker compose version
sudo ufw status
```
Le pare-feu doit autoriser `OpenSSH`, `80/tcp`, `443/tcp` et `443/udp`.

---

## 1 bis. Installer le Caddy partagé (une seule fois par serveur)

Un seul Caddy, dans `/opt/caddy`, sert **toutes** les plateformes du VPS
(logo-services.com aujourd'hui, les autres plus tard) et gère leurs
certificats HTTPS. Les plateformes s'y branchent via le réseau Docker `proxy`.
Pour en ajouter une plus tard, voir [deploy/caddy/README.md](deploy/caddy/README.md).

**[NOUVEAU]**
```
docker network create proxy
sudo mkdir -p /opt/caddy && sudo chown $USER:$USER /opt/caddy
cp -r /opt/logo-site/deploy/caddy/. /opt/caddy/
cd /opt/caddy
docker compose up -d
docker compose ps
```
Le conteneur `caddy` doit être `Up`. Tant que le site et le DNS ne sont pas en
place, ses logs contiendront des erreurs de certificat : c'est normal.

> `/opt/caddy` est désormais indépendant du dépôt : les futures plateformes y
> ajoutent leur fichier dans `sites/` sans toucher à logo-site.

---

## 2. Créer le fichier `.env` de production

**[NOUVEAU]**
```
cd /opt/logo-site
cp .env.production.example .env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
openssl rand -hex 24
nano .env
```
Dans `nano`, renseigne :
- `SECRET_KEY` : la ligne affichée par la commande `python3`
- `DB_PASSWORD` : la valeur affichée par `openssl` (ou reprends celle de l'ancien
  serveur, au choix — la base est recréée de toute façon)
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` : tes identifiants SMTP OVH
  (tu peux les copier depuis le `.env` de l'ancien serveur)

Enregistre avec `Ctrl+O`, `Entrée`, puis quitte avec `Ctrl+X`.
```
chmod 600 .env
```

---

## 3. Exporter les données de l'ancien serveur

**[PC]**
```
ssh ubuntu@51.178.251.73
```

**[ANCIEN]** Va dans le dossier du site (celui qui contient
`docker-compose.prod.yml` — adapte le chemin) :
```
cd /chemin/vers/logo-site
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U logosite --no-owner logosite | gzip > ~/logosite.sql.gz
docker compose -f docker-compose.prod.yml exec -T web tar czf - -C /app/logosite/static/images . > ~/media.tar.gz
ls -lh ~/logosite.sql.gz ~/media.tar.gz
exit
```
> Si `DB_USER` / `DB_NAME` sont différents dans le `.env` de l'ancien serveur,
> remplace `logosite` dans la commande `pg_dump`.

---

## 4. Transférer les fichiers vers le nouveau serveur

**[PC]** (en passant par ton ordinateur)
```
scp ubuntu@51.178.251.73:~/logosite.sql.gz ubuntu@51.178.251.73:~/media.tar.gz .
scp logosite.sql.gz media.tar.gz ubuntu@139.99.209.66:~/
```

---

## 5. Restaurer les données sur le nouveau serveur

**[PC]**
```
ssh ubuntu@139.99.209.66
```

**[NOUVEAU]**
```
cd /opt/logo-site
export COMPOSE_FILE=docker-compose.standalone.yml

# Construire les images et démarrer uniquement la base
docker compose build
docker compose up -d db
docker compose ps        # attendre que db soit "healthy"

# Restaurer la base (dans une base encore vide, avant tout "migrate")
gunzip -c ~/logosite.sql.gz | docker compose exec -T db psql -U logosite -d logosite -v ON_ERROR_STOP=1

# Restaurer les images uploadées (partenaires, vignettes du blog…)
docker compose run --rm --no-deps -T --entrypoint sh web -c "tar xzf - -C /app/logosite/static/images" < ~/media.tar.gz
```

---

## 6. Démarrer le site

**[NOUVEAU]**
```
docker compose up -d
docker compose ps
docker compose logs web --tail 30
```
Les 3 conteneurs (`db`, `web`, `cron`) doivent être `Up`. Dans les logs de
`web`, tu dois voir `Listening at: http://0.0.0.0:8000`.

Vérifie que Caddy voit bien le site sur le réseau `proxy` (doit afficher une IP) :
```
docker run --rm --network proxy busybox nslookup logo-site-web
```

Test de Django avant la bascule DNS (doit afficher `200`) :
```
docker compose exec web python -c "import urllib.request as u; print(u.urlopen(u.Request('http://localhost:8000/', headers={'Host': 'logo-services.com', 'X-Forwarded-Proto': 'https'})).status)"
```

Tant que le DNS pointe encore vers l'ancien serveur, Caddy affichera des
erreurs de certificat dans ses logs : c'est normal, il réessaiera tout seul.

---

## 7. Bascule DNS

Chez ton registrar, modifie les enregistrements `A` :

| Nom | Type | Valeur |
|---|---|---|
| `logo-services.com` | A | `139.99.209.66` |
| `www.logo-services.com` | A | `139.99.209.66` |

Supprime les éventuels enregistrements `AAAA` (IPv6) qui pointent vers l'ancien serveur.

Vérifie la propagation depuis le **[PC]** :
```
nslookup logo-services.com
```

Puis sur le **[NOUVEAU]**, regarde Caddy obtenir le certificat :
```
cd /opt/caddy
docker compose logs -f caddy
```
Attends une ligne `certificate obtained successfully` pour les deux domaines
(`Ctrl+C` pour quitter), puis ouvre https://logo-services.com dans le navigateur.
https://www.logo-services.com doit rediriger vers https://logo-services.com.

---

## 8. Nettoyer l'ancien serveur

Une fois le nouveau site vérifié (pages, admin, formulaire de contact) :

**[ANCIEN]**
1. Retire le bloc `logo-services.com, www.logo-services.com { ... }` de
   `/opt/kbot/Caddyfile`, puis recharge le Caddy de kbot :
   ```
   cd /opt/kbot
   docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
   ```
   (adapte `caddy` au nom du service Caddy dans le compose de kbot)
2. Arrête les conteneurs du site (les volumes sont conservés par sécurité) :
   ```
   cd /chemin/vers/logo-site
   docker compose -f docker-compose.prod.yml down
   ```
3. Supprime les fichiers d'export : `rm ~/logosite.sql.gz ~/media.tar.gz`

Sur le **[NOUVEAU]** aussi : `rm ~/logosite.sql.gz ~/media.tar.gz`.
Sur le **[PC]**, supprime les deux fichiers téléchargés.

---

## 9. Sauvegarde automatique quotidienne

**[NOUVEAU]**
```
crontab -e
```
Ajoute cette ligne (sauvegarde chaque nuit à 3 h, 14 jours conservés dans
`/opt/logo-site/backups/`) :
```
0 3 * * * cd /opt/logo-site && COMPOSE_FILE=docker-compose.standalone.yml sh scripts/backup_db.sh >> backups/backup.log 2>&1
```
Pense à copier régulièrement ces sauvegardes hors du serveur (sur ton PC, par
exemple avec `scp`).

---

## Mises à jour du site par la suite

**[NOUVEAU]**
```
cd /opt/logo-site
git pull
docker compose -f docker-compose.standalone.yml up -d --build
```
Les migrations et le `collectstatic` sont lancés automatiquement au
démarrage du conteneur `web`.

## Commandes utiles

```
cd /opt/logo-site
export COMPOSE_FILE=docker-compose.standalone.yml
docker compose ps                                     # état des conteneurs
docker compose logs -f web                            # logs Django
docker compose exec web python manage.py createsuperuser
docker compose restart web
```
