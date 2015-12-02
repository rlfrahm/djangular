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

from .serializers import RegisterSerializer, LoginSerializer, RoleSerializer, SearchSerializer, UserSerializer, AvatarSerializer, UserPasswordSerializer
from .decorators import HasGroupPermission, is_in_group

from account.models import UserProfile, USER_PROFILE_DEFAULT
# from notifications.emails import send_bartender_invite, send_bar_creation_email

import uuid, datetime

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
			'avatar': request.user.profile.avatar_url
		}
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
		return Response({
			'id': user.id,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'avatar': user.profile.avatar_url,
			})

class AuthHandler(APIView):
	"""
	Login, register, logout users
	"""

	def delete(self, request, format=None):
		logout(request)
		return Response({
			'logout': True
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
