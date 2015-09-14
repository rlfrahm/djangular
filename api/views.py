from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer

from accounts.models import UserProfile

# Create your views here.
class LoginHandler(APIView):
  """
  Check if user is logged in or log in user
  """
  def get(self, request, format=None):
    return True

  def post(self, request, format=None):
    
    return Response({'howdy': 'there'})

class RegisterHandler(APIView):
  """
  Create new user
  """
  def post(self, request, format=None):
    serializer = RegisterSerializer(data=request.data)
    print request.data
    if serializer.is_valid():
      print serializer.data
      user = User.objects.create_user(serializer.data['username'], serializer.data['email'], serializer.data['password'])
      user.save()

      token = Token.objects.create(user=user)

      return Response({'token': token})
    else:
      print 'not valid'

    return Response({'error': 'True'})