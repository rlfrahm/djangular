from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from .forms import RegisterForm
from .models import Bar, Bartender, BartenderInvite
from .emails import send_bartender_invite

# Create your views here.
@login_required
def registerBarHandler(request):
  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():
      name = form.cleaned_data['name']
      street = form.cleaned_data['street']
      city = form.cleaned_data['city']
      province = form.cleaned_data['province']

      # Create bar
      bar = Bar(name=name, owner=request.user, street=street, city=city, province=province)
      # bar.slug = slugify(bar.name)
      bar.save()

      # Redirect to new bar
      return HttpResponseRedirect(reverse('bars:bar-detail', args=(bar.pk,)))
  else:
    form = RegisterForm()
  return render(request, 'bars/new_bar.html', {'form': form})

@login_required
def barDetailHandler(request, bar_id):
  bar = get_object_or_404(Bar, pk=bar_id)
  return render(request, 'bars/bar_detail.html', {'bar': bar})

@login_required
def barDetailHandler(request, bar_id, invite_id):
  bar = get_object_or_404(Bar, pk=bar_id)
  return render(request, 'bars/bar_detail.html', {'bar': bar})

@login_required
def bartenderInviteHandler(request, bar_id, invite_id):
  invite = get_object_or_404(BartenderInvite, token=invite_id)
  if request.user.email == invite.email:
    bartender = Bartender()
    bartender.user = request.user
    bartender.bar = get_object_or_404(Bar, pk=bar_id)
    bartender.save()
    invite.delete()
    return redirect(reverse('core:home') + '#/bars/%s' % bar_id)