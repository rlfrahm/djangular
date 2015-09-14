from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer

# Create your views here.
def loginHandler(APIView):
  """
  Check if user is logged in or log in user
  """
  def get(self, request, format=None):
    return True

def registerHandler(APIView):
  """
  Create new user
  """
  def post(self, request, format=None):
    serializer = RegisterSerializer(data=request.data)
    return request.data
    if serializer.is_valid():
      print serializer.data