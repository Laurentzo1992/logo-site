# Caddy partagé du VPS

Un seul Caddy (dans `/opt/caddy` sur le serveur) reçoit tout le trafic
HTTP/HTTPS et le répartit entre les plateformes. Chaque plateforme tourne
dans son propre projet Docker Compose et n'ouvre aucun port sur Internet.

```
Internet ──80/443──> Caddy (/opt/caddy) ──réseau "proxy"──> logo-site-web:8000
                                                       ├──> autre-plateforme:3000
                                                       └──> ...
```

## Ajouter une nouvelle plateforme

1. Dans le `docker-compose.yml` de la plateforme, branche le service exposé
   sur le réseau `proxy` avec un **alias unique** (les noms de service comme
   `web` ou `app` se répètent d'un projet à l'autre, l'alias évite les
   collisions) :

   ```yaml
   services:
     app:
       # ... pas de "ports:" : seul Caddy est exposé
       networks:
         default:
         proxy:
           aliases:
             - ma-plateforme-app

   networks:
     default:
     proxy:
       external: true
   ```

2. Crée `/opt/caddy/sites/ma-plateforme.caddy` :

   ```
   ma-plateforme.com {
   	encode zstd gzip
   	reverse_proxy ma-plateforme-app:3000
   }
   ```

3. Fais pointer le DNS du domaine (enregistrement `A`) vers l'IP du VPS.

4. Recharge Caddy, sans coupure pour les autres sites :

   ```
   cd /opt/caddy
   docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
   ```

Caddy obtient le certificat HTTPS du nouveau domaine automatiquement.

## Commandes utiles

```
cd /opt/caddy
docker compose logs -f caddy                                         # logs / certificats
docker compose exec caddy caddy validate --config /etc/caddy/Caddyfile  # vérifier la config
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile    # appliquer la config
```
