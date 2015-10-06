from django import forms

class RegisterForm(forms.Form):
  name = forms.CharField(label='Bar Name', max_length=255)
  street = forms.CharField(label='Street', max_length=255)
  city = forms.CharField(label='City', max_length=20)
  province = forms.CharField(label='State', max_length=100)
  # image = forms.ImageField()

class ContactForm(forms.Form):
	bar_name = forms.CharField(label='Bar Name', max_length=255)
	name = forms.CharField(label='Your Name', max_length=255)
	email = forms.EmailField()
	phone = forms.CharField(label='Phone', max_length=10)
	license_number = forms.CharField(label='Liquor License Number', max_length=50)
	comments = forms.CharField(label='Comments', widget=forms.Textarea, required=False)
