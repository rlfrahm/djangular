from django import forms

class RegisterForm(forms.Form):
  name = forms.CharField(label='Bar Name', max_length=255)
  street = forms.CharField(label='Street', max_length=255)
  city = forms.CharField(label='City', max_length=20)
  province = forms.CharField(label='State', max_length=100)
  # image = forms.ImageField()