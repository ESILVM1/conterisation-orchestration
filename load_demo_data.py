#!/usr/bin/env python
"""
Script pour charger des données de démonstration dans la boutique e-commerce
"""
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import Product, Customer, Order
from django.contrib.auth.models import User

def load_demo_products():
    """Charge des produits de démonstration"""
    
    products_data = [
        {
            'name': 'MacBook Pro 16"',
            'price': 2499.99,
            'digital': False,
            'image': 'placeholder.png',
            'description': 'Ordinateur portable haute performance avec puce M3 Pro, 16GB RAM, 512GB SSD. Parfait pour le développement et la création de contenu.'
        },
        {
            'name': 'iPhone 15 Pro',
            'price': 1199.99,
            'digital': False,
            'image': 'placeholder.png',
            'description': 'Smartphone dernière génération avec puce A17 Pro, appareil photo 48MP, écran ProMotion 120Hz. Disponible en 256GB.'
        },
        {
            'name': 'AirPods Pro (2ème gen)',
            'price': 249.99,
            'digital': False,
            'image': 'headphones.jpg',
            'description': 'Écouteurs sans fil avec réduction de bruit active, son spatial personnalisé, résistance à l\'eau IPX4. Boîtier MagSafe inclus.'
        },
        {
            'name': 'iPad Air 11"',
            'price': 699.99,
            'digital': False,
            'image': 'placeholder.png',
            'description': 'Tablette polyvalente avec puce M2, écran Liquid Retina, compatible Apple Pencil. Idéale pour le travail et le divertissement.'
        },
        {
            'name': 'Apple Watch Series 9',
            'price': 429.99,
            'digital': False,
            'image': 'watch.jpg',
            'description': 'Montre connectée avec suivi santé avancé, GPS, écran always-on, résistance à l\'eau 50m. Boîtier 45mm en aluminium.'
        },
        {
            'name': 'Formation Python Complète',
            'price': 89.99,
            'digital': True,
            'image': 'sourcecode.jpg',
            'description': 'Cours vidéo complet pour maîtriser Python : bases, POO, Django, Flask, data science. 40h de contenu + exercices pratiques.'
        },
        {
            'name': 'Formation Docker & Kubernetes',
            'price': 129.99,
            'digital': True,
            'image': 'book.jpg',
            'description': 'Apprenez la conteneurisation et l\'orchestration : Docker, Docker Compose, Kubernetes, CI/CD. Certificat inclus.'
        },
        {
            'name': 'Formation Développement Web Full Stack',
            'price': 199.99,
            'digital': True,
            'image': 'sourcecode.jpg',
            'description': 'Formation complète : HTML/CSS, JavaScript, React, Node.js, MongoDB, déploiement. Projets réels + portfolio.'
        },
        {
            'name': 'Magic Keyboard',
            'price': 99.99,
            'digital': False,
            'image': 'placeholder.png',
            'description': 'Clavier sans fil rechargeable avec pavé numérique, connexion Bluetooth, compatible Mac et iPad. Batterie longue durée.'
        },
        {
            'name': 'Magic Mouse',
            'price': 79.99,
            'digital': False,
            'image': 'placeholder.png',
            'description': 'Souris sans fil avec surface tactile Multi-Touch, rechargeable, design ergonomique. Compatible macOS et iPadOS.'
        },
        {
            'name': 'T-Shirt Developer',
            'price': 29.99,
            'digital': False,
            'image': 'shirt.jpg',
            'description': 'T-shirt 100% coton bio avec design humoristique "I speak fluent Python". Tailles S à XXL disponibles.'
        },
        {
            'name': 'Sneakers Tech',
            'price': 149.99,
            'digital': False,
            'image': 'shoes.jpg',
            'description': 'Baskets confortables avec semelle memory foam, design moderne, matériaux respirants. Parfaites pour le quotidien.'
        },
    ]
    
    print("🔄 Suppression des anciens produits...")
    Product.objects.all().delete()
    
    print("➕ Création des nouveaux produits...")
    for product_data in products_data:
        product = Product.objects.create(**product_data)
        print(f"   ✅ Créé: {product.name} - {product.price}€")
    
    print(f"\n✨ {len(products_data)} produits créés avec succès!")

def create_demo_user():
    """Crée un utilisateur de démonstration"""
    print("\n👤 Création d'un utilisateur de démonstration...")
    
    # Supprimer l'ancien utilisateur s'il existe
    User.objects.filter(username='demo').delete()
    
    # Créer un nouvel utilisateur
    user = User.objects.create_user(
        username='demo',
        email='demo@example.com',
        password='demo123',
        first_name='Démo',
        last_name='Utilisateur'
    )
    
    # Créer le profil client associé
    customer, created = Customer.objects.get_or_create(
        user=user,
        defaults={
            'name': f'{user.first_name} {user.last_name}',
            'email': user.email
        }
    )
    
    print(f"   ✅ Utilisateur créé: {user.username}")
    print(f"   📧 Email: {user.email}")
    print(f"   🔑 Mot de passe: demo123")
    
    return user

def create_admin_user():
    """Crée un superutilisateur pour l'admin Django"""
    print("\n👨‍💼 Création d'un compte administrateur...")
    
    # Supprimer l'ancien admin s'il existe
    User.objects.filter(username='admin').delete()
    
    # Créer un superutilisateur
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='System'
    )
    
    print(f"   ✅ Admin créé: {admin.username}")
    print(f"   📧 Email: {admin.email}")
    print(f"   🔑 Mot de passe: admin123")
    print(f"   🔗 Admin panel: http://localhost/admin/")
    
    return admin

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Chargement des données de démonstration")
    print("=" * 60)
    
    load_demo_products()
    create_demo_user()
    create_admin_user()
    
    print("\n" + "=" * 60)
    print("✅ Données de démonstration chargées avec succès!")
    print("=" * 60)
    print("\n📝 Informations de connexion:")
    print("   🔹 Utilisateur démo:")
    print("      - Username: demo")
    print("      - Password: demo123")
    print("\n   🔹 Administrateur:")
    print("      - Username: admin")
    print("      - Password: admin123")
    print("      - Panel: http://localhost/admin/")
    print("\n🌐 Accédez à l'application: http://localhost")
    print("=" * 60)

