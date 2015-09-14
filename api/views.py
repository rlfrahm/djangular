from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, LoginSerializer

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