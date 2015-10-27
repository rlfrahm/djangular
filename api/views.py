from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from .serializers import RegisterSerializer, LoginSerializer, BarSerializer, RoleSerializer, SearchSerializer, TabSerializer, CreditCardSerializer, PayBarSerializer, UserSerializer, AcceptTabSerializer, AvatarSerializer, UserPasswordSerializer, BarsWithinDistanceSerializer
from .decorators import HasGroupPermission, is_in_group, BAR_OWNERS, DRINKERS

from account.models import UserProfile, USER_PROFILE_DEFAULT
from bars.models import Bar, Bartender, RoleInvite, Checkin, Tab, Sale, Transaction, authorize_source, Role
from notifications.emails import send_bartender_invite, send_bar_creation_email

import uuid, datetime, stripe

stripe.api_key = settings.STRIPE_API_KEY

# Create your views here.
class LoginHandler(APIView):
	"""
	Check if user is logged in or log in user
	"""
	authentication_classes = ()
	def get(self, request, format=None):
		return True

	def post(self, request, format=None):
		serializer = LoginSerializer(data=request.data)
		if serializer.is_valid():
			user = authenticate(username=request.data['username'], password=request.data['password'])
			token = Token.objects.get(user=user)
			if token:
				return Response({'token': token.key})
			else:
				return Response({'error': True})

class RegisterHandler(APIView):
	"""
	Create new user
	"""
	authentication_classes = ()
	def post(self, request, format=None):
		serializer = RegisterSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()

			token = Token.objects.create(user=user)

			return Response({'token': token.key})
		else:
			print 'not valid'

		return Response({'error': 'True'})

class UserHandler(APIView):
	"""
	Retrieve, update, delete users
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		d = {
			'username': request.user.username,
			'email': request.user.email,
			'id': request.user.pk,
			'first_name': request.user.first_name,
			'last_name': request.user.last_name,
			'bar_owner': is_in_group(request.user, BAR_OWNERS),
			'avatar': request.user.profile.avatar_url
		}
		if request.user.customer.default_source:
			d['sources'] = True
		return Response(d)

	def post(self, request, format=None):
		serializer = UserSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		request.user.first_name = serializer.validated_data['first_name']
		request.user.last_name = serializer.validated_data['last_name']
		request.user.save()
		return Response({
			'id': request.user.pk,
			'username': request.user.username,
			'email': request.user.email,
			'first_name': request.user.first_name,
			'last_name': request.user.last_name
			})

class UserPasswordHandler(APIView):
	"""
	Change the user's password
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):
		serializer = UserPasswordSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		request.user.set_password(serializer.validated_data['password'])
		request.user.save()
		update_session_auth_hash(request, request.user)
		return Response({
			'success': True
		})

class UserAvatarHandler(APIView):
	"""
	Sets the user's profile image
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, format=None):
		serializer = AvatarSerializer(request.POST, request.FILES)
		serializer.is_valid(raise_exception=True)
		request.user.profile.avatar = serializer.validated_data['avatar']
		request.user.profile.save()
		return Response({
			'success': True
			})

class UserProfileHandler(APIView):
	"""
	Retrieves users based on an id
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, user_id, format=None):
		user = get_object_or_404(User, pk=user_id)
		cs = user.checkin_set.all().order_by('-created')[:10]
		checkins = []
		for checkin in cs:
			checkins.append({
				'when': checkin.when,
				'bar_id': checkin.bar.pk,
				'bar_name': checkin.bar.name
				})
		return Response({
			'id': user.id,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'avatar': user.profile.avatar_url,
			'checkins': checkins
			})

class UserBarsHandler(APIView):
	"""
	Get all bars owned by user
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated, HasGroupPermission,)
	required_groups = {
		'GET': [BAR_OWNERS],
	}

	def get(self, request, format=None):
		bs = request.user.bar_set.all()
		bars = []
		for bar in bs:
			bars.append({
				'id': bar.pk,
				'name': bar.name,
				'street': bar.street,
				'city': bar.city,
				'province': bar.province,
				'owner': bar.owner.pk,
				})
		ub = request.user.role_set.all()
		for b in ub:
			bars.append({
				'id': b.bar.pk,
				'name': b.bar.name,
				'street': b.bar.street,
				'city': b.bar.city,
				'province': b.bar.province,
				'owner': b.bar.owner.pk,
				'bartender': True,
				'working': b.working,
				'bartender_id': b.pk,
				})
		return Response(bars)


class AuthHandler(APIView):
	"""
	Login, register, logout users
	"""

	def delete(self, request, format=None):
		logout(request)
		return Response({
			'logout': True
			})

class BarHandler(APIView):
	"""
	CRUD on bar
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated, HasGroupPermission,)
	required_groups = {
		'GET': [],
		'POST': [BAR_OWNERS],
		'DELETE': [BAR_OWNERS],
	}

	def get(self, request, bar_id, format=None):
		b = get_object_or_404(Bar, pk=self.kwargs.get('bar_id'))
		bar = {
			'name': b.name,
			'street': b.street,
			'city': b.city,
			'province': b.province,
			'postal': b.postal,
			'country': b.country,
			'lat': b.lat,
			'lng': b.lng,
			'id': b.pk,
			'owner': b.owner.pk,
			'avatar': b.avatar_url,
		}
		# Check if we need to add any action items
		# The user has set up a merchant account through Stripe
		bar['merchant'] = hasattr(b.owner, 'merchant')
		return Response(bar)

	# Update bar details
	def post(self, request, bar_id, format=None):
		serializer = BarSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			bar = get_object_or_404(Bar, pk=bar_id)
			if bar.owner != request.user:
				return PermissionDenied()
			bar.name = serializer.validated_data['name']
			bar.street = serializer.validated_data['street']
			bar.city = serializer.validated_data['city']
			bar.province = serializer.validated_data['province']
			bar.postal = serializer.validated_data['postal']
			bar.lat = serializer.validated_data['lat']
			bar.lng = serializer.validated_data['lng']
			bar.save()
			return Response(serializer.data)
		else:
			return Response({'error': True})

	# Delete bar
	def delete(self, request, bar_id, format=None):
		bar = get_object_or_404(Bar, pk=bar_id)
		if bar.owner is not request.user:
			return PermissionDenied()
		bar.delete()
		return Response({'delete': True})

class BarSalesHandler(APIView):
	"""
	CRUD on bar sales
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated, HasGroupPermission,)
	required_groups = {
		'GET': [BAR_OWNERS],
	}

	def get(self, request, bar_id, format=None):
		bar = get_object_or_404(Bar, pk=bar_id)
		s = bar.sale_set.all().order_by('-created')
		sales = []
		for sale in s:
			sales.append({
				'id': sale.pk,
				'amount': sale.amount,
				'customer_first_name': sale.customer.first_name,
				'customer_last_name': sale.customer.last_name,
				'customer_id': sale.customer.pk,
				'bar_id': sale.bar.pk,
				'when': sale.created
			})
		return Response(sales)

class BarSaleHandler(APIView):
	"""
	Handles operations for individual bar sales
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated, HasGroupPermission,)
	required_groups = {
		'PUT': [DRINKERS],
	}
	# Add a tip to a sale
	def put(self, request, bar_id, sale_id, format=None):
		serializer = TipSerializer(data=request.POST)
		serializer.is_valid(raise_exception=True)
		sale = get_object_or_404(Sale, pk=sale_id)
		# Capture the sale with the tip amount
		return Response({})

class BarAvatarHandler(APIView):
	"""
	Sets the user's profile image
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated, HasGroupPermission,)
	required_groups = {
		'POST': [BAR_OWNERS],
	}

	def post(self, request, bar_id, format=None):
		serializer = AvatarSerializer(request.POST, request.FILES)
		serializer.is_valid(raise_exception=True)
		bar = get_object_or_404(Bar, pk=bar_id)
		bar.avatar = serializer.validated_data['avatar']
		bar.save()
		return Response({
			'success': True
			})

class BarsHandler(APIView):
	"""
	CRUD for Bar
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated, HasGroupPermission,)
	required_groups = {
		'GET': [DRINKERS],
		'POST': [BAR_OWNERS],
	}

	def get(self, request, format=None):
		if request.GET.get('distance') and request.GET.get('lat') and request.GET.get('lng'):
			bs = Bar.objects.nearby(request.GET.get('lat'), request.GET.get('lng'), request.GET.get('distance'))
		else:
			bs = Bar.objects.all()
		bars = []
		for bar in bs:
			bars.append({
				'id': bar.pk,
				'name': bar.name,
				'owner': bar.owner.pk,
				'avatar': bar.avatar_url,
				'street': bar.street,
				'city': bar.city,
				'province': bar.province,
				'postal': bar.postal,
				'lat': bar.lat,
				'lng': bar.lng
				})
		return Response(bars)

	# Create new bar
	def post(self, request, format=None):
		serializer = BarSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			# bar = Bar.new(serializer.validated_data['name'], serializer.validated_data, request.user, serializer.validated_data.get('avatar'))
			bar = serializer.save()
			serializer.data['id'] = bar.pk
			send_bar_creation_email(request, bar)
			return Response(serializer.data)
		else:
			return Response({'error': True, 'errors': serializer.errors})

class RolesHandler(APIView):
	"""
	CRUD operations for Bartenders
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, bar_id, format=None):
		bar = get_object_or_404(Bar, pk=bar_id)
		bartenders = []
		for b in bar.bartender_set.all():
			bartenders.append({
				'email': b.user.email,
				'firstname': b.user.first_name,
				'lastname': b.user.last_name,
				'avatar': b.user.profile.avatar_url or USER_PROFILE_DEFAULT,
				'id': b.user.pk,
				})
		return Response(bartenders)

	# Creates a role and returns an invite if needed
	def post(self, request, bar_id, format=None):
		serializer = RoleSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			new_roles = serializer.validated_data.get('role').lower().split(',')
			email = serializer.validated_data.get('email')
			uid = serializer.validated_data.get('uid')
			if not email and not uid:
				return Response(status=status.HTTP_400_BAD_REQUEST)
			# Get the bar
			bar = get_object_or_404(Bar, pk=bar_id)
			if not bar.is_admin(request.user.pk):
				return Response(status=status.HTTP_400_BAD_REQUEST)
			user = None
			if uid:
				user = User.objects.get(pk=uid)
			if not user:
				user = User.objects.filter(email=email)[:1]
				if len(user) > 0:
					user = user[0]
			if user:
				# Use the user's account
				# First, see if this user has a role for this bar
				user_role = user.role_set.filter(bar=bar)[:1]
				if len(user_role) > 0:
					# A role exists, use it
					user_role = user_role[0].split(',') # [role, role, ..]
					for r in new_roles:
						# Check if user already has this role
						if r not in user_role:
							user_role.append(r)
				else:
					# A role does not exist, create a new one
					user_role = Role(user=request.user, bar=bar, roles=''.join(new_roles))
					user_role.save()
			else:
				# Send an email invite
				invite = RoleInvite(bar=bar, email=request.data.get('email'), token=uuid.uuid4(), roles=''.join(new_roles))
				invite.save()
				send_bartender_invite(request, invite)
				# 'bar_id': invite.bar.pk,
				# 'email': invite.email,
				# 'token': invite.token,
			return Response({
				'role': serializer.validated_data.get('role')
				}, status=status.HTTP_201_CREATED)

		# Update an existing role
		def put(self, request, bar_id, format=None):
			print "I should do role things"

class BartendersHandler(APIView):
	"""
	CRUD operations for a bar's bartenders
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, bar_id, format=None):
		bartenders = Role.objects.filter(bar_id=bar_id, roles__icontains='bartender')
		bs = []
		for b in bartenders:
			bs.append({
				'user': b.user.pk,
				'user_first_name': b.user.first_name,
				'user_last_name': b.user.last_name
			})
		return Response(bs, status=status.HTTP_200_OK)

class BartenderHandler(APIView):
	"""
	CRUD operations for a specific bartender
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def put(self, request, bar_id, bartender_id, format=None):
		bartender = get_object_or_404(Bartender, pk=bartender_id)
		bartender.working = request.data.get('working')
		bartender.save()
		return Response({
			'id': bartender.pk,
			'working': bartender.working,
			'user': bartender.user.pk,
			})

class BarCheckinHandler(APIView):
	"""
	Handler for bar checkins by drinkers
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, bar_id, format=None):
		cs = Checkin.objects.filter(bar__pk=bar_id).order_by('-created')[:10]
		checkins = []
		for c in cs:
			checkins.append({
				'id': c.pk,
				'user': c.user.pk,
				'firstname': c.user.first_name,
				'lastname': c.user.last_name,
				'avatar': c.user.profile.avatar_url,
				'bar': c.bar.pk,
				'when': c.when
				})
		return Response(checkins)

	def post(self, request, bar_id, format=None):
		checkin = Checkin.new(bar_id, request.user)
		return Response({
			'id': checkin.pk,
			'user': checkin.user.pk,
			'bar': checkin.bar.pk,
			'when': checkin.when,
			})

class SearchHandler(APIView):
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		serializer = SearchSerializer(data=request.GET)
		if serializer.is_valid():
			term = serializer.validated_data['term']
			r = User.objects.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term))[:10]
			results = []
			for result in r:
				results.append({
					'id': result.pk,
					'first_name': result.first_name,
					'last_name': result.last_name,
					'avatar': result.profile.avatar_url
					})
			return Response(results)
		else:
			return Response([])

class UserSearchHandler(APIView):
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		serializer = SearchSerializer(data=request.GET)
		if serializer.is_valid():
			term = request.GET.get('term')
			users = User.objects.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(email__icontains=term))[:10]
			u = []
			for user in users:
				u.append({
					'id': user.pk,
					'first_name': user.first_name,
					'last_name': user.last_name,
					'avatar': user.profile.avatar_url
				})
			return Response(u)
		else:
			return Response([])

class BarSearchHandler(APIView):
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		serializer = SearchSerializer(data=request.GET)
		if serializer.is_valid():
			term = serializer.validated_data['term']
			bs = Bar.objects.filter(Q(name__icontains=term))
			bars = []
			for bar in bs:
				bars.append({
					'id': bar.pk,
					'name': bar.name,
					'location': bar.location,
					'avatar': bar.avatar_url
					})
			return Response(bars)
		else:
			return Response([])

class UserTabHandler(APIView):
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		tab = request.user.profile.tab
		return Response({'tab': tab})

class TabsHandler(APIView):
	"""
	CRUD operations for user tabs
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		tabs = Tab.objects.filter(receiver=request.user).order_by('accepted', '-created')
		t = []
		for tab in tabs:
			t.append({
				'id': tab.pk,
				'amount': tab.amount,
				'receiver': tab.receiver.pk,
				'sender': tab.sender.pk,
				'sender_first_name': tab.sender.first_name,
				'sender_last_name': tab.sender.last_name,
				'sender_avatar': tab.sender.profile.avatar_url,
				'accepted': tab.accepted,
				'note': tab.note
				})
		return Response(t)

	# Create new tab
	def post(self, request, format=None):
		serializer = TabSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			# The amount in dollars
			amount = serializer.validated_data['amount']
			# The user's payment source
			source = serializer.validated_data['source']
			# The user(s) who are receiving the tab(s)
			users = serializer.validated_data.get('users')
			# The response data
			response = {'tabs': []}
			for u in users:
				uid = u.get('id')
				if not uid:
					email = u.get('email')
				else:
					user = User.objects.get(pk=u['id'])
					if not user:
						# User with this id was not found
						# TODO: fail better than this
						continue
					email = user.email
				# The email associated with the receiver
				receiver_email = email
				# The note added to the tab
				note = serializer.validated_data.get('note')
				# Create a new note
				try:
					tab = Tab.new(amount, receiver_email, source, request.user, request=request, note=note)
				except Exception, e:
					# TODO: fail better than this
					return Response({
						'status': 400,
						'message': 'Authorization of the payment source failed'
					}, status=status.HTTP_400_BAD_REQUEST)
				d = {
					'id': tab.pk,
					'sender': tab.sender.pk,
					'amount': tab.amount,
				}
				if tab.email:
					d['email'] = tab.email
				if tab.receiver:
					d['receiver'] = tab.receiver.pk
				response['tabs'].append(d)
			response['amount'] = amount
			return Response(response)

class TabsAccepted(APIView):
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		ts = request.user.tab_set.filter(accepted=False)
		tabs = []
		for tab in ts:
			tabs.append({
				'id': tab.pk,
				'amount': tab.amount,
				'sender': tab.sender.pk,
				'sender_first_name': tab.sender.username
				})


class TabHandler(APIView):
	"""
	Handles the acceptance of a tab
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def post(self, request, tab_id, format=None):
		serializer = AcceptTabSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		tab = get_object_or_404(Tab, pk=tab_id)
		accepted = serializer.validated_data['accepted']
		if accepted:
			tab.accepted = True

			# Add the amount to the user's tab
			tab.receiver.profile.tab += tab.amount
			tab.receiver.profile.save()
			tab.save()
		else:
			tab.delete()

		return Response({
			'id': tab.pk,
			'accepted': tab.accepted
			})

class SourcesHandler(APIView):
	"""
	CRUD operations for Stripe sources
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		sources = stripe.Customer.retrieve(request.user.customer.customer_id).sources.all()
		data = sources.get('data')
		for s in data:
			if s['id'] == request.user.customer.default_source:
				s.default_source = True
		return Response(data)

	# Create new source
	def post(self, request, format=None):
		serializer = CreditCardSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		customer = stripe.Customer.retrieve(request.user.customer.customer_id)
		source = customer.sources.create(source=serializer.validated_data['token'])
		if request.user.customer.default_source == '':
			request.user.customer.default_source = source.get('id')
			request.user.customer.save()
		return Response({'success': True})

class SourceHandler(APIView):
	"""
	Handles source
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	# Set default source
	def post(self, request, source_id, format=None):
		customer = stripe.Customer.retrieve(request.user.customer.customer_id)
		source = customer.sources.retrieve(source_id)
		id = source.get('id')
		if id == source_id:
			request.user.customer.default_source = source_id
			request.user.customer.save()
			return Response({'source': source_id})
		else:
			return Response({'source': False})

class PayBarHandler(APIView):
	"""
	Handles payment at bars
	"""
	authentication_classes = (SessionAuthentication,)
	permission_classes = (IsAuthenticated,)

	# Create new payment
	# Payments from individual sources must be at least
	# $5. We iterate through the total payment amount
	# and select, then use, tabs that are open. If we
	# run out of open tabs we use the user's card on
	# file.
	def post(self, request, bar_id, format=None):
		serializer = PayBarSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		bar = get_object_or_404(Bar, pk=bar_id)
		open_tabs = Tab.objects.filter(receiver=request.user, accepted=True).order_by('created')
		# Hold the last charge id so we know what source
		# to charge the rest of the payment.
		charge = None

		# This is the amount of the sale
		amount = serializer.validated_data['amount']
		# This is the amount of the sale left to pay
		amount_left = amount

		# Open a new sale
		sale = Sale(amount=amount, bar=bar, customer=request.user)
		sale.save()

		# This is the amount of money in the user's tab
		total_tab = request.user.profile.tab
		# Track the each tab used in this transaction
		tabs_used = []
		tabs_deleted = []
		for tab in open_tabs:
			# Iterate through open tabs until we
			# 1) Run out of tabs to extract money from
			# 2) Suffice the amount of money needed to be withdrawn
			authorize = False
			charge_amt = 0

			# Check to make sure that the rest of the amount is greater
			# than the minimum amount that can be put on a card.
			# If the amount left is less than the minimum we need
			# to alert the client.
			if amount_left == 0:
				break
			elif amount_left < settings.MIN_CARD_COST:
				# The amount left is less than the MIN_CARD_COST
				# We need them to add more money to the charge
				tabs_used.append({
					'tab_id': tab.pk,
					'sender_first_name': tab.sender.first_name,
					'sender_last_name': tab.sender.last_name,
					'sender': tab.sender.pk,
					'amount': amount_left,
					'amount_needed': settings.MIN_CARD_COST - amount_left,
					'error': True,
					'type': 'tab'
				})
				# return Response({'error': True})
				continue

			if amount_left < tab.amount:
				# When the amount left is less than this tab
				# Just use this tab and only authorize the tab just in case
				# a tip is added
				# Adjust the amount left on this tab
				tab.amount -= amount_left
				# Adjust the user's total tab amount
				total_tab -= float(tab.amount)
				charge_amt = amount_left
				# Adjust the amount_left
				amount_left = 0
				authorize = True
			elif amount_left > tab.amount:
				# When the amount left is more than this tab
				# Use all of this tab and capture the charge
				total_tab -= float(tab.amount)
				charge_amt = tab.amount
				# Adjust the amount_left
				amount_left -= tab.amount
				authorize = False
			else:
				# When the amount left is equal to this tab
				# Amounts are equal; remove & break
				total_tab -= float(amount_left)
				charge_amt = amount_left
				# Adjust the amount_left
				amount_left -= tab.amount
				authorize = False

			t_data = {
				'tab_id': tab.pk,
				'sender_first_name': tab.sender.first_name,
				'sender_last_name': tab.sender.last_name,
				'sender': tab.sender.pk,
				'amount': charge_amt,
				'type': 'tab'
			}

			transaction = Transaction(sale=sale, owner=tab.sender, source=tab.source, amount=charge_amt)

			if authorize:
				# We want to only authorize this charge just in case
				# the user adds a tip
				status = transaction.authorize()
				if status:
					t_data['status'] = 'authorized'
				else:
					# TODO: account for failed authorization
					print 'Authorization failed for tab: %s' % tab.pk
				# charge = authorize_source(amount_left, tab.sender.customer.customer_id, tab.source, request.user.email)
			else:
				# We want to charge the source
				transaction.charge = tab.charge
				status = transaction.process()
				if status:
					t_data['status'] = 'charged'
				else:
					# TODO: account for failed charge
					print 'Charge failed for tab: %s' % tab.pk
				tab.delete()
				# charge_source(tab.sender.customer.customer_id, tab.source, bar.owner.merchant.account_id, tab.amount, tab.charge)
			if tab.amount < settings.MIN_CARD_COST:
				tabs_deleted.append({
					'sender_first_name': tab.sender.first_name,
					'sender_last_name': tab.sender.last_name,
					'amount': tab.amount
				})
				tab.delete()
			transaction.save()
			t_data['transaction_id'] = transaction.pk
			tabs_used.append(t_data)

		request.user.profile.tab = total_tab
		request.user.profile.save()

		if amount_left > 0:
			# We need to use the user's financial source
			if request.user.customer.default_source != '':
				transaction = Transaction(sale=sale, owner=request.user, source=request.user.customer.default_source, amount=amount_left)
				t = {
					'type': 'user',
					'amount': amount_left
				}
				if amount_left < settings.MIN_CARD_COST:
					t['amount_needed'] = settings.MIN_CARD_COST - amount_left
					t['error'] = True
				else:
					t['status'] = 'authorized'
					status = transaction.authorize()
				transaction.save()
				t['transaction_id'] = transaction.pk
				tabs_used.append(t)
				# authorize_source(amount_left, request.user.customer.customer_id, request.user.customer.default_source, request.user.email, bar.owner.merchant.account_id)
		return Response({'tab': total_tab, 'sale': sale.pk, 'transactions': tabs_used, 'removed': tabs_deleted})
