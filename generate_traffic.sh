#!/bin/bash

echo "Génération de trafic sur Nginx..."

# Requêtes normales (200)
for i in {1..50}; do
  curl -s http://localhost/ > /dev/null
  curl -s http://localhost/cart/ > /dev/null
  curl -s http://localhost/login/ > /dev/null
done

# Erreurs 404
for i in {1..20}; do
  curl -s http://localhost/page-inexistante-$i > /dev/null
done

# Fichiers statiques
for i in {1..30}; do
  curl -s http://localhost/static/css/main.css > /dev/null
  curl -s http://localhost/static/js/cart.js > /dev/null
done

echo "Trafic généré : 100 requêtes"
echo "Consultez Kibana sur http://localhost:5601"
