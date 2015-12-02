from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.views.decorators.http import require_GET

from .forms import LoginForm, RegisterForm, ProfileForm, Step1Form, EmailForm, Step2Form
from .models import UserProfile, PasswordResetToken, AccountActivationToken
from notifications.emails import send_password_reset_email, send_account_activate_email

from core.decorators import anonymous_required

import urllib, urllib2, json, uuid

def loginHandler(request):
	form = None
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['email'][:30]
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				continue_url = request.GET.get('next')
				if continue_url:
					return HttpResponseRedirect(continue_url)
				return HttpResponseRedirect('/')
			else:
				form.add_error(None, 'Invalid username or password')
			# else:
			#   # invalid login
			#   return HttpResponseRedirect('/login')
	else:
		if request.user.is_authenticated():
			return HttpResponseRedirect('/')
		else:
			form = LoginForm()

	return render(request, 'registration/login.html', {'form': form})

def registerHandler(request):
	if settings.SIGN_UP_LOCKED:
		return render(request, 'registration/disabled.html')
	form = None
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			# Check for dupe users
			email = form.cleaned_data['email']
			users = User.objects.filter(email=email)
			if len(users) > 0:
				# User already exists with this email
				form.add_error(None, 'User exists with that email already. Did you mean to login?')
				return render(request, 'registration/register.html', {'form': form})
			firstname = form.cleaned_data['firstname']
			lastname = form.cleaned_data['lastname']
			username = form.cleaned_data['email'][:30]
			password = form.cleaned_data['password']
			dob = form.cleaned_data['dob']

			# Shiny new saved user
			user = UserProfile.new(email, password, firstname, lastname, dob)

			# Email activation
			token = AccountActivationToken(user=user, token=uuid.uuid4())
			token.save()
			send_account_activate_email(request, token)

			user = authenticate(username=username, password=password)
			login(request, user)
			continue_url = request.GET.get('next')
			if continue_url:
				return HttpResponseRedirect(continue_url)
			return HttpResponseRedirect('/register/step-1')
	else:
		if request.user.is_authenticated():
			return HttpResponseRedirect('/')
		else:
			form = RegisterForm()

	return render(request, 'registration/register.html', {'form': form})

def handle_uploaded_file(f, filename):
	with open('some/file/name.txt', 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

@login_required
def step1Handler(request):
	if request.method == 'POST':
			form = Step1Form(request.POST, request.FILES)
			if form.is_valid():
					request.user.profile.avatar = form.cleaned_data['avatar']
					request.user.profile.save()
			return redirect(reverse('user:register-step-2'))
	else:
		form = Step1Form()
	return render(request, 'registration/step-1.html')

@login_required
def step2Handler(request):
	if request.method == 'POST':
		form = Step2Form(request.POST)
		# if form.is_valid():
		# 	source = customer.sources.create(source=form.cleaned_data['token'])
		# 	if request.user.customer.default_source == '':
		# 		request.user.customer.default_source = source.get('id')
		# 		request.user.customer.save()
		return redirect(reverse('core:home'))
	else:
			form = Step1Form()
	return render(request, 'registration/step-2.html', {'stripe_pk': settings.STRIPE_PUB_API_KEY})

def logoutHandler(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required
def profileHandler(request):
	form = ProfileForm()
	return render(request, 'user/user_settings_profile.html', {'form': form})

@login_required
def userHandler(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render(request, 'user/user.html', {'user': user})

def resetPasswordFormHandler(request):
	if request.method == 'POST':
		form = EmailForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			users = User.objects.filter(email=email)
			if len(users) < 1:
				# No user, fail
				form.add_error(None, 'No user exists with that email.')
				return render(request, 'registration/reset_password.html', {'form': form})
			user = users[0]
			passResetToken = PasswordResetToken.objects.filter(user=user)
			if len(passResetToken) < 1:
				passResetToken = PasswordResetToken.new(user)
				send_password_reset_email(request, passResetToken)
				passResetToken.save()
				return redirect(reverse('user:login'))
			else:
				form.add_error(None, 'An email has already been sent to that email.')
	else:
		form = EmailForm()
	return render(request, 'registration/reset_password.html', {'form': form})

@anonymous_required()
def resetPasswordHandler(request, token):
		if request.method == 'GET':
				passResetToken = get_object_or_404(PasswordResetToken, token=token)
				if passResetToken:
						passResetToken.user.backend = 'django.contrib.auth.backends.ModelBackend'
						login(request, passResetToken.user)
						passResetToken.delete()
						return redirect(reverse('core:home') + '#/profile')
		return redirect(reverse('user:login'))

@login_required
def activeAccountHandler(request, token):
		if request.method == 'GET':
				activateAccountToken = get_object_or_404(AccountActivationToken, token=token)
				if activateAccountToken:
						activateAccountToken.user.profile.active = True
						activateAccountToken.user.profile.save()
						activateAccountToken.delete()
		return redirect(reverse('core:home'))
