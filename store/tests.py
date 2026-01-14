import json
import uuid
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Customer, Product, Order


class StoreBackendTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.customer = Customer.objects.create(user=self.user, name='Test User', email='test@example.com')
        self.product = Product.objects.create(name='Test Product', price=9.99, digital=False)

    def test_update_item_add_and_remove(self):
        self.client.force_login(self.user)
        url = reverse('update_item')
        resp = self.client.post(url, data=json.dumps({'productId': self.product.id, 'action': 'add'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('quantity'), 1)

        # add again
        resp = self.client.post(url, data=json.dumps({'productId': self.product.id, 'action': 'add'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('quantity'), 2)

        # remove
        resp = self.client.post(url, data=json.dumps({'productId': self.product.id, 'action': 'remove'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('quantity'), 1)

    def test_process_order_guest_creates_order(self):
        # set cookie cart for guest
        self.client.cookies.load({'cart': json.dumps({str(self.product.id): {'quantity': 2}})})
        url = reverse('process_order')
        payload = {'form': {'name': 'Guest', 'email': 'guest@example.com', 'total': '19.98'}, 'shipping': {'address':'1 Test St','city':'City','state':'ST','zipcode':'12345'}}
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        # transaction id should be a uuid
        tid = data.get('transaction_id')
        uuid.UUID(tid)

        # check order exists for guest email and is complete
        customer = Customer.objects.get(email='guest@example.com')
        order = Order.objects.filter(customer=customer).order_by('-id').first()
        self.assertIsNotNone(order)
        self.assertTrue(order.complete)
