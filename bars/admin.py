from django.contrib import admin
from django.shortcuts import render
from django.conf.urls import patterns

from .models import Bar, Bartender, RoleInvite, Tab, TabInvite

# Register your models here.
admin.site.register(Bar)
admin.site.register(Bartender)
admin.site.register(RoleInvite)
admin.site.register(Tab)
admin.site.register(TabInvite)

# class BarOnboardingAdmin(admin.ModelAdmin):
#
#     def view(self, request):
#         return barOnboardingHandler(request)
#
#     def get_urls(self):
#         urls = super(BarOnboardingAdmin, self).get_urls()
#         my_urls = patterns('', (r'^new-bar/$', self.view()))
#         return my_urls + urls
#
# def barOnboardingHandler(request):
#     return render(request, 'admin/newbar.html')
#
# admin.site.register('', BarOnboardingAdmin)
