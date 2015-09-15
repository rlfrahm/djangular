from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from account.models import UserProfile
from bars.models import Bar

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

class BarSerializer(serializers.ModelSerializer):
  class Meta:
    model = Bar
    exclude = ('image', 'code')

  def create(self, validated_data):
    bar = Bar()
    bar.name = validated_data.get('name')
    bar.street = validated_data.get('street')
    bar.city = validated_data.get('city')
    bar.province = validated_data.get('province')
    print self.context
    bar.owner = self.context['request'].user
    bar.save()
    return bar