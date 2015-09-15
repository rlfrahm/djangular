from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import SessionAuthentication

from .serializers import RegisterSerializer, LoginSerializer, BarSerializer

from account.models import UserProfile

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
      'email': request.user.email
      })

class UserBarsHandler(APIView):
  """
  Get all bars owned by user
  """
  def get(self, request, format=None):
    bs = request.user.bar_set.all()
    print bs
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

class BarsHandler(APIView):
  """
  CRUD for Bar
  """
  def post(self, request, format=None):
    serializer = BarSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
      bar = serializer.save()
      return Response(serializer.data)
    else:
      return Response({'error': True})