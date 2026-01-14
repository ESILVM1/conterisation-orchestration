import json
import logging
import re
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import EmailValidator
from .models import *

logger = logging.getLogger(__name__)

def cookieCart(request):
	"""Parse cart from cookies with proper error handling"""
	try:
		cart = json.loads(request.COOKIES.get('cart', '{}'))
	except (json.JSONDecodeError, KeyError) as e:
		logger.warning(f"Invalid cart cookie: {str(e)}")
		cart = {}

	items = []
	order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        # cartItems will be computed after processing items to avoid stale value
        cartItems = 0
	for product_id_str in cart:
		try:
			# Validate product ID is an integer
			product_id = int(product_id_str)
			# Use original string key to access cart dict
			quantity = int(cart[product_id_str].get('quantity', 0))
			
			# Validate quantity is positive
			if quantity <= 0:
				continue
			
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
			logger.warning(f"Invalid cart item {product_id_str}: {str(e)}")
			continue
			
        # Update cartItems based on the order aggregation
        cartItems = order['get_cart_items']
def cartData(request):
	"""Get cart data for authenticated or guest user"""
	if request.user.is_authenticated:
		try:
			customer = request.user.customer
			order, created = Order.objects.get_or_create(customer=customer, complete=False)
			items = order.orderitem_set.all()
			cartItems = order.get_cart_items
		except AttributeError:
			# User has no customer profile, use cookie cart
			cookieData = cookieCart(request)
			cartItems = cookieData['cartItems']
			order = cookieData['order']
			items = cookieData['items']
	else:
		cookieData = cookieCart(request)
		cartItems = cookieData['cartItems']
		order = cookieData['order']
		items = cookieData['items']

	return {'cartItems': cartItems, 'order': order, 'items': items}

	
def guestOrder(request, data):
	"""Create order for guest user with proper validation"""
	form_data = data.get('form', {})
	
	name = form_data.get('name', '').strip()
	email = form_data.get('email', '').strip()
	
	# Validate name
	if not name or len(name) < 2 or len(name) > 200:
		raise ValidationError('Invalid name: must be between 2 and 200 characters')
	
	# Validate email
	email_validator = EmailValidator()
	try:
		email_validator(email)
	except ValidationError:
		raise ValidationError('Invalid email address')
	
	# Sanitize name (remove potentially dangerous characters)
	name = re.sub(r'[<>"\']', '', name)
	
	cookieData = cookieCart(request)
	items = cookieData['items']
	
	try:
		customer, created = Customer.objects.get_or_create(email=email)
		customer.name = name
		customer.save()
	except Exception as e:
		logger.error(f"Error creating customer: {str(e)}")
		raise
	
	try:
		order = Order.objects.create(customer=customer, complete=False)
	except Exception as e:
		logger.error(f"Error creating order: {str(e)}")
		raise
	
	# Create order items with validation
	if not items:
		raise ValidationError('Cart is empty')
	
	for item in items:
		try:
			product = Product.objects.get(id=item['id'])
			quantity = max(1, int(item.get('quantity', 1)))  # Minimum 1, validate type
			# Limit maximum quantity to prevent abuse
			quantity = min(quantity, 100)
			
			OrderItem.objects.create(
				product=product,
				order=order,
				quantity=quantity,
			)
		except Product.DoesNotExist:
			logger.warning(f"Product {item.get('id')} not found when creating guest order")
			continue
		except (ValueError, TypeError) as e:
			logger.warning(f"Invalid quantity for product {item.get('id')}: {str(e)}")
			continue
		except Exception as e:
			logger.error(f"Error creating order item: {str(e)}")
			continue
	
	return customer, order

