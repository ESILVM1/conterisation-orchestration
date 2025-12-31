# Explication : requirements.txt

## 🎯 À quoi sert ce fichier ?

Le `requirements.txt` liste **toutes les dépendances Python** nécessaires pour faire fonctionner votre projet Django. Il permet de réinstaller exactement les mêmes versions partout.

## 📋 Dépendances expliquées

### 1. **Django==3.0.2**
```txt
Django==3.0.2
```
- **Rôle :** Framework web principal
- **Version :** 3.0.2 (compatible avec votre projet)
- **Usage :** Toute l'application Django

### 2. **gunicorn==20.1.0**
```txt
gunicorn==20.1.0
```
- **Rôle :** Serveur WSGI pour la production
- **Pourquoi :** Le serveur de développement Django n'est pas adapté à la production
- **Usage :** Sert l'application Django dans Docker/production
- **Alternative :** uWSGI (mais Gunicorn est plus simple)

### 3. **psycopg2-binary==2.9.3**
```txt
psycopg2-binary==2.9.3
```
- **Rôle :** Driver PostgreSQL pour Python
- **Pourquoi :** Permet à Django de se connecter à PostgreSQL
- **`-binary` :** Version précompilée (plus facile à installer)
- **Alternative :** psycopg2 (nécessite compilation)

### 4. **Pillow==9.5.0**
```txt
Pillow==9.5.0
```
- **Rôle :** Bibliothèque de traitement d'images
- **Pourquoi :** Nécessaire pour `ImageField` dans vos modèles Django
- **Usage :** Upload et traitement des images produits
- **Important :** Sans Pillow, les ImageField ne fonctionnent pas

### 5. **whitenoise==6.2.0**
```txt
whitenoise==6.2.0
```
- **Rôle :** Service des fichiers statiques en production
- **Pourquoi :** Django ne sert pas les fichiers statiques efficacement en production
- **Usage :** Alternative à Nginx pour servir les fichiers statiques
- **Note :** Avec Nginx, cette dépendance est optionnelle mais utile

## 🔧 Installation

### Dans un environnement virtuel
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Dans Docker
Le Dockerfile installe automatiquement :
```dockerfile
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
```

## 📊 Versions

### Pourquoi des versions spécifiques ?
- **Reproductibilité :** Même environnement partout
- **Stabilité :** Évite les breaking changes
- **Sécurité :** Contrôle des versions installées

### Mettre à jour les versions
```bash
# Voir les versions disponibles
pip list --outdated

# Mettre à jour requirements.txt manuellement
# Puis tester avant de commiter
```

## 🔒 Sécurité

### Vérifier les vulnérabilités
```bash
pip install safety
safety check -r requirements.txt
```

### Versions recommandées (2024)
- **Django :** 3.0.2 (actuel) ou migrer vers 4.2 LTS
- **Gunicorn :** 20.1.0 (actuel) ou 21.x
- **Pillow :** 9.5.0 (actuel) ou 10.x
- **psycopg2-binary :** 2.9.3 (actuel) ou 2.9.x

## 💡 Dépendances optionnelles (à ajouter si besoin)

### Pour le développement
```txt
# Débogage
django-debug-toolbar==3.2.4

# Tests
pytest==7.4.0
pytest-django==4.5.2
```

### Pour la production
```txt
# Monitoring
sentry-sdk==1.32.0

# Rate limiting
django-ratelimit==4.0.0

# Cache Redis
redis==4.5.4
django-redis==5.2.0
```

### Pour les emails
```txt
# Envoi d'emails
django-ses==3.0.0
```

## 📝 Format du fichier

### Syntaxe
```txt
# Commentaire
package==version          # Version exacte
package>=version         # Version minimale
package~=version         # Compatible (même version majeure)
```

### Exemple avec versions flexibles
```txt
Django>=3.0,<4.0        # Django 3.x
gunicorn>=20.0,<21.0     # Gunicorn 20.x
```

## 🚀 Commandes utiles

### Générer requirements.txt depuis l'environnement actuel
```bash
pip freeze > requirements.txt
```

### Installer sans cache (Docker)
```bash
pip install --no-cache-dir -r requirements.txt
```

### Vérifier les dépendances
```bash
pip check
```

## ⚠️ Points d'attention

1. **psycopg2-binary :** Version précompilée, plus lourde mais plus simple
2. **Versions :** Tester avant de mettre à jour en production
3. **Sécurité :** Vérifier régulièrement les vulnérabilités
4. **Compatibilité :** Django 3.0.2 est ancien, considérer une mise à jour

