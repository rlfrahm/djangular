from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
  url(r'^user/bars$', views.UserBarsHandler.as_view(), name='user-bars'),
  url(r'^user', views.UserHandler.as_view(), name='user'),
  url(r'^auth', views.AuthHandler.as_view(), name='auth'),
  url(r'^bars', views.BarsHandler.as_view(), name='bars'),
]

urlpatterns = format_suffix_patterns(urlpatterns)