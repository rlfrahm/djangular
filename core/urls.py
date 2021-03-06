"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]

from django.conf import settings
if settings.DEBUG:
    urlpatterns.append(url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }))
    urlpatterns.append(url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }))

urlpatterns.append(url(r'^api/v1/', include('api.urls', namespace='api')))
urlpatterns.append(url(r'^about$', views.aboutHandler, name='about'))
urlpatterns.append(url(r'^$', views.homeHandler, name='home'))
urlpatterns.append(url(r'^', include('account.urls', namespace='user')))
urlpatterns.append(url(r'^', include('core.urls', namespace='core')))

    # url('^', include('django.contrib.auth.urls')),
