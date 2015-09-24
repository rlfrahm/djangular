from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from account.models import UserProfile
from bars.models import Bar, BartenderInvite

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
    bar.owner = self.context['request'].user
    bar.save()
    return bar

  def update(self):
    print self.context['request']
    bar = get_object_or_404(Bar, pk=self.context['request'].id)
    bar.name = self.context['request'].name
    bar.street = self.context['request'].street
    bar.city = self.context['request'].city
    bar.province = self.context['request'].province
    bar.save()
    return bar

class InviteSerializer(serializers.Serializer):
  email = serializers.EmailField()

  def create(self, validated_data):
    user = self.context['request'].user
    print self.context['bar_id']
    bar = get_object_or_404(Bar, pk=self.context['bar_id'])
    print bar
    invite = BartenderInvite(bar=bar, email=validated_data.get('email'))
    invite.save()
    return invite

class SearchSerializer(serializers.Serializer):
  term = serializers.CharField(max_length=25)

class TabSerializer(serializers.Serializer):
  amount = serializers.DecimalField(max_digits=6, decimal_places=2)
  email = serializers.EmailField()
  source = serializers.CharField(max_length=100)
  note = serializers.CharField(max_length=140, required=False)

class AcceptTabSerializer(serializers.Serializer):
  accepted = serializers.BooleanField()

class CreditCardSerializer(serializers.Serializer):
  token = serializers.CharField(max_length=100)

class PayBarSerializer(serializers.Serializer):
  amount = serializers.DecimalField(max_digits=8, decimal_places=2)