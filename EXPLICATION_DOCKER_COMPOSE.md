# Explication : docker-compose.yml

## 🎯 À quoi sert ce fichier ?

Le `docker-compose.yml` permet de **définir et orchestrer plusieurs conteneurs Docker** ensemble. Au lieu de lancer chaque conteneur manuellement, vous lancez tout d'un coup avec une seule commande.

## 📋 Services définis

### 1. **Service `db`** (PostgreSQL)
```yaml
db:
  image: postgres:13-alpine
```
- **Rôle :** Base de données PostgreSQL
- **Port :** 5432 (exposé sur la machine hôte)
- **Volume :** Persiste les données dans `postgres_data`
- **Healthcheck :** Vérifie que la DB est prête avant de démarrer les autres services

### 2. **Service `web`** (Django)
```yaml
web:
  build: .
  command: gunicorn ...
```
- **Rôle :** Application Django avec Gunicorn
- **Port :** 8000 (exposé sur la machine hôte)
- **Dépendances :** Attend que `db` soit healthy
- **Volumes :** 
  - Code source (développement)
  - Fichiers statiques
  - Images/media

### 3. **Service `nginx`** (Reverse Proxy)
```yaml
nginx:
  image: nginx:alpine
```
- **Rôle :** Serveur web qui sert les fichiers statiques et reverse proxy
- **Ports :** 80 (HTTP) et 443 (HTTPS)
- **Dépendances :** Attend que `web` soit démarré

## 🔄 Architecture

```
Internet
   ↓
Nginx (port 80/443)
   ↓
Django/Gunicorn (port 8000)
   ↓
PostgreSQL (port 5432)
```

## 📝 Variables d'environnement

### Variables par défaut
```yaml
DB_NAME: ecommerce_db
DB_USER: django_user
DB_PASSWORD: django_pass
```

### Surcharge avec `.env`
Créez un fichier `.env` :
```bash
DB_NAME=mon_db
DB_USER=mon_user
DB_PASSWORD=mon_password_secret
```

## 🚀 Commandes utiles

### Démarrer tous les services
```bash
docker-compose up -d
```

### Voir les logs
```bash
docker-compose logs -f web
```

### Arrêter tous les services
```bash
docker-compose down
```

### Reconstruire après modification
```bash
docker-compose up -d --build
```

### Accéder au shell du conteneur web
```bash
docker-compose exec web bash
```

### Exécuter une commande Django
```bash
docker-compose exec web python manage.py createsuperuser
```

## 🔧 Volumes

### `postgres_data`
- **Type :** Volume nommé
- **Rôle :** Persiste les données de la base de données
- **Avantage :** Les données survivent au redémarrage des conteneurs

### `static_volume` et `media_volume`
- **Type :** Volumes nommés
- **Rôle :** Stockent les fichiers statiques et médias
- **Partagés :** Entre `web` et `nginx`

## 🌐 Réseau

### `ecommerce_network`
- **Type :** Bridge network
- **Rôle :** Permet aux conteneurs de communiquer entre eux
- **Isolation :** Les conteneurs sont isolés du reste du système

## ⚙️ Healthcheck

Le service `db` a un healthcheck :
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U django_user"]
```
- **Rôle :** Vérifie que PostgreSQL est prêt
- **Impact :** `web` attend que `db` soit healthy avant de démarrer
- **Avantage :** Évite les erreurs de connexion

## 🔒 Sécurité

1. **Variables d'environnement :** Secrets dans `.env` (non commité)
2. **Utilisateur non-root :** Conteneurs exécutés avec utilisateur limité
3. **Réseau isolé :** Communication interne uniquement
4. **Volumes nommés :** Données persistantes sécurisées

## 📊 Exemple d'utilisation complète

```bash
# 1. Créer le fichier .env
echo "SECRET_KEY=ma-cle-secrete" > .env
echo "DB_PASSWORD=mon-password" >> .env

# 2. Démarrer tous les services
docker-compose up -d

# 3. Vérifier que tout fonctionne
docker-compose ps

# 4. Voir les logs
docker-compose logs -f

# 5. Accéder à l'application
# http://localhost (via Nginx)
# ou http://localhost:8000 (directement Django)
```

## 💡 Avantages

✅ **Simplicité :** Une commande pour tout démarrer  
✅ **Orchestration :** Gestion automatique des dépendances  
✅ **Isolation :** Chaque service dans son conteneur  
✅ **Scalabilité :** Facile d'ajouter plus d'instances  
✅ **Reproductibilité :** Même environnement partout

