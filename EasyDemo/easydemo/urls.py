# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

# noinspection PyUnresolvedReferences
from easydemo.views import cache_60, cache_nevercache, cache_private, cache_vary_on_headers
from django.conf.urls import url

urlpatterns = [
    url(r'^demo/cache_60/', cache_60, name='cache_60'),
    url(r'^demo/cache_vary_on_headers/', cache_vary_on_headers, name='cache_vary_on_headers'),
    url(r'^demo/cache_private/', cache_private, name='cache_private'),
    url(r'^demo/cache_nevercache/', cache_nevercache, name='cache_nevercache'),
]
