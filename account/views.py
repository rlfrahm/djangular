from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import LoginForm, RegisterForm, ProfileForm
from .models import UserProfile

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

      profile = UserProfile(user=user, dob=dob)

      user = authenticate(username=username, password=password)
      login(request, user)
      continue_url = request.GET.get('next')
      if continue_url:
        return HttpResponseRedirect(continue_url)
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

def userHandler(request, user_id):
  user = get_object_or_404(User, pk=user_id)
  return render(request, 'user/user.html', {'user': user})