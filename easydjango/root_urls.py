# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.utils.module_loading import import_string
from django.views.i18n import javascript_catalog
from django.views.static import serve

from easydjango import urls
from easydjango.scripts import load_celery
from easydjango.views import favicon, robots

__author__ = 'Matthieu Gallet'

load_celery()
admin.autodiscover()

if settings.EASYDJANGO_URL_CONF:
    extra_urls = import_string(settings.EASYDJANGO_URL_CONF)
else:
    extra_urls = []

urlpatterns = [url(r'^admin/', include(admin.site.urls)),
               url(r'^jsi18n/$', javascript_catalog, {'packages': ('easydjango', 'django.contrib.admin'), }),
               url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], serve, {'document_root': settings.MEDIA_ROOT}),
               url(r'^%s(?P<path>.*)$' % settings.STATIC_URL[1:], serve, {'document_root': settings.STATIC_ROOT}),
               url(r'^ed/', include(urls, namespace='ed')),
               url(r'^robots\.txt$', robots),
               url(r'^favicon\.ico$', favicon, name='favicon'),
               ] + list(extra_urls)
if settings.EASYDJANGO_LOGIN_VIEW:
    login_view = import_string(settings.EASYDJANGO_LOGIN_VIEW)
    urlpatterns += [url(r'^%s' % settings.LOGIN_URL[1:], login_view.as_view(), name='login')]
if settings.USE_REST_FRAMEWORK:
    urlpatterns += [
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]
if settings.EASYDJANGO_INDEX_VIEW:
    index_view = import_string(settings.EASYDJANGO_INDEX_VIEW)
    urlpatterns += [url(r'^$', index_view.as_view(), name='index')]
if settings.DEBUG and settings.USE_DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)), ]
