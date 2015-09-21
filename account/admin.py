from django.contrib import admin

from .models import UserProfile, StripeCustomer

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(StripeCustomer)