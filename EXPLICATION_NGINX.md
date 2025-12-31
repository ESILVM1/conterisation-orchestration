# Explication : nginx.conf

## 🎯 À quoi sert ce fichier ?

Le `nginx.conf` configure **Nginx** comme reverse proxy devant Django. Il sert les fichiers statiques directement et redirige les requêtes dynamiques vers Django.

## 📋 Structure de la configuration

### 1. **Upstream Django** (lignes 1-3)
```nginx
upstream django {
    server web:8000;
}
```
- **Rôle :** Définit le serveur backend (Django sur le conteneur `web`)
- **Port :** 8000 (port interne du conteneur)
- **Avantage :** Si vous avez plusieurs instances Django, vous pouvez les ajouter ici

### 2. **Server HTTP** (lignes 5-32)
```nginx
server {
    listen 80;
    ...
}
```

#### **Location `/`** (lignes 13-18)
- **Rôle :** Toutes les requêtes vers l'application Django
- **Action :** Proxy vers `http://django` (le conteneur web)
- **Headers :** 
  - `X-Forwarded-For` : IP du client
  - `Host` : Nom d'hôte
  - `X-Forwarded-Proto` : Protocole (http/https)

#### **Location `/static/`** (lignes 20-24)
- **Rôle :** Servir les fichiers statiques (CSS, JS)
- **Source :** `/static/` (volume monté depuis Django)
- **Cache :** 30 jours (fichiers statiques changent rarement)
- **Performance :** Nginx sert directement, Django n'est pas sollicité

#### **Location `/images/`** (lignes 26-30)
- **Rôle :** Servir les images/media
- **Source :** `/media/` (volume monté)
- **Cache :** 7 jours (images peuvent changer plus souvent)

### 3. **Server HTTPS** (lignes 34-60, commenté)
- **Rôle :** Configuration HTTPS pour la production
- **SSL :** Certificats dans `/etc/nginx/ssl/`
- **Protocoles :** TLS 1.2 et 1.3 (sécurisés)
- **État :** Commenté par défaut (décommenter en production)

## 🔄 Flux des requêtes

```
Client
  ↓
Nginx (port 80)
  ↓
  ├─ /static/* → Fichiers statiques (directement)
  ├─ /images/* → Images/media (directement)
  └─ /* → Django/Gunicorn (proxy)
```

## 💡 Avantages

### 1. **Performance** ⚡
- Nginx sert les fichiers statiques directement (plus rapide)
- Django se concentre sur le code Python
- Cache des fichiers statiques (moins de requêtes)

### 2. **Sécurité** 🔒
- Nginx peut gérer SSL/TLS
- Protection contre certaines attaques (DDoS, etc.)
- Headers de sécurité configurables

### 3. **Scalabilité** 📈
- Plusieurs instances Django possibles
- Load balancing facile
- Gestion du trafic

## 🔧 Configuration importante

### `client_max_body_size 10M`
- **Rôle :** Limite la taille des uploads
- **Valeur :** 10 Mo (ajustable selon vos besoins)
- **Utile :** Évite les uploads trop volumineux

### Headers proxy
```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
```
- **Rôle :** Transmettre les informations du client à Django
- **Important :** Django peut détecter l'IP réelle et le protocole

### Cache
```nginx
expires 30d;
add_header Cache-Control "public, immutable";
```
- **Rôle :** Indique au navigateur de mettre en cache
- **Avantage :** Moins de requêtes répétées
- **Performance :** Pages plus rapides

## 🚀 Activation HTTPS en production

1. **Obtenir des certificats SSL** (Let's Encrypt, etc.)
2. **Créer le dossier `ssl/`** avec les certificats
3. **Décommenter la section HTTPS** dans `nginx.conf`
4. **Commenter la redirection HTTP → HTTPS** (ligne 9)

## 📝 Exemple de configuration Django

Dans `settings.py`, ajoutez :
```python
# Pour que Django détecte les requêtes HTTPS via Nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
```

## 🔍 Debugging

### Vérifier la configuration
```bash
docker-compose exec nginx nginx -t
```

### Voir les logs Nginx
```bash
docker-compose logs -f nginx
```

### Tester les fichiers statiques
```bash
curl http://localhost/static/css/main.css
```

## ⚠️ Points d'attention

1. **Volumes :** Les chemins `/static/` et `/media/` doivent correspondre aux volumes dans `docker-compose.yml`
2. **Permissions :** Nginx doit avoir accès en lecture aux fichiers statiques
3. **HTTPS :** En production, toujours utiliser HTTPS
4. **Headers :** Les headers proxy sont essentiels pour que Django fonctionne correctement

