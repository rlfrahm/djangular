from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from .forms import LoginForm, RegisterForm, ProfileForm, StripeConnectRedirectForm, Step1Form, EmailForm
from .models import UserProfile, StripeCustomer, StripeMerchant, PasswordResetToken
from .emails import send_password_reset_email

import stripe, urllib, urllib2, json, uuid

stripe.api_key = settings.STRIPE_API_KEY

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
        if user.is_active:
          login(request, user)
          continue_url = request.GET.get('next')
          if continue_url:
            return HttpResponseRedirect(continue_url)
          return HttpResponseRedirect('/')
        else:
          # Account is disabled
          return HttpResponseRedirect('/login')
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
      firstname = form.cleaned_data['firstname']
      lastname = form.cleaned_data['lastname']
      username = form.cleaned_data['email'][:30]
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      dob = form.cleaned_data['dob']

      user = User.objects.create_user(username, email, password)
      user.first_name = firstname
      user.last_name = lastname
      user.save()

      group = Group.objects.get(name='Drinkers')
      user.groups.add(group)

      profile = UserProfile(user=user, dob=dob)
      profile.save()

      # Stripe
      cus = stripe.Customer.create(
        description=user.email,
        email=user.email
      )
      stripe_customer = StripeCustomer(user=user, customer_id=cus.get('id'))
      stripe_customer.save()

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
    print form.is_valid()
    print form.cleaned_data
    if form.is_valid():
      request.user.profile.picture = form.cleaned_data['avatar']
      request.user.profile.save()
      return HttpResponseRedirect('/register/step-2')
    else:
      form = Step1Form()
  return render(request, 'registration/step-1.html')

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

@login_required
def stripeConnectRedirectHandler(request):
  form = StripeConnectRedirectForm(request.GET)
  if form.is_valid():
    data = {
      'client_secret': settings.STRIPE_API_KEY,
      'code': request.GET['code'],
      'grant_type': 'authorization_code',
    }
    data = urllib.urlencode(data)
    url = 'https://connect.stripe.com/oauth/token'
    res = urllib2.urlopen(url, data)
    # TODO: Error checking
    data = json.loads(res.read())
    merchant = StripeMerchant()
    merchant.user = request.user
    merchant.account_id = data.get('stripe_user_id')
    merchant.pub_key = data.get('stripe_publishable_key')
    merchant.refresh_token = data.get('refresh_token')
    merchant.access_token = data.get('access_token')
    merchant.save()
    return redirect(reverse('core:home') + '#/bars/mine')
  else:
    # Something went wrong
    return redirect(reverse('core:home'))

def resetPasswordFormHandler(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            if user is None:
                # No user, fail
                ValidationError(_('No user has this email.'), code='invalid')
            passResetToken = PasswordResetToken.objects.filter(user=user)
            if len(passResetToken) < 1:
                passResetToken = PasswordResetToken(user=user, token=uuid.uuid4())
                print passResetToken.token
                send_password_reset_email(request, passResetToken)
                passResetToken.save()
            else:
                ValidationError(_('A password reset email has already been sent.'), code='invalid')
    else:
        form = EmailForm()
    return render(request, 'registration/reset_password.html', {'form': form})

def resetPasswordHandler(request, token):
    if request.method = 'GET':
        passResetToken = get_object_or_404(PasswordResetToken, token=token)
    return redirect(reverse('user:login'))
