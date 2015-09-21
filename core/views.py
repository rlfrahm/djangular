from django.shortcuts import render
from django.conf import settings

def homeHandler(request):
  if request.user.is_authenticated() is not True:
    return render(request, 'home-logged-out.html')
  else:
    return render(request, 'home.html', {'stripe_pk': settings.STRIPE_PUB_API_KEY})

def buyDrinksHandler(request):
  return render(request, 'buy_drinks.html')