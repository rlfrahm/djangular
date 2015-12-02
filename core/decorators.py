from django.core.urlresolvers import reverse
from django.shortcuts import redirect

def anonymous_required(function=None):
    """
    Check that the user is NOT logged in
    """
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect(reverse('core:home'))
            else:
                return view_func(request, *args, **kwargs)

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)
