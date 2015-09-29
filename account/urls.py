from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^login$', views.loginHandler, name='login'),
  url(r'^register/step-1$', views.step1Handler, name='register-step-1'),
  url(r'^register$', views.registerHandler, name='register'),
  url(r'^logout$', views.logoutHandler, name='logout'),
  # url(r'^user/(?P<user_id>[0-9]+)$', views.userHandler, name='user'),
  # url(r'^user/$', views.profileHandler, name='profile'),
  url(r'^settings/financial/stripe/connect$', views.stripeConnectRedirectHandler, name='stripe-connect'),
]