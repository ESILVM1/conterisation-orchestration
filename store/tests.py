from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from .models import Customer, Product, Order, OrderItem, ShippingAddress


class ProductModelTest(TestCase):
    """Tests for Product model"""
    
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=29.99,
            digital=False
        )
    
    def test_product_creation(self):
        """Test product is created correctly"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, 29.99)
        self.assertFalse(self.product.digital)
    
    def test_product_str(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), "Test Product")
    
    def test_product_image_url_no_image(self):
        """Test product imageURL property when no image"""
        self.assertEqual(self.product.imageURL, '')
    
    def test_digital_product(self):
        """Test digital product creation"""
        digital_product = Product.objects.create(
            name="Digital Product",
            price=15.00,
            digital=True
        )
        self.assertTrue(digital_product.digital)


class CustomerModelTest(TestCase):
    """Tests for Customer model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name='Test Customer',
            email='test@example.com'
        )
    
    def test_customer_creation(self):
        """Test customer is created correctly"""
        self.assertEqual(self.customer.name, 'Test Customer')
        self.assertEqual(self.customer.email, 'test@example.com')
        self.assertEqual(self.customer.user, self.user)
    
    def test_customer_str(self):
        """Test customer string representation"""
        self.assertEqual(str(self.customer), 'Test Customer')
    
    def test_customer_without_user(self):
        """Test customer can be created without a user"""
        guest_customer = Customer.objects.create(
            name='Guest Customer',
            email='guest@example.com'
        )
        self.assertIsNone(guest_customer.user)
        self.assertEqual(guest_customer.name, 'Guest Customer')


class OrderModelTest(TestCase):
    """Tests for Order model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name='Test Customer',
            email='test@example.com'
        )
        self.product1 = Product.objects.create(
            name="Physical Product",
            price=25.00,
            digital=False
        )
        self.product2 = Product.objects.create(
            name="Digital Product",
            price=15.00,
            digital=True
        )
        self.order = Order.objects.create(
            customer=self.customer,
            complete=False
        )
    
    def test_order_creation(self):
        """Test order is created correctly"""
        self.assertEqual(self.order.customer, self.customer)
        self.assertFalse(self.order.complete)
        self.assertIsNotNone(self.order.date_ordered)
    
    def test_order_str(self):
        """Test order string representation"""
        self.assertEqual(str(self.order), str(self.order.id))
    
    def test_get_cart_total(self):
        """Test cart total calculation"""
        OrderItem.objects.create(
            product=self.product1,
            order=self.order,
            quantity=2
        )
        OrderItem.objects.create(
            product=self.product2,
            order=self.order,
            quantity=1
        )
        # 2 * 25.00 + 1 * 15.00 = 65.00
        self.assertEqual(self.order.get_cart_total, 65.00)
    
    def test_get_cart_items(self):
        """Test cart items count"""
        OrderItem.objects.create(
            product=self.product1,
            order=self.order,
            quantity=2
        )
        OrderItem.objects.create(
            product=self.product2,
            order=self.order,
            quantity=3
        )
        self.assertEqual(self.order.get_cart_items, 5)
    
    def test_shipping_required_for_physical_product(self):
        """Test shipping is required for physical products"""
        OrderItem.objects.create(
            product=self.product1,
            order=self.order,
            quantity=1
        )
        self.assertTrue(self.order.shipping)
    
    def test_no_shipping_for_digital_product(self):
        """Test no shipping for digital only products"""
        OrderItem.objects.create(
            product=self.product2,
            order=self.order,
            quantity=1
        )
        self.assertFalse(self.order.shipping)
    
    def test_empty_cart_total(self):
        """Test empty cart returns 0"""
        self.assertEqual(self.order.get_cart_total, 0)
        self.assertEqual(self.order.get_cart_items, 0)


class OrderItemModelTest(TestCase):
    """Tests for OrderItem model"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com'
        )
        self.product = Product.objects.create(
            name="Test Product",
            price=20.00,
            digital=False
        )
        self.order = Order.objects.create(
            customer=self.customer,
            complete=False
        )
        self.order_item = OrderItem.objects.create(
            product=self.product,
            order=self.order,
            quantity=3
        )
    
    def test_order_item_creation(self):
        """Test order item is created correctly"""
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.quantity, 3)
    
    def test_get_total(self):
        """Test order item total calculation"""
        self.assertEqual(self.order_item.get_total, 60.00)
    
    def test_get_total_single_item(self):
        """Test order item total for single quantity"""
        single_item = OrderItem.objects.create(
            product=self.product,
            order=self.order,
            quantity=1
        )
        self.assertEqual(single_item.get_total, 20.00)


class ShippingAddressModelTest(TestCase):
    """Tests for ShippingAddress model"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com'
        )
        self.order = Order.objects.create(
            customer=self.customer,
            complete=False
        )
    
    def test_shipping_address_creation(self):
        """Test shipping address is created correctly"""
        address = ShippingAddress.objects.create(
            customer=self.customer,
            order=self.order,
            address='123 Test Street',
            city='Test City',
            state='Test State',
            zipcode='12345'
        )
        self.assertEqual(address.address, '123 Test Street')
        self.assertEqual(address.city, 'Test City')
        self.assertEqual(address.state, 'Test State')
        self.assertEqual(address.zipcode, '12345')
    
    def test_shipping_address_str(self):
        """Test shipping address string representation"""
        address = ShippingAddress.objects.create(
            customer=self.customer,
            order=self.order,
            address='456 Main Avenue',
            city='Sample City',
            state='Sample State',
            zipcode='54321'
        )
        self.assertEqual(str(address), '456 Main Avenue')


class StoreViewTest(TestCase):
    """Tests for store views"""
    
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Test Product",
            price=29.99,
            digital=False
        )
    
    def test_store_view_loads(self):
        """Test store page loads correctly"""
        response = self.client.get(reverse('store'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/store.html')
    
    def test_store_view_contains_products(self):
        """Test store page displays products"""
        response = self.client.get(reverse('store'))
        self.assertContains(response, "Test Product")
    
    def test_cart_view_loads(self):
        """Test cart page loads correctly"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cart.html')
    
    def test_checkout_view_loads(self):
        """Test checkout page loads correctly"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/checkout.html')


class UpdateItemViewTest(TestCase):
    """Tests for updateItem API endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name='Test Customer',
            email='test@example.com'
        )
        self.product = Product.objects.create(
            name="Test Product",
            price=29.99,
            digital=False
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        response = self.client.post(
            reverse('update_item'),
            data=json.dumps({
                'productId': self.product.id,
                'action': 'add'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['quantity'], 1)
    
    def test_remove_item_from_cart(self):
        """Test removing item from cart"""
        # First add item
        order = Order.objects.create(customer=self.customer, complete=False)
        OrderItem.objects.create(
            product=self.product,
            order=order,
            quantity=2
        )
        
        # Then remove one
        response = self.client.post(
            reverse('update_item'),
            data=json.dumps({
                'productId': self.product.id,
                'action': 'remove'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['quantity'], 1)
    
    def test_remove_last_item_deletes_orderitem(self):
        """Test removing last item deletes OrderItem"""
        order = Order.objects.create(customer=self.customer, complete=False)
        OrderItem.objects.create(
            product=self.product,
            order=order,
            quantity=1
        )
        
        response = self.client.post(
            reverse('update_item'),
            data=json.dumps({
                'productId': self.product.id,
                'action': 'remove'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['quantity'], 0)
    
    def test_invalid_product_id(self):
        """Test invalid product ID"""
        response = self.client.post(
            reverse('update_item'),
            data=json.dumps({
                'productId': 99999,
                'action': 'add'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_action(self):
        """Test invalid action"""
        response = self.client.post(
            reverse('update_item'),
            data=json.dumps({
                'productId': self.product.id,
                'action': 'invalid'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_invalid_json(self):
        """Test invalid JSON"""
        response = self.client.post(
            reverse('update_item'),
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_missing_fields(self):
        """Test missing required fields"""
        response = self.client.post(
            reverse('update_item'),
            data=json.dumps({
                'productId': self.product.id
                # missing action
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_unauthenticated_user(self):
        """Test unauthenticated user cannot update cart"""
        self.client.logout()
        response = self.client.post(
            reverse('update_item'),
            data=json.dumps({
                'productId': self.product.id,
                'action': 'add'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login


class LoginViewTest(TestCase):
    """Tests for login functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_page_loads(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/login.html')
    
    def test_successful_login(self):
        """Test successful login"""
        response = self.client.post(
            reverse('login'),
            {
                'username': 'testuser',
                'password': 'testpass123'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertRedirects(response, reverse('store'))
    
    def test_failed_login_wrong_password(self):
        """Test failed login with wrong password"""
        response = self.client.post(
            reverse('login'),
            {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
        )
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'incorrect')
    
    def test_failed_login_missing_fields(self):
        """Test failed login with missing fields"""
        response = self.client.post(
            reverse('login'),
            {
                'username': 'testuser'
                # missing password
            }
        )
        self.assertEqual(response.status_code, 200)
    
    def test_logout(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_already_authenticated_redirect(self):
        """Test authenticated user redirected from login page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store'))
