from django.shortcuts import render
from django.conf import settings

def aboutHandler(request):
	return render(request, 'about.html')

def homeHandler(request):
  if request.user.is_authenticated() is not True:
    return render(request, 'home-logged-out.html')
  else:
    return render(request, 'home.html')

def buyDrinksHandler(request):
  return render(request, 'buy_drinks.html')
