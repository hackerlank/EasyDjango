# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.conf.urls import url
from django.utils.module_loading import import_string

from djangofloor.views import auth, signals, monitoring

__author__ = 'Matthieu Gallet'


urlpatterns = [
    url(r'^signals.js$', signals, name='signals'),
    url(r'^logout/', auth.logout, name='logout'),
    url(r'^password_reset/', auth.password_reset, name='password_reset'),
    url(r'^set_password/', auth.set_password, name='set_password'),
]
if settings.DF_SYSTEM_CHECKS:
    urlpatterns += [url(r'^monitoring/system_state/', monitoring.system_state, name='system_state')]

if settings.DF_SITE_SEARCH_VIEW:
    search_view = import_string(settings.DF_SITE_SEARCH_VIEW)
    urlpatterns += [url(r'^search/', search_view.as_view(), name='site_search')]
