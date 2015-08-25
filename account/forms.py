from django import forms

import datetime

class LoginForm(forms.Form):
  username = forms.CharField(label='Username', max_length=100)
  # email = forms.EmailField(label='Email')
  password = forms.CharField(label='Password', widget=forms.PasswordInput)

class RegisterForm(forms.Form):
  username = forms.CharField(label='Username', max_length=100)
  email = forms.EmailField(label='Email')
  password = forms.CharField(label='Password', widget=forms.PasswordInput)
  dob = forms.DateField(initial=datetime.date.today)

class ProfileForm(forms.Form):
  username = forms.CharField(label='Username', max_length=100)
  dob = forms.DateField(initial=datetime.date.today)

class PasswordForm(forms.Form):
  password = forms.CharField(label='Password', widget=forms.PasswordInput)

class EmailForm(forms.Form):
  email = forms.EmailField(label='Email')
