# Explication : .dockerignore

## 🎯 À quoi sert ce fichier ?

Le `.dockerignore` fonctionne comme `.gitignore` mais pour Docker. Il indique à Docker quels fichiers **ne pas copier** dans l'image lors du build.

## 📋 Pourquoi c'est important ?

### 1. **Performance** ⚡
- Réduit la taille du contexte de build
- Accélère le transfert de fichiers vers Docker
- Build plus rapide

### 2. **Sécurité** 🔒
- Évite de copier des fichiers sensibles (`.env`, logs)
- Empêche l'exposition de secrets dans l'image
- Réduit la surface d'attaque

### 3. **Taille de l'image** 📦
- Images Docker plus petites
- Moins d'espace disque utilisé
- Déploiement plus rapide

## 📝 Contenu du fichier

### Fichiers Python exclus
```
__pycache__/          # Cache Python
*.pyc                 # Fichiers compilés
venv/                 # Environnements virtuels
```

### Fichiers Django exclus
```
db.sqlite3            # Base de données locale
*.log                 # Fichiers de logs
/staticfiles          # Fichiers statiques (regénérés)
```

### Fichiers sensibles exclus
```
.env                  # Variables d'environnement (SECRET_KEY, etc.)
security.log          # Logs de sécurité
```

### Fichiers de développement exclus
```
.vscode/              # Configuration IDE
.git/                 # Dépôt Git
*.md                  # Documentation (sauf README.md)
```

## 🔍 Exemple concret

**Sans .dockerignore :**
```
Context envoyé à Docker: 150 MB
Temps de build: 2 minutes
```

**Avec .dockerignore :**
```
Context envoyé à Docker: 5 MB
Temps de build: 30 secondes
```

## ⚠️ Points importants

1. **`.env` doit être exclu** - Contient SECRET_KEY et autres secrets
2. **`db.sqlite3` doit être exclu** - Base de données locale, pas pour production
3. **`*.log` doit être exclu** - Logs générés localement
4. **`__pycache__/` doit être exclu** - Cache Python, recréé dans le conteneur

## 💡 Astuce

Le `.dockerignore` utilise la même syntaxe que `.gitignore`, donc vous pouvez réutiliser des patterns similaires.

