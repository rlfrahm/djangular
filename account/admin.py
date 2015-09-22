from django.contrib import admin

from .models import UserProfile, StripeCustomer, StripeMerchant

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(StripeCustomer)
admin.site.register(StripeMerchant)