# Guide des Tests Backend

## Vue d'ensemble

Ce projet contient une suite complète de tests backend pour l'application e-commerce Django. Les tests couvrent tous les modèles, vues et API endpoints.

## Installation des dépendances

```bash
pip install -r requirements.txt
```

Les dépendances de test incluent:
- `coverage` - Mesure de la couverture de code
- `pytest` - Framework de test moderne
- `pytest-django` - Plugin pytest pour Django

## Exécution des tests

### Tests simples

```bash
# Exécuter tous les tests
python manage.py test store

# Exécuter une classe de test spécifique
python manage.py test store.tests.ProductModelTest

# Exécuter un test spécifique
python manage.py test store.tests.ProductModelTest.test_product_creation
```

### Tests avec couverture

```bash
# Exécuter les tests avec rapport de couverture
coverage run --source='.' manage.py test store

# Afficher le rapport dans le terminal
coverage report

# Générer un rapport HTML
coverage html

# Ouvrir le rapport HTML (créé dans htmlcov/)
open htmlcov/index.html
```

### Tests avec pytest

```bash
# Exécuter avec pytest
pytest

# Avec couverture
pytest --cov=store --cov-report=html
```

## Structure des tests

### Tests des modèles (`store/tests.py`)

#### ProductModelTest
- `test_product_creation` - Vérifie la création de produit
- `test_product_str` - Teste la représentation string
- `test_product_image_url_no_image` - Teste imageURL sans image
- `test_digital_product` - Teste les produits digitaux

#### CustomerModelTest
- `test_customer_creation` - Vérifie la création de client
- `test_customer_str` - Teste la représentation string
- `test_customer_without_user` - Teste client sans utilisateur (invité)

#### OrderModelTest
- `test_order_creation` - Vérifie la création de commande
- `test_get_cart_total` - Teste le calcul du total
- `test_get_cart_items` - Teste le comptage des articles
- `test_shipping_required_for_physical_product` - Teste shipping pour produits physiques
- `test_no_shipping_for_digital_product` - Teste absence shipping pour produits digitaux
- `test_empty_cart_total` - Teste panier vide

#### OrderItemModelTest
- `test_order_item_creation` - Vérifie la création d'article
- `test_get_total` - Teste le calcul prix × quantité
- `test_get_total_single_item` - Teste le total pour un seul article

#### ShippingAddressModelTest
- `test_shipping_address_creation` - Vérifie la création d'adresse
- `test_shipping_address_str` - Teste la représentation string

### Tests des vues

#### StoreViewTest
- `test_store_view_loads` - Vérifie que la page boutique charge
- `test_store_view_contains_products` - Vérifie l'affichage des produits
- `test_cart_view_loads` - Vérifie que la page panier charge
- `test_checkout_view_loads` - Vérifie que la page checkout charge

#### UpdateItemViewTest
- `test_add_item_to_cart` - Teste l'ajout au panier
- `test_remove_item_from_cart` - Teste la suppression du panier
- `test_remove_last_item_deletes_orderitem` - Teste la suppression complète
- `test_invalid_product_id` - Teste la validation du produit
- `test_invalid_action` - Teste la validation de l'action
- `test_invalid_json` - Teste la validation du JSON
- `test_missing_fields` - Teste les champs requis
- `test_unauthenticated_user` - Teste l'authentification requise

#### LoginViewTest
- `test_login_page_loads` - Vérifie que la page login charge
- `test_successful_login` - Teste le login réussi
- `test_failed_login_wrong_password` - Teste le login échoué
- `test_failed_login_missing_fields` - Teste les champs manquants
- `test_logout` - Teste le logout
- `test_already_authenticated_redirect` - Teste la redirection si déjà connecté

## Couverture de code

La suite de tests vise une couverture de:
- **Modèles**: 100% (toutes les méthodes et propriétés)
- **Vues**: 85%+ (tous les chemins principaux)
- **Total**: 80%+ de couverture globale

## CI/CD avec GitHub Actions

Le projet inclut une configuration GitHub Actions (`.github/workflows/ci.yml`) qui:

1. **Tests Backend** - Exécute tous les tests avec couverture
2. **Code Quality** - Vérifie le style avec flake8 et black
3. **Docker Build** - Vérifie que l'image Docker se construit
4. **Security Scan** - Scanne les vulnérabilités avec safety et Trivy

Les tests s'exécutent automatiquement sur:
- Chaque push sur les branches: `main`, `master`, `test`, `develop`
- Chaque pull request vers `main` ou `master`

## Bonnes pratiques

### Avant de commiter
```bash
# Exécuter les tests
python manage.py test store

# Vérifier la couverture
coverage run --source='.' manage.py test store
coverage report

# Vérifier le style
flake8 store/
black --check store/
```

### Lors de l'ajout de nouvelles fonctionnalités

1. Écrire les tests AVANT le code (TDD)
2. Assurer au minimum 80% de couverture
3. Tester les cas limites et les erreurs
4. Vérifier que tous les tests passent avant de push

## Dépannage

### Erreur de migration
```bash
python manage.py migrate --run-syncdb
```

### Base de données de test corrompue
```bash
python manage.py test --keepdb store
```

### Réinitialiser la couverture
```bash
coverage erase
coverage run --source='.' manage.py test store
```

## Ressources

- [Documentation Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
