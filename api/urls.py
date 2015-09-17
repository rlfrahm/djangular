from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
  url(r'^user/bars$', views.UserBarsHandler.as_view(), name='user-bars'),
  url(r'^user$', views.UserHandler.as_view(), name='user'),
  url(r'^auth$', views.AuthHandler.as_view(), name='auth'),
  # url(r'^bars/(?P<bar_id>[0-9]+)/bartenders/invite/(?P<invite_id>.+)$', views.BartenderInviteHandler.as_view(), name='bartender-invite'),
  url(r'^bars/(?P<bar_id>[0-9]+)/bartenders/(?P<bartender_id>[0-9]+)$', views.BartenderHandler.as_view(), name='bartender'),
  url(r'^bars/(?P<bar_id>[0-9]+)/bartenders$', views.BartendersHandler.as_view(), name='bartenders'),
  url(r'^bars/(?P<bar_id>[0-9]+)/checkin$', views.BarCheckinHandler.as_view(), name='bar'),
  url(r'^bars/(?P<bar_id>[0-9]+)$', views.BarHandler.as_view(), name='bar'),
  url(r'^bars$', views.BarsHandler.as_view(), name='bars'),
]

urlpatterns = format_suffix_patterns(urlpatterns)