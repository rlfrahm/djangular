from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^buy-drinks', views.buyDrinksHandler, name='buy_drinks'),
  url(r'^', views.homeHandler, name='home'),
]