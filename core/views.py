from django.shortcuts import render

def homeHandler(request):
  if request.user.is_authenticated() is not True:
    return render(request, 'home-logged-out.html')
  else:
    return render(request, 'home.html')

def buyDrinksHandler(request):
  return render(request, 'buy_drinks.html')