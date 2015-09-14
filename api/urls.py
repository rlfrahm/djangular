from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
  url(r'^register', csrf_exempt(views.RegisterHandler.as_view()), name='register'),
  url(r'^login', csrf_exempt(views.LoginHandler.as_view()), name='login'),
]

urlpatterns = format_suffix_patterns(urlpatterns)