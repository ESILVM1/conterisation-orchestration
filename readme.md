# 🛒 Django E-commerce - Containerization & Orchestration

> **Module :** Containerization & Orchestration  
> **Enseignant référent :** Maxime CORDEIRO  
> **Auteur :** Ahmat ROUCHAD  
> **Promotion :** ESILV M1

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![ElasticStack](https://img.shields.io/badge/Elastic_Stack-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## 📋 Description du Projet

Ce projet est une application e-commerce complète développée avec **Django**, conteneurisée et orchestrée via **Docker Compose**. L'objectif principal de ce module était de mettre en place une architecture micro-services robuste, sécurisée et observable.

Le projet intègre une **stack ELK (Elasticsearch, Kibana, Filebeat)** complète pour la centralisation et l'analyse des logs du serveur web Nginx, permettant un monitoring en temps réel du trafic, des erreurs et des performances.

## 🏗 Architecture Technique

L'application est décomposée en services interconnectés :

| Service | Rôle | Technologie |
|---------|------|-------------|
| **WebApp** | Backend logique et API | Django (Gunicorn) |
| **Database** | Persistance des données | PostgreSQL 15 |
| **Nginx** | Reverse Proxy & Fichiers statiques | Nginx (Alpine) |
| **Elasticsearch** | Moteur de recherche & Stockage logs | Elasticsearch 8.11 |
| **Kibana** | Visualisation & Dashboards | Kibana 8.11 |
| **Filebeat** | Collecteur de logs léger | Filebeat 8.11 |

### Points Forts de l'implémentation
* **Logs JSON :** Configuration Nginx personnalisée pour générer des logs au format JSON pur, facilitant l'ingestion.
* **Optimisation :** Limitation de la mémoire (Heap Size) pour faire tourner la stack ELK sur des machines à ressources limitées.
* **Sécurité :** Utilisation d'utilisateurs non-root là où c'est possible et gestion des secrets via variables d'environnement.

---

## 🚀 Installation et Démarrage

### Prérequis
* Docker Desktop & Docker Compose
* Git
* Au moins 4GB de RAM allouée à Docker

### 1. Cloner le projet
```bash
git clone [https://github.com/ESILVM1/conterisation-orchestration.git](https://github.com/ESILVM1/conterisation-orchestration.git)
cd django_ecommerce_mod5
