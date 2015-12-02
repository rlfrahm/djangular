from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.conf import settings

from account.models import UserProfile

class LoginSerializer(serializers.Serializer):
  username = serializers.CharField(max_length=255)
  password = serializers.CharField(max_length=255)

  def authenticate(self, validated_data):
    """
    Uses Django's authenticate function
    """
    print validated_data
    return authenticate(self.validated_data['username'], self.validated_data['password'])

class RegisterSerializer(serializers.Serializer):
  username = serializers.CharField(max_length=255)
  email = serializers.EmailField()
  password = serializers.CharField(max_length=255)
  dob = serializers.DateField(required=False)

  def create(self, validated_data):
    """
    Create and return a new 'User' instance, given the validated data
    """
    user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
    user.save()
    profile = UserProfile(user=user)
    profile.save()
    return user

class UserSerializer(serializers.Serializer):
  first_name = serializers.CharField(max_length=255)
  last_name = serializers.CharField(max_length=255)

class UserPasswordSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255)

class AvatarSerializer(serializers.Serializer):
  avatar = serializers.ImageField()

class RoleSerializer(serializers.Serializer):
  email = serializers.EmailField(required=False)
  uid = serializers.IntegerField(min_value=1, required=False)
  role = serializers.CharField(max_length=100)

class SearchSerializer(serializers.Serializer):
  term = serializers.CharField(max_length=25)
