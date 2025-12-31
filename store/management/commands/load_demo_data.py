from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Product, Customer

class Command(BaseCommand):
    help = 'Charge des données de démonstration pour la boutique'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS('🚀 Chargement des données de démonstration'))
        self.stdout.write("=" * 60)
        
        self.load_products()
        self.create_demo_user()
        self.create_admin_user()
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS('✅ Données chargées avec succès!'))
        self.stdout.write("=" * 60)
        self.stdout.write("\n📝 Informations de connexion:")
        self.stdout.write("   🔹 Utilisateur démo:")
        self.stdout.write("      - Username: demo")
        self.stdout.write("      - Password: demo123")
        self.stdout.write("\n   🔹 Administrateur:")
        self.stdout.write("      - Username: admin")
        self.stdout.write("      - Password: admin123")
        self.stdout.write("      - Panel: http://localhost/admin/")
        self.stdout.write("\n🌐 Application: http://localhost")
        self.stdout.write("=" * 60)

    def load_products(self):
        """Charge des produits de démonstration"""
        products_data = [
            {
                'name': 'MacBook Pro 16"',
                'price': 2499.99,
                'digital': False,
                'image': 'placeholder.png',
            },
            {
                'name': 'iPhone 15 Pro',
                'price': 1199.99,
                'digital': False,
                'image': 'placeholder.png',
            },
            {
                'name': 'AirPods Pro (2ème gen)',
                'price': 249.99,
                'digital': False,
                'image': 'headphones.jpg',
            },
            {
                'name': 'iPad Air 11"',
                'price': 699.99,
                'digital': False,
                'image': 'placeholder.png',
            },
            {
                'name': 'Apple Watch Series 9',
                'price': 429.99,
                'digital': False,
                'image': 'watch.jpg',
            },
            {
                'name': 'Formation Python Complète',
                'price': 89.99,
                'digital': True,
                'image': 'sourcecode.jpg',
            },
            {
                'name': 'Formation Docker & Kubernetes',
                'price': 129.99,
                'digital': True,
                'image': 'book.jpg',
            },
            {
                'name': 'Formation Web Full Stack',
                'price': 199.99,
                'digital': True,
                'image': 'sourcecode.jpg',
            },
            {
                'name': 'Magic Keyboard',
                'price': 99.99,
                'digital': False,
                'image': 'placeholder.png',
            },
            {
                'name': 'Magic Mouse',
                'price': 79.99,
                'digital': False,
                'image': 'placeholder.png',
            },
            {
                'name': 'T-Shirt Developer',
                'price': 29.99,
                'digital': False,
                'image': 'shirt.jpg',
            },
            {
                'name': 'Sneakers Tech',
                'price': 149.99,
                'digital': False,
                'image': 'shoes.jpg',
            },
        ]
        
        self.stdout.write("\n🔄 Suppression des anciens produits...")
        Product.objects.all().delete()
        
        self.stdout.write("➕ Création des nouveaux produits...")
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            self.stdout.write(f"   ✅ {product.name} - {product.price}€")
        
        self.stdout.write(self.style.SUCCESS(f"\n✨ {len(products_data)} produits créés!"))

    def create_demo_user(self):
        """Crée un utilisateur de démonstration"""
        self.stdout.write("\n👤 Création utilisateur démo...")
        
        User.objects.filter(username='demo').delete()
        
        user = User.objects.create_user(
            username='demo',
            email='demo@example.com',
            password='demo123',
            first_name='Démo',
            last_name='Utilisateur'
        )
        
        Customer.objects.get_or_create(
            user=user,
            defaults={
                'name': f'{user.first_name} {user.last_name}',
                'email': user.email
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f"   ✅ {user.username} créé"))

    def create_admin_user(self):
        """Crée un superutilisateur"""
        self.stdout.write("\n👨‍💼 Création administrateur...")
        
        User.objects.filter(username='admin').delete()
        
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='System'
        )
        
        self.stdout.write(self.style.SUCCESS(f"   ✅ {admin.username} créé"))

