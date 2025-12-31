# Corrections de Sécurité - Exemples de Code

Ce document contient des exemples de code corrigé pour les vulnérabilités identifiées.

---

## 1. Configuration Sécurisée (settings.py)

### Avant (VULNÉRABLE):
```python
SECRET_KEY = 'z+ksf@)0d^qojbh4rnp4b1to$hq&*tt(3bs$gf(3i267g$k9ln'
DEBUG = True
ALLOWED_HOSTS = []
```

### Après (SÉCURISÉ):
```python
import os
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name, default=None):
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_env_variable('SECRET_KEY')
DEBUG = get_env_variable('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Sécurité des cookies
SESSION_COOKIE_SECURE = not DEBUG  # True en production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

# Headers de sécurité
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

## 2. Validation du Prix - Correction Critique

### Avant (VULNÉRABLE):
```python
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    # ... code ...
    
    total = float(data['form']['total'])  # ⚠️ NE JAMAIS FAIRE CONFIANCE AU CLIENT
    order.transaction_id = transaction_id
    
    if total == order.get_cart_total:  # ⚠️ Comparaison dangereuse
        order.complete = True
    order.save()
```

### Après (SÉCURISÉ):
```python
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_protect
def processOrder(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    transaction_id = datetime.datetime.now().timestamp()
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)
    
    # ✅ RECALCULER le total côté serveur - NE JAMAIS FAIRE CONFIANCE AU CLIENT
    calculated_total = order.get_cart_total
    
    # Optionnel: vérifier si le total envoyé correspond (pour logging uniquement)
    client_total = float(data.get('form', {}).get('total', 0))
    if abs(client_total - calculated_total) > 0.01:  # Tolérance pour les arrondis
        logger.warning(f"Price mismatch: client={client_total}, server={calculated_total}, order={order.id}")
        # Ne pas bloquer, mais logger l'anomalie
    
    order.transaction_id = transaction_id
    order.complete = True  # ✅ Valider uniquement si le calcul serveur est correct
    order.save()
    
    if order.shipping:
        # Validation des données d'adresse
        shipping_data = data.get('shipping', {})
        if not all(key in shipping_data for key in ['address', 'city', 'state', 'zipcode']):
            return JsonResponse({'error': 'Missing shipping information'}, status=400)
        
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=shipping_data['address'][:200],  # Limiter la longueur
            city=shipping_data['city'][:200],
            state=shipping_data['state'][:200],
            zipcode=shipping_data['zipcode'][:200],
        )
    
    return JsonResponse({'success': True, 'transaction_id': transaction_id}, status=200)
```

---

## 3. Protection CSRF et Authentification

### Avant (VULNÉRABLE):
```python
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    customer = request.user.customer  # ⚠️ Peut lever AttributeError
    product = Product.objects.get(id=productId)  # ⚠️ Peut lever DoesNotExist
```

### Après (SÉCURISÉ):
```python
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_protect
@login_required
def updateItem(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Validation des données d'entrée
    productId = data.get('productId')
    action = data.get('action')
    
    if not productId or not action:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    if action not in ['add', 'remove']:
        return JsonResponse({'error': 'Invalid action'}, status=400)
    
    try:
        productId = int(productId)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid product ID'}, status=400)
    
    try:
        customer = request.user.customer
    except AttributeError:
        return JsonResponse({'error': 'Customer profile not found'}, status=404)
    
    try:
        product = Product.objects.get(id=productId)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    try:
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        
        if action == 'add':
            orderItem.quantity += 1
        elif action == 'remove':
            orderItem.quantity -= 1
        
        orderItem.save()
        
        if orderItem.quantity <= 0:
            orderItem.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Item updated',
            'quantity': orderItem.quantity if orderItem.quantity > 0 else 0
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
```

---

## 4. Gestion d'Erreurs Améliorée (utils.py)

### Avant (VULNÉRABLE):
```python
def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    
    for i in cart:
        try:
            if(cart[i]['quantity']>0):
                product = Product.objects.get(id=i)
                # ...
        except:
            pass  # ⚠️ Ignore toutes les erreurs
```

### Après (SÉCURISÉ):
```python
import json
import logging
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Invalid cart cookie: {str(e)}")
        cart = {}
    
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']
    
    for product_id in cart:
        try:
            product_id = int(product_id)  # Valider que c'est un entier
            quantity = cart[product_id].get('quantity', 0)
            
            if quantity > 0:
                try:
                    product = Product.objects.get(id=product_id)
                    total = product.price * quantity
                    
                    order['get_cart_total'] += total
                    order['get_cart_items'] += quantity
                    
                    item = {
                        'id': product.id,
                        'product': {
                            'id': product.id,
                            'name': product.name,
                            'price': product.price,
                            'imageURL': product.imageURL
                        },
                        'quantity': quantity,
                        'digital': product.digital,
                        'get_total': total,
                    }
                    items.append(item)
                    
                    if not product.digital:
                        order['shipping'] = True
                        
                except Product.DoesNotExist:
                    logger.warning(f"Product {product_id} not found in cart")
                    continue
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid product data for {product_id}: {str(e)}")
                    continue
                    
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Invalid cart item {product_id}: {str(e)}")
            continue
    
    return {'cartItems': cartItems, 'order': order, 'items': items}
```

---

## 5. Validation des Données de Formulaire

### Avant (VULNÉRABLE):
```python
def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']
    # Pas de validation
```

### Après (SÉCURISÉ):
```python
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import EmailValidator

def guestOrder(request, data):
    form_data = data.get('form', {})
    
    name = form_data.get('name', '').strip()
    email = form_data.get('email', '').strip()
    
    # Validation du nom
    if not name or len(name) < 2 or len(name) > 200:
        raise ValidationError('Invalid name')
    
    # Validation de l'email
    email_validator = EmailValidator()
    try:
        email_validator(email)
    except ValidationError:
        raise ValidationError('Invalid email address')
    
    # Nettoyage du nom (supprimer caractères dangereux)
    name = re.sub(r'[<>"\']', '', name)
    
    cookieData = cookieCart(request)
    items = cookieData['items']
    
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()
    
    order = Order.objects.create(customer=customer, complete=False)
    
    for item in items:
        try:
            product = Product.objects.get(id=item['id'])
            quantity = max(1, int(item.get('quantity', 1)))  # Minimum 1, valider le type
            
            OrderItem.objects.create(
                product=product,
                order=order,
                quantity=quantity,
            )
        except (Product.DoesNotExist, ValueError, TypeError) as e:
            logger.warning(f"Error creating order item: {str(e)}")
            continue
    
    return customer, order
```

---

## 6. Fichier .env.example

Créer un fichier `.env.example` pour documenter les variables d'environnement nécessaires:

```bash
# .env.example
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com
DATABASE_URL=sqlite:///db.sqlite3
```

Et ajouter `.env` au `.gitignore`:

```
.env
*.pyc
__pycache__/
db.sqlite3
```

---

## 7. Correction JavaScript (checkout.html)

### Avant (VULNÉRABLE):
```javascript
'Content-Type':'applicaiton/json',  // Faute de frappe
```

### Après (CORRIGÉ):
```javascript
'Content-Type': 'application/json',  // ✅ Corrigé
```

---

## 8. Configuration de Logging (settings.py)

Ajouter une configuration de logging pour tracer les problèmes de sécurité:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'security.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'store': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
```

---

## 9. Rate Limiting (optionnel mais recommandé)

Installer django-ratelimit:
```bash
pip install django-ratelimit
```

Utilisation:
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
@require_http_methods(["POST"])
@csrf_protect
@login_required
def updateItem(request):
    # ...
```

---

## Checklist de Déploiement

Avant de déployer en production, vérifier:

- [ ] SECRET_KEY dans variable d'environnement
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configuré
- [ ] Validation du prix corrigée
- [ ] Protection CSRF sur tous les endpoints
- [ ] Authentification requise où nécessaire
- [ ] Gestion d'erreurs améliorée
- [ ] Validation des entrées utilisateur
- [ ] Cookies sécurisés
- [ ] HTTPS activé
- [ ] Base de données de production (pas SQLite)
- [ ] Backups configurés
- [ ] Logging configuré
- [ ] Tests de sécurité effectués

---

*Ces corrections doivent être testées en environnement de développement avant d'être déployées en production.*

