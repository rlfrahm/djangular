from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import LoginForm, RegisterForm, ProfileForm

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
          return HttpResponseRedirect('/')
        else:
          # Account is disabled
          return HttpResponseRedirect('/login')
      else:
        # invalid login
        return HttpResponseRedirect('/login')
  else:
    if request.user.is_authenticated():
      return HttpResponseRedirect('/')
    else:
      form = LoginForm()

  return render(request, 'registration/login.html', {'form': form})

def registerHandler(request):
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
      user = authenticate(username=username, password=password)
      login(request, user)
      return HttpResponseRedirect('/')
  else:
    if request.user.is_authenticated():
      return HttpResponseRedirect('/')
    else:
      form = RegisterForm()

  return render(request, 'registration/register.html', {'form': form})

def logoutHandler(request):
  logout(request)
  return HttpResponseRedirect('/')

def profileHandler(request):
  form = ProfileForm()
  return render(request, 'user/user_settings_profile.html', {'form': form})