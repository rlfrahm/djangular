from django.contrib import admin

from .models import Bar, Bartender, BartenderInvite, Tab, TabInvite

# Register your models here.
admin.site.register(Bar)
admin.site.register(Bartender)
admin.site.register(BartenderInvite)
admin.site.register(Tab)
admin.site.register(TabInvite)