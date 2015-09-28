from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from .forms import LoginForm, RegisterForm, ProfileForm, StripeConnectRedirectForm
from .models import UserProfile, StripeCustomer, StripeMerchant

import stripe, urllib, urllib2, json

stripe.api_key = settings.STRIPE_API_KEY

def loginHandler(request):
  form = None
  if request.user.is_authenticated():
    return HttpResponseRedirect('/')
  if request.method == 'POST':
    form = LoginForm(request.POST)
    if form.is_valid():
      username = request.POST['username']
      password = request.POST['password']
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
      username = request.POST['username']
      email = request.POST['email']
      password = request.POST['password']
      dob = request.POST['dob']

      user = User.objects.create_user(username, email, password)
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
      return HttpResponseRedirect('/#/profile')
  else:
    if request.user.is_authenticated():
      return HttpResponseRedirect('/')
    else:
      form = RegisterForm()

  return render(request, 'registration/register.html', {'form': form})

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