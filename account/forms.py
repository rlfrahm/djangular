from django import forms

from .models import UserProfile

import datetime

class LoginForm(forms.Form):
  username = forms.CharField(label='Username', max_length=100)
  # email = forms.EmailField(label='Email')
  password = forms.CharField(label='Password', widget=forms.PasswordInput)

class RegisterForm(forms.Form):
  # username = forms.CharField(label='Username', max_length=100)
  firstname = forms.CharField(label="First Name", max_length=100)
  lastname = forms.CharField(label="Last Name", max_length=100)
  email = forms.EmailField(label='Email')
  username = forms.CharField(label='Username', max_length=255)
  password = forms.CharField(label='Password', widget=forms.PasswordInput)

class ProfileForm(forms.Form):
  username = forms.CharField(label='Username', max_length=100)

class PasswordForm(forms.Form):
  password = forms.CharField(label='Password', widget=forms.PasswordInput)

class EmailForm(forms.Form):
  email = forms.EmailField(label='Email')

class Step1Form(forms.Form):
  avatar = forms.ImageField(label='Avatar')

class Step2Form(forms.Form):
    token = forms.CharField(max_length=100)
