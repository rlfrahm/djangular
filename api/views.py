from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import SessionAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, BarSerializer, InviteSerializer, SearchSerializer, TabSerializer, CreditCardSerializer, PayBarSerializer

from account.models import UserProfile
from bars.models import Bar, Bartender, BartenderInvite, Checkin, Tab
from bars.emails import send_bartender_invite

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
      print request.data
      print user
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
    print request.data
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
  def get(self, request, format=None):
    return Response({
      'username': request.user.username,
      'email': request.user.email,
      'id': request.user.pk,
      })

class UserBarsHandler(APIView):
  """
  Get all bars owned by user
  """
  def get(self, request, format=None):
    bs = request.user.bar_set.all()
    bars = []
    for bar in bs:
      print bar.name
      bars.append({
        'id': bar.pk,
        'name': bar.name,
        'street': bar.street,
        'city': bar.city,
        'province': bar.province,
        'owner': bar.owner.pk,
        })
    ub = request.user.bartender_set.all()
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
    logout(request.user)
    return Response({
      'logout': True
      })

class BarHandler(APIView):
  """
  CRUD on bar
  """
  def get(self, request, bar_id, format=None):
    b = get_object_or_404(Bar, pk=self.kwargs.get('bar_id'))
    bar = {
      'name': b.name,
      'street': b.street,
      'city': b.city,
      'province': b.province,
      'id': b.pk,
      'owner': b.owner.pk
    }
    return Response(bar)

  def post(self, request, bar_id, format=None):
    print request.data
    serializer = BarSerializer(data=request.data, context={'request': request})
    print serializer.is_valid()
    if serializer.is_valid():
      bar = get_object_or_404(Bar, pk=bar_id)
      bar.name = request.data.get('name')
      bar.save()
      return Response(serializer.data)
    else:
      return Response({'error': True})

  def delete(self, request, bar_id, format=None):
    bar = get_object_or_404(Bar, pk=bar_id)
    bar.delete()
    return Response({'delete': True})

class BarsHandler(APIView):
  """
  CRUD for Bar
  """
  def get(self, request, format=None):
    bs = Bar.objects.all()
    bars = []
    for bar in bs:
      bars.append({
        'id': bar.pk,
        'name': bar.name,
        'owner': bar.owner.pk
        })
    return Response(bars)

  def post(self, request, format=None):
    serializer = BarSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
      bar = serializer.save()
      return Response(serializer.data)
    else:
      return Response({'error': True})

class BartendersHandler(APIView):
  """
  CRUD operations for Bartenders
  """
  def get(self, request, bar_id, format=None):
    bar = get_object_or_404(Bar, pk=bar_id)
    bartenders = []
    for b in bar.bartender_set.all():
      bartenders.append({
        'email': b.user.email,
        'firstname': b.user.first_name,
        'lastname': b.user.last_name,
        'id': b.user.pk,
        })
    return Response(bartenders)

  # Creates and returns a BartenderInvite
  def post(self, request, bar_id, format=None):
    serializer = InviteSerializer(data=request.data, context={'request': request, 'bar_id': bar_id})
    if serializer.is_valid(raise_exception=True):
      # invite = serializer.save()
      bar = get_object_or_404(Bar, pk=bar_id)
      invite = BartenderInvite(bar=bar, email=request.data.get('email'), token=uuid.uuid4())
      invite.save()
      send_bartender_invite(request, invite)
      return Response({
        'bar_id': invite.bar.pk,
        'email': invite.email,
        'token': invite.token,
        })

class BartenderHandler(APIView):
  """
  CRUD operations for a specific bartender
  """
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
  def get(self, request, bar_id, format=None):
    cs = Checkin.objects.filter(bar__pk=bar_id).order_by('-created')[:10]
    checkins = []
    for c in cs:
      checkins.append({
        'id': c.pk,
        'user': c.user.pk,
        'firstname': c.user.first_name,
        'bar': c.bar.pk,
        'when': c.when
        })
    return Response(checkins)

  def post(self, request, bar_id, format=None):
    checkin = Checkin()
    checkin.bar = get_object_or_404(Bar, pk=bar_id)
    checkin.user = request.user
    checkin.when = datetime.now()
    checkin.save()
    return Response({
      'id': checkin.pk,
      'user': checkin.user.pk,
      'bar': checkin.bat.pk,
      'when': checkin.when,
      })

class UserSearchHandler(APIView):
  def get(self, request, format=None):
    serializer = SearchSerializer(data=request.GET)
    if serializer.is_valid():
      term = request.GET.get('term')
      users = User.objects.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(email__icontains=term))
      u = []
      for user in users:
        u.append({
          'id': user.pk,
          'first_name': user.first_name,
          'last_name': user.last_name,
          'email': user.email,
        })
      return Response(u)
    else:
      return Response([])

class BarSearchHandler(APIView):
  def get(self, request, format=None):
    serializer = SearchSerializer(data=request.GET)
    if serializer.is_valid():
      term = serializer.validated_data['term']
      bs = Bar.objects.filter(Q(name__icontains=term))
      bars = []
      for bar in bs:
        bars.append({
          'id': bar.pk,
          'name': bar.name
          })
      return Response(bars)
    else:
      return Response([])

class UserTabHandler(APIView):
  def get(self, request, format=None):
    tab = request.user.profile.tab
    return Response({'tab': tab})

class TabsHandler(APIView):
  """
  CRUD operations for user tabs
  """
  def get(self, request, format=None):
    tabs = Tab.objects.filter(receiver=request.user)
    t = []
    for tab in tabs:
      t.append({
        'id': tab.pk,
        'amount': tab.amount,
        'receiver': tab.receiver.pk,
        'sender': tab.sender.pk
        })
    return Response(t)

  def post(self, request, format=None):
    serializer = TabSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
      tab = Tab()
      tab.amount = serializer.validated_data['amount']
      tab.sender = request.user
      tab.source = serializer.validated_data['source']
      tab = tab.set_receiver(request, serializer.validated_data['email'])
      tab.save()

      # Add the amount to the user's tab unless there was an invite sent
      if tab.receiver:
        request.user.profile.tab += tab.amount

      return Response({
        'id': tab.pk,
        'sender': tab.sender.pk,
        'email': tab.email,
        'amount': tab.amount,
        })

class SourcesHandler(APIView):
  """
  CRUD operations for Stripe sources
  """
  def get(self, request, format=None):
    sources = stripe.Customer.retrieve(request.user.stripe.customer_id).sources.all()
    return Response(sources.get('data'))

  def post(self, request, format=None):
    serializer = CreditCardSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    customer = stripe.Customer.retrieve(request.user.stripe.customer_id)
    customer.sources.create(source=serializer.validated_data['token'])
    return Response({'success': True})

class PayBarHandler(APIView):
  """
  Handles payment at bars
  """
  # Create new payment
  def post(self, request, format=None):
    return Response(True)
