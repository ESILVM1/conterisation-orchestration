# Configuration ELK Stack

## Démarrage

1. Démarrer tous les services :
   ```bash
   docker compose up -d
   ```

2. Attendre que tous les services soient prêts (2-3 minutes)

3. Vérifier l'état :
   ```bash
   docker compose ps
   docker compose logs elasticsearch
   ```

## Accès aux services

- **Application** : http://localhost
- **Kibana** : http://localhost:5601
- **Elasticsearch** : http://localhost:9200

## Configuration Kibana

1. Ouvrir http://localhost:5601
2. Aller dans "Stack Management" > "Index Patterns"
3. Créer pattern : `nginx-logs-*`
4. Choisir le champ de temps : `@timestamp`
5. Aller dans "Discover" pour voir les logs

## Dashboard recommandé

Visualisations à créer :
1. **Requêtes par statut** (Pie chart) - Champ: `status`
2. **Top 10 IPs** (Data table) - Champ: `remote_addr`
3. **Timeline** (Line chart) - Count over time
4. **URLs populaires** (Bar chart) - Champ: `request_uri`
5. **Temps de réponse** (Metric) - Avg `request_time`

## Génération de trafic

```bash
chmod +x generate_traffic.sh
./generate_traffic.sh
```

## Arrêt

```bash
docker compose down
```

## Nettoyage complet

```bash
docker compose down -v  # Supprime aussi les volumes
```

## Ressources système optimisées

Configuration allégée pour cette implémentation :

| Service | RAM | Notes |
|---------|-----|-------|
| Elasticsearch | 512 MB | heap size réduit |
| Kibana | 512 MB | par défaut |
| Filebeat | 50 MB | très léger |
| **Total ELK** | **~1 GB** | Au lieu de 5-7 GB |

## Points d'attention

1. **Premier démarrage lent** : Elasticsearch prend 1-2 minutes
2. **Healthchecks** : Attendre que tous soient "healthy"
3. **Index Pattern** : Créer manuellement dans Kibana la première fois
4. **Logs rotation** : Configurer ILM pour limiter la croissance
5. **Performance** : Version allégée = moins de fonctionnalités avancées

## Dépannage

**Elasticsearch ne démarre pas :**
```bash
docker compose logs elasticsearch
# Vérifier la mémoire disponible
docker stats
```

**Pas de logs dans Kibana :**
```bash
# Vérifier Filebeat
docker compose logs filebeat

# Vérifier les logs Nginx existent
docker compose exec nginx ls -la /var/log/nginx/

# Générer du trafic
./generate_traffic.sh
```

**Kibana lent :**
- Normal avec ressources limitées
- Réduire le time range dans Discover
- Utiliser des filtres

## Étapes pour créer le Dashboard Kibana

### 1. Créer l'Index Pattern

1. Ouvrir Kibana : http://localhost:5601
2. Menu (☰) > Stack Management > Index Patterns
3. Cliquer "Create index pattern"
4. Pattern name : `nginx-logs-*`
5. Next step
6. Time field : `@timestamp`
7. Create index pattern

### 2. Visualiser les logs

1. Menu (☰) > Discover
2. Vérifier que les logs apparaissent
3. Explorer les champs disponibles :
   - `remote_addr` - IP du client
   - `status` - Code HTTP (200, 404, 500...)
   - `request_uri` - URL demandée
   - `request_time` - Temps de réponse
   - `http_user_agent` - Navigateur

### 3. Créer les visualisations

**Visualisation 1 - Requêtes par code HTTP (Pie chart)**
1. Menu > Visualize > Create visualization
2. Type : Pie
3. Index pattern : nginx-logs-*
4. Metrics : Count
5. Buckets : Add > Split slices
   - Aggregation : Terms
   - Field : status
   - Size : 10
6. Save : "Codes HTTP"

**Visualisation 2 - Top 10 IPs (Data table)**
1. Create visualization > Data table
2. Metrics : Count
3. Buckets : Split rows
   - Aggregation : Terms
   - Field : remote_addr.keyword
   - Size : 10
   - Order by : Metric Count (Descending)
4. Save : "Top IPs"

**Visualisation 3 - Timeline (Line chart)**
1. Create visualization > Line
2. Metrics : Count
3. Buckets : X-axis
   - Aggregation : Date histogram
   - Field : @timestamp
   - Interval : Auto
4. Save : "Timeline requêtes"

**Visualisation 4 - URLs populaires (Horizontal bar)**
1. Create visualization > Horizontal bar
2. Metrics : Count
3. Buckets : Y-axis
   - Aggregation : Terms
   - Field : request_uri.keyword
   - Size : 20
4. Save : "URLs populaires"

**Visualisation 5 - Temps de réponse moyen (Metric)**
1. Create visualization > Metric
2. Metrics : Average
   - Field : request_time
3. Save : "Temps réponse moyen"

### 4. Créer le Dashboard

1. Menu > Dashboard > Create dashboard
2. Add visualization
3. Ajouter toutes les visualisations créées
4. Arranger selon vos préférences
5. Save dashboard : "Nginx Monitoring"

### 5. Tester

```bash
# Générer du trafic
./generate_traffic.sh

# Rafraîchir le dashboard Kibana
# Les nouvelles données devraient apparaître en quelques secondes
```

## Commandes utiles

```bash
# Voir les logs d'un service
docker compose logs -f elasticsearch
docker compose logs -f filebeat

# Vérifier l'état d'Elasticsearch
curl http://localhost:9200/_cluster/health

# Voir les index créés
curl http://localhost:9200/_cat/indices

# Compter les documents
curl http://localhost:9200/nginx-logs-*/_count

# Redémarrer un service
docker compose restart filebeat

# Voir les stats des conteneurs
docker stats
```

## Structure du projet

```
django_ecommerce_mod5/
├── docker-compose.yml          # Configuration complète avec ELK
├── nginx.conf                  # Config Nginx avec logs JSON
├── generate_traffic.sh         # Script de test
├── ELK_SETUP.md               # Ce fichier
└── elk/
    ├── elasticsearch/
    │   └── elasticsearch.yml   # Config Elasticsearch
    ├── kibana/
    │   └── kibana.yml         # Config Kibana
    └── filebeat/
        └── filebeat.yml       # Config Filebeat
```

## Pour aller plus loin

- Configurer des alertes dans Kibana
- Ajouter Logstash pour parsing avancé
- Mettre en place Index Lifecycle Management (ILM)
- Collecter aussi les logs Django
- Ajouter la géolocalisation des IPs
- Créer des dashboards personnalisés
