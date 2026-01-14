from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import json
import datetime
import logging
import uuid
from .models import Customer, Product, Order, OrderItem, ShippingAddress
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

@require_http_methods(["POST"])
@csrf_protect
@login_required
def updateItem(request):
	"""Update cart item with proper validation and error handling"""
	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON'}, status=400)
	
	# Validate input data
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
			# Limit maximum quantity to prevent abuse
			if orderItem.quantity > 100:
				orderItem.quantity = 100
		elif action == 'remove':
			orderItem.quantity -= 1
		
		orderItem.save()
		
		if orderItem.quantity <= 0:
			orderItem.delete()
			return JsonResponse({
				'success': True,
				'message': 'Item removed',
				'quantity': 0
			}, status=200)
		
		return JsonResponse({
			'success': True,
			'message': 'Item updated',
			'quantity': orderItem.quantity
		}, status=200)
		
	except Exception as e:
		logger.error(f"Error updating item: {str(e)}")
		return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["POST"])
@csrf_protect
def processOrder(request):
	"""Process order with server-side price validation"""
	try:
		data = json.loads(request.body)
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON'}, status=400)
	
# Use a UUID for transaction IDs to avoid collisions and predictability
        transaction_id = str(uuid.uuid4())
	
	try:
		if request.user.is_authenticated:
			try:
				customer = request.user.customer
				order, created = Order.objects.get_or_create(customer=customer, complete=False)
			except AttributeError:
				# User has no customer profile, treat as guest
				customer, order = guestOrder(request, data)
		else:
			customer, order = guestOrder(request, data)
	except ValidationError as e:
		logger.warning(f"Validation error in order: {str(e)}")
		return JsonResponse({'error': str(e)}, status=400)
	except Exception as e:
		logger.error(f"Error creating order: {str(e)}")
		return JsonResponse({'error': 'Error processing order'}, status=500)
	
	# CRITICAL: Recalculate total on server side - NEVER trust client
	calculated_total = float(order.get_cart_total)
	
	# Validate order has items
	if calculated_total <= 0:
		return JsonResponse({'error': 'Cart is empty'}, status=400)
	
	# Optional: Log if client total doesn't match (for security monitoring)
	try:
		client_total = float(data.get('form', {}).get('total', 0))
		if abs(client_total - calculated_total) > 0.01:  # Tolerance for rounding
			logger.warning(f"Price mismatch detected: client={client_total}, server={calculated_total}, order={order.id}")
	except (ValueError, TypeError):
		pass  # Ignore invalid client total, we use server calculation anyway
	
	# Always use server-calculated total
	order.transaction_id = str(transaction_id)
	order.complete = True  # Complete order based on server calculation
	order.save()
	
	# Handle shipping address with validation
	if order.shipping:
		shipping_data = data.get('shipping', {})
		
		# Validate required shipping fields
		required_fields = ['address', 'city', 'state', 'zipcode']
		if not all(key in shipping_data for key in required_fields):
			return JsonResponse({'error': 'Missing shipping information'}, status=400)
		
		# Validate and sanitize shipping data
		try:
			# Sanitize and validate shipping fields
			address = shipping_data['address'].strip()[:200]
			city = shipping_data['city'].strip()[:200]
			state = shipping_data['state'].strip()[:200]
			zipcode = shipping_data['zipcode'].strip()[:200]
			
			# Basic validation - ensure fields are not empty after strip
			if not all([address, city, state, zipcode]):
				return JsonResponse({'error': 'All shipping fields are required'}, status=400)
			
			ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=address,
				city=city,
				state=state,
				zipcode=zipcode,
			)
		except Exception as e:
			logger.error(f"Error creating shipping address: {str(e)}")
			return JsonResponse({'error': 'Error saving shipping address'}, status=500)
	
	return JsonResponse({
		'success': True,
		'message': 'Payment submitted',
		'transaction_id': transaction_id
	}, status=200)