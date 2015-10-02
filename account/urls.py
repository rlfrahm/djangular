from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^login$', views.loginHandler, name='login'),
  url(r'^register/step-1$', views.step1Handler, name='register-step-1'),
  url(r'^register/step-2$', views.step2Handler, name='register-step-2'),
  url(r'^register$', views.registerHandler, name='register'),
  url(r'^activate/(?P<token>.+)$', views.activeAccountHandler, name='activate'),
  url(r'^logout$', views.logoutHandler, name='logout'),
  url(r'^reset_password/(?P<token>.+)$', views.resetPasswordHandler, name='reset-password'),
  url(r'^reset_password$', views.resetPasswordFormHandler, name='reset-password-form'),
  # url(r'^user/(?P<user_id>[0-9]+)$', views.userHandler, name='user'),
  # url(r'^user/$', views.profileHandler, name='profile'),
  url(r'^settings/financial/stripe/connect$', views.stripeConnectRedirectHandler, name='stripe-connect'),
]
