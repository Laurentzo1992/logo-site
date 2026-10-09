# Déploiement sur le VPS Ubuntu 26.04 (139.99.209.66)

Guide à suivre à la main pour installer logo-services.com sur le nouveau VPS,
en partant d'une base vide. Le serveur est organisé pour héberger **plusieurs
sites et applications** : un seul Caddy reçoit tout le trafic et le répartit.

Les commandes notées **[PC]** se lancent dans PowerShell sur ton ordinateur,
**[VPS]** sur le serveur.

---

## Organisation du serveur

```
/opt/
├── caddy/          ← Caddy partagé : HTTPS de TOUS les sites (ports 80/443)
│   ├── Caddyfile
│   └── sites/
│       ├── logo-services.caddy
│       └── <autre-site>.caddy      ← ajouté plus tard
├── logo-site/      ← ce dépôt (Django + Postgres + veille RSS)
└── <autre-app>/    ← chaque future application dans son propre dossier
```

```
Internet ──80/443──> Caddy ──réseau Docker "proxy"──> logo-site-web:8000
                                                 ├──> autre-app:3000
                                                 └──> ...
```

Règles communes à toutes les applications :
- seul Caddy ouvre des ports sur Internet ; les applications n'ont **pas** de `ports:` ;
- chaque application rejoint le réseau `proxy` avec un **alias unique** ;
- chaque application a sa propre base de données, dans son propre projet Compose.

---

## 1. Sécuriser l'accès et préparer le serveur

**[PC]**
```
ssh ubuntu@139.99.209.66
```

**[VPS]** Change d'abord le mot de passe de `ubuntu` :
```
passwd
```

Installe git, clone le dépôt et lance le script de préparation (Docker,
Docker Compose, pare-feu ufw, mises à jour de sécurité automatiques) :
```
sudo apt-get update && sudo apt-get install -y git
sudo mkdir -p /opt/logo-site && sudo chown $USER:$USER /opt/logo-site
git clone https://github.com/Laurentzo1992/logo-site.git /opt/logo-site
sudo sh /opt/logo-site/scripts/setup_vps.sh
exit
```
> Dépôt privé ? GitHub demandera un identifiant : ton nom d'utilisateur
> GitHub, et un *personal access token* (lecture seule) comme mot de passe.

> Si le script échoue sur `docker-compose-v2` (« Unable to locate package »),
> lance `sudo add-apt-repository -y universe` puis relance le script.

Reconnecte-toi (indispensable pour utiliser `docker` sans `sudo`) et vérifie :

**[PC]**
```
ssh ubuntu@139.99.209.66
```
**[VPS]**
```
docker --version
docker compose version
sudo ufw status
```
Le pare-feu doit autoriser `OpenSSH`, `80/tcp`, `443/tcp` et `443/udp`.

---

## 2. Installer le Caddy partagé (une seule fois)

**[VPS]**
```
docker network create proxy
sudo mkdir -p /opt/caddy && sudo chown $USER:$USER /opt/caddy
cp -r /opt/logo-site/deploy/caddy/. /opt/caddy/
nano /opt/caddy/Caddyfile
```
Dans le `Caddyfile`, vérifie l'adresse e-mail (Let's Encrypt l'utilise pour
prévenir en cas de problème de certificat). `Ctrl+O`, `Entrée`, `Ctrl+X`.

```
cd /opt/caddy
docker compose up -d
docker compose ps
```
Le conteneur `caddy` doit être `Up`. Tant que le DNS et le site ne sont pas
en place, ses logs contiendront des erreurs de certificat : c'est normal.

> `/opt/caddy` est indépendant du dépôt logo-site : les futures applications
> y ajoutent simplement leur fichier dans `sites/`.

---

## 3. Pointer le DNS vers le serveur

Chez ton registrar (OVH…), crée ou modifie les enregistrements :

| Nom | Type | Valeur |
|---|---|---|
| `logo-services.com` | A | `139.99.209.66` |
| `www.logo-services.com` | A | `139.99.209.66` |

Supprime les éventuels enregistrements `AAAA` (IPv6) ou `A` qui pointent
ailleurs. Vérifie la propagation depuis le **[PC]** :
```
nslookup logo-services.com
nslookup www.logo-services.com
```
Les deux doivent répondre `139.99.209.66` (quelques minutes à quelques heures).

---

## 4. Configurer logo-site (`.env`)

**[VPS]**
```
cd /opt/logo-site
cp .env.production.example .env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"
openssl rand -hex 24
nano .env
```
Dans `nano`, renseigne :
- `SECRET_KEY` : la ligne affichée par la commande `python3`
- `DB_PASSWORD` : la valeur affichée par `openssl`
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` : tes identifiants SMTP OVH

Laisse `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` et `USE_HTTPS=True` tels quels.
`Ctrl+O`, `Entrée`, `Ctrl+X`, puis :
```
chmod 600 .env
```

---

## 5. Démarrer logo-site

**[VPS]**
```
cd /opt/logo-site
export COMPOSE_FILE=docker-compose.standalone.yml
docker compose up -d --build
docker compose ps
docker compose logs web --tail 30
```
Les 3 conteneurs (`db`, `web`, `cron`) doivent être `Up`. Dans les logs de
`web`, tu dois voir les migrations puis `Listening at: http://0.0.0.0:8000`.
Le conteneur `cron` importe tout de suite les articles de veille RSS du blog.

Vérifie que Caddy voit le site sur le réseau `proxy` (doit afficher une IP) :
```
docker run --rm --network proxy busybox nslookup logo-site-web
```

Crée ton compte administrateur (pour `/admin/`) :
```
docker compose exec web python manage.py createsuperuser
```

---

## 6. Vérifier le HTTPS

**[VPS]**
```
cd /opt/caddy
docker compose logs -f caddy
```
Attends `certificate obtained successfully` pour `logo-services.com` et
`www.logo-services.com` (`Ctrl+C` pour quitter). Si le DNS n'était pas encore
propagé, Caddy réessaie tout seul ; tu peux forcer avec :
```
docker compose restart caddy
```

Dans le navigateur :
- https://logo-services.com → le site s'affiche ;
- https://www.logo-services.com → redirige vers https://logo-services.com ;
- https://logo-services.com/admin/ → connexion avec le compte créé à l'étape 5.

Il te reste à saisir le contenu dans l'admin : services, coordonnées
(*Contact*), page « Qui sommes-nous », projets du catalogue.

---

## 7. Sauvegarde automatique quotidienne

**[VPS]**
```
crontab -e
```
Ajoute cette ligne (sauvegarde chaque nuit à 3 h, 14 jours conservés dans
`/opt/logo-site/backups/`) :
```
0 3 * * * cd /opt/logo-site && COMPOSE_FILE=docker-compose.standalone.yml sh scripts/backup_db.sh >> backups/backup.log 2>&1
```
Copie régulièrement ces sauvegardes hors du serveur, depuis le **[PC]** :
```
scp -r ubuntu@139.99.209.66:/opt/logo-site/backups .
```

---

## 8. Mettre à jour logo-site

**[VPS]**
```
cd /opt/logo-site
git pull
docker compose -f docker-compose.standalone.yml up -d --build
```
Les migrations et le `collectstatic` se lancent automatiquement au démarrage
de `web`. Les autres sites ne sont pas touchés.

---

## 9. Ajouter un autre site ou une autre application

Exemple : une application `mon-app` sur `mon-app.com`, qui écoute sur le port 3000
dans son conteneur.

**a. Déposer l'application** dans son propre dossier :
```
sudo mkdir -p /opt/mon-app && sudo chown $USER:$USER /opt/mon-app
git clone <url-du-depot> /opt/mon-app
```

**b. Dans son `docker-compose.yml`**, le service web n'a **pas** de `ports:`
et rejoint le réseau `proxy` avec un alias unique :
```yaml
services:
  app:
    build: .
    restart: unless-stopped
    networks:
      default:
      proxy:
        aliases:
          - mon-app-web

networks:
  default:
  proxy:
    external: true
```
Si elle a une base de données, celle-ci reste sur le réseau `default` du
projet (jamais sur `proxy`, jamais de `ports:`).

**c. Démarrer l'application :**
```
cd /opt/mon-app
docker compose up -d --build
```

**d. Déclarer le domaine dans Caddy** : crée `/opt/caddy/sites/mon-app.caddy` :
```
mon-app.com {
	encode zstd gzip
	reverse_proxy mon-app-web:3000
}
```
Variantes utiles :
```
# Sous-domaine
app.logo-services.com {
	reverse_proxy mon-app-web:3000
}

# www qui redirige vers le domaine principal
www.mon-app.com {
	redir https://mon-app.com{uri} permanent
}
```

**e. DNS** : enregistrement `A` du domaine → `139.99.209.66`.

**f. Recharger Caddy** (sans coupure pour les autres sites) :
```
cd /opt/caddy
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```
Le certificat HTTPS du nouveau domaine est obtenu automatiquement.

> Un site purement statique (HTML/CSS) n'a même pas besoin de conteneur :
> mets ses fichiers dans `/opt/caddy/www/mon-site`, monte ce dossier dans le
> conteneur Caddy (`- ./www:/srv:ro` dans `/opt/caddy/docker-compose.yml`,
> puis `docker compose up -d`) et utilise :
> ```
> mon-site.com {
> 	root * /srv/mon-site
> 	file_server
> }
> ```

---

## Commandes utiles

```
# logo-site
cd /opt/logo-site && export COMPOSE_FILE=docker-compose.standalone.yml
docker compose ps
docker compose logs -f web
docker compose restart web

# Caddy (tous les sites)
cd /opt/caddy
docker compose logs -f caddy
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile

# Vue d'ensemble du serveur
docker ps                                  # tous les conteneurs
docker network inspect proxy --format '{{range .Containers}}{{.Name}} {{end}}'
df -h && docker system df                  # espace disque
docker image prune -f                      # supprimer les anciennes images après les mises à jour
```
