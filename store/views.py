from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
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

def loginPage(request):
	"""Handle user login"""
	if request.user.is_authenticated:
		return redirect('store')
	
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		if not username or not password:
			messages.error(request, 'Veuillez remplir tous les champs')
			return render(request, 'store/login.html')
		
		user = authenticate(request, username=username, password=password)
		
		if user is not None:
			auth_login(request, user)
			messages.success(request, f'Bienvenue {user.username} !')
			
			# Redirect to next page or store
			next_page = request.GET.get('next', 'store')
			return redirect(next_page)
		else:
			messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')
	
	return render(request, 'store/login.html')

def logoutUser(request):
	"""Handle user logout"""
	auth_logout(request)
	messages.success(request, 'Vous avez été déconnecté avec succès')
	return redirect('login')

def payment(request):
	"""Display payment page"""
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	
	# Redirect if cart is empty
	if cartItems == 0:
		messages.warning(request, 'Votre panier est vide')
		return redirect('cart')
	
	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'store/payment.html', context)

@require_http_methods(["POST"])
@csrf_protect
def processPayment(request):
	"""Process payment with card simulation"""
	try:
		card_number = request.POST.get('card_number', '').replace(' ', '')
		card_holder = request.POST.get('card_holder', '')
		expiry = request.POST.get('expiry', '')
		cvv = request.POST.get('cvv', '')
		
		# Validate fields
		if not all([card_number, card_holder, expiry, cvv]):
			messages.error(request, 'Veuillez remplir tous les champs')
			return redirect('payment')
		
		# Simulate payment failure for specific card number
		if card_number == '0000000000000000':
			messages.error(request, '❌ Paiement refusé ! Carte invalide ou fonds insuffisants.')
			logger.warning(f"Payment failed simulation for card: {card_number}")
			return redirect('payment')
		
		# Process order for successful payment
		data = cartData(request)
		order = data['order']
		
		if order.get_cart_total <= 0:
			messages.error(request, 'Votre panier est vide')
			return redirect('cart')
		
		# Create transaction
		transaction_id = datetime.datetime.now().timestamp()
		order.transaction_id = str(transaction_id)
		order.complete = True
		order.save()
		
		# Store order info in session for confirmation page
		request.session['last_order'] = {
			'transaction_id': str(int(transaction_id)),
			'total': str(order.get_cart_total),
			'items_count': order.get_cart_items
		}
		
		logger.info(f"Payment successful for order: {transaction_id}")
		messages.success(request, '✅ Paiement réussi ! Votre commande a été confirmée.')
		
		return redirect('order_success')
		
	except Exception as e:
		logger.error(f"Error processing payment: {str(e)}")
		messages.error(request, 'Une erreur est survenue lors du paiement')
		return redirect('payment')

def orderSuccess(request):
	"""Display order confirmation page"""
	# Get order info from session
	order_info = request.session.get('last_order')
	
	if not order_info:
		messages.warning(request, 'Aucune commande récente trouvée')
		return redirect('store')
	
	# Clear cart cookie
	response = render(request, 'store/order_success.html', {
		'transaction_id': order_info.get('transaction_id'),
		'total': order_info.get('total'),
		'items_count': order_info.get('items_count'),
		'date': datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')
	})
	
	# Clear cart
	response.set_cookie('cart', '{}')
	
	# Clear session order
	if 'last_order' in request.session:
		del request.session['last_order']
	
	return response