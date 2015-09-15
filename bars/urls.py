from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^bars/register$', views.registerBarHandler, name='register-bar'),
  url(r'^bars/(?P<bar_id>[0-9]+)$', views.barDetailHandler, name='bar-detail'),
]