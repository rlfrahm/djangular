from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
  # url(r'^user/sources/(?P<source_id>.+)$', views.SourceHandler.as_view(), name='credit-card'),
  # url(r'^user/sources$', views.SourcesHandler.as_view(), name='credit-cards'),
  url(r'^user/avatar$', views.UserAvatarHandler.as_view(), name='user-avatar'),
  url(r'^user/password$', views.UserPasswordHandler.as_view(), name='user-password'),
  url(r'^user$', views.UserHandler.as_view(), name='user'),
  url(r'^users/(?P<user_id>[0-9]+)$', views.UserProfileHandler.as_view(), name='user-profile'),
  url(r'^auth$', views.AuthHandler.as_view(), name='auth'),
  url(r'^search/users$', views.UserSearchHandler.as_view(), name='search-user'),
  url(r'^search$', views.SearchHandler.as_view(), name='search'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
