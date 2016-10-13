# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.conf.urls import url
from django.utils.module_loading import import_string

from easydjango.views import auth, signals
from easydjango.views.examples import cache_vary_on_headers, cache_private, cache_nevercache, cache_60

__author__ = 'Matthieu Gallet'


urlpatterns = [
    url(r'^signals.js$', signals, name='signals'),
    url(r'^logout/', auth.logout, name='logout'),
    url(r'^password_reset/', auth.password_reset, name='password_reset'),
    url(r'^set_password/', auth.set_password, name='set_password'),

    url(r'^demo/cache_60/', cache_60, name='cache_60'),
    url(r'^demo/cache_vary_on_headers/', cache_vary_on_headers, name='cache_vary_on_headers'),
    url(r'^demo/cache_private/', cache_private, name='cache_private'),
    url(r'^demo/cache_nevercache/', cache_nevercache, name='cache_nevercache'),
]
if settings.EASYDJANGO_LOGIN_VIEW:
    login_view = import_string(settings.EASYDJANGO_LOGIN_VIEW)
    urlpatterns += [url(r'^login/', login_view.as_view(), name='login')]
if settings.EASYDJANGO_SITE_SEARCH_VIEW:
    search_view = import_string(settings.EASYDJANGO_SITE_SEARCH_VIEW)
    urlpatterns += [url(r'^search/', search_view.as_view(), name='site_search')]

#
# public=True
# private=True
# no_cache=True
# no_transform=True
# must_revalidate=True
# proxy_revalidate=True
# max_age=num_seconds
# s_maxage=num_seconds
