# Guide Docker - Django E-commerce

## 🚀 Démarrage Rapide

### 1. Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```bash
# SECURITY: Générez une nouvelle clé secrète
SECRET_KEY=votre-cle-secrete-generee-ici

# Définir à False en production
DEBUG=True

# Liste des hôtes autorisés
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration Base de Données PostgreSQL
DATABASE=postgresql
DB_NAME=ecommerce_db
DB_USER=django_user
DB_PASSWORD=django_pass
DB_HOST=db
DB_PORT=5432
```

### 2. Générer une SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Démarrer les conteneurs

```bash
docker compose up -d --build
```

### 4. Vérifier les logs

```bash
docker compose logs -f web
```

## 📋 Commandes Utiles

### Démarrer tous les services
```bash
docker compose up -d
```

### Arrêter tous les services
```bash
docker compose down
```

### Reconstruire après modification
```bash
docker compose up -d --build
```

### Voir les logs
```bash
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx
```

### Accéder au shell du conteneur web
```bash
docker compose exec web bash
```

### Exécuter des commandes Django
```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic
```

### Arrêter et supprimer les volumes (⚠️ supprime les données)
```bash
docker compose down -v
```

## 🔧 Configuration

### Ports
- **Django** : http://localhost:8000
- **Nginx** : http://localhost (port 80)
- **PostgreSQL** : localhost:5432

### Volumes
- `postgres_data` : Données de la base de données
- `static_volume` : Fichiers statiques collectés
- `media_volume` : Images et médias uploadés

## ⚠️ Résolution de Problèmes

### Erreur : "env file .env not found"
**Solution :** Créez le fichier `.env` comme indiqué ci-dessus. Le fichier est optionnel mais recommandé.

### Erreur : "version is obsolete"
**Solution :** Déjà corrigé - la ligne `version` a été supprimée du docker-compose.yml.

### Erreur de connexion à la base de données
**Solution :** Vérifiez que le service `db` est démarré :
```bash
docker compose ps
docker compose logs db
```

### Erreur de permissions
**Solution :** Les conteneurs utilisent un utilisateur non-root. Si vous avez des problèmes, vérifiez les permissions des volumes.

## 📝 Notes

- Le fichier `.env` ne doit **JAMAIS** être commité dans Git
- Les données de la base sont persistées dans le volume `postgres_data`
- Les fichiers statiques sont collectés automatiquement au démarrage
- Nginx sert les fichiers statiques directement (plus rapide)

