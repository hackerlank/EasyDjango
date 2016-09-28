# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.i18n import javascript_catalog
from django.views.static import serve
from django.utils.module_loading import import_string

from easydjango.scripts import load_celery
from easydjango.views import favicon, robots, signals

__author__ = 'Matthieu Gallet'

load_celery()
admin.autodiscover()

if settings.EASYDJANGO_URL_CONF:
    extra_urls = import_string(settings.EASYDJANGO_URL_CONF)
else:
    extra_urls = []

if settings.EASYDJANGO_INDEX:
    index_view = settings.EASYDJANGO_INDEX
else:
    index_view = 'easydjango.views.index'
index_view = import_string(index_view)

urlpatterns = [url(r'^admin/', include(admin.site.urls)),
               url(r'^jsi18n/$', javascript_catalog, {'packages': ('easydjango', 'django.contrib.admin'), }),
               url(r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
               url(r'^' + settings.STATIC_URL[1:] + '(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
               # url(r'^df/signal/(?P<signal>[\w\.\-_]+)\.json$', signal_call, name='df_signal_call'),
               # url(r'^df/ws_emulation.js$', get_signal_calls, name='df_get_signal_calls'),
               url(r'^ed/signals.js$', signals, name='signals'),
               url(r'^robots\.txt$', robots),
               url(r'^favicon\.ico$', favicon),
               url(r'^$', index_view, name='index'),
               ] + list(extra_urls)

if settings.DEBUG and settings.USE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
