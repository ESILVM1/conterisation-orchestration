# Explication : docker-entrypoint.sh

## 🎯 À quoi sert ce fichier ?

Le `docker-entrypoint.sh` est un **script de démarrage** qui s'exécute automatiquement quand le conteneur Docker démarre. Il prépare l'environnement avant de lancer l'application Django.

## 📋 Fonctions du script

### 1. **Attente de la base de données** (lignes 5-11)
```bash
if [ "$DATABASE" = "postgresql" ]; then
    echo "Waiting for postgres..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done
```
- **Pourquoi ?** La base de données peut prendre quelques secondes à démarrer
- **Action :** Le script attend que PostgreSQL soit prêt avant de continuer
- **Évite :** Les erreurs de connexion si Django démarre avant la DB

### 2. **Exécution des migrations** (lignes 13-15)
```bash
echo "Running migrations..."
python manage.py migrate --noinput
```
- **Pourquoi ?** Applique les changements de schéma de base de données
- **Action :** Crée/modifie les tables automatiquement au démarrage
- **`--noinput` :** Pas de confirmation interactive (nécessaire en Docker)

### 3. **Collecte des fichiers statiques** (lignes 17-19)
```bash
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
```
- **Pourquoi ?** Django a besoin de rassembler les fichiers CSS/JS/images
- **Action :** Copie tous les fichiers statiques dans un dossier centralisé
- **`--clear` :** Nettoie les anciens fichiers avant de copier

### 4. **Exécution de la commande principale** (ligne 22)
```bash
exec "$@"
```
- **Pourquoi ?** Exécute la commande passée au conteneur (ex: `gunicorn`)
- **`exec` :** Remplace le processus shell par la commande (meilleure gestion des signaux)

## 🔄 Flux d'exécution

```
Démarrage du conteneur
    ↓
docker-entrypoint.sh s'exécute
    ↓
1. Attend PostgreSQL (si nécessaire)
    ↓
2. Exécute les migrations
    ↓
3. Collecte les fichiers statiques
    ↓
4. Lance la commande CMD (gunicorn)
    ↓
Application Django en cours d'exécution
```

## 💡 Avantages

✅ **Automatisation** : Plus besoin de faire manuellement les migrations  
✅ **Fiabilité** : S'assure que tout est prêt avant de démarrer  
✅ **Sécurité** : Utilise `set -e` pour arrêter en cas d'erreur  
✅ **Flexibilité** : Peut exécuter n'importe quelle commande passée

## 🔧 Personnalisation

Vous pouvez ajouter d'autres tâches :
- Créer un superutilisateur
- Charger des données initiales (fixtures)
- Vérifier la configuration
- Nettoyer des fichiers temporaires

## 📝 Exemple d'utilisation

Dans le Dockerfile :
```dockerfile
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ecommerce.wsgi:application"]
```

Quand le conteneur démarre :
1. Le script s'exécute d'abord (migrations, static files)
2. Puis lance `gunicorn` (la commande CMD)

