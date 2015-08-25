from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^login', views.loginHandler, name='login'),
  url(r'^register', views.registerHandler, name='register'),
  url(r'^logout', views.logoutHandler, name='logout'),
  url(r'^user', views.profileHandler, name='profile'),
]