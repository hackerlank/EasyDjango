# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf.urls import url

from easydjango.views.examples import cache_vary_on_headers, cache_private, cache_nevercache, cache_60

__author__ = 'Matthieu Gallet'

urlpatterns = [
       url(r'^demo/cache_60/', cache_60, name='cache_60'),
       url(r'^demo/cache_vary_on_headers/', cache_vary_on_headers, name='cache_vary_on_headers'),
       url(r'^demo/cache_private/', cache_private, name='cache_private'),
       url(r'^demo/cache_nevercache/', cache_nevercache, name='cache_nevercache'),
]

#
# public=True
# private=True
# no_cache=True
# no_transform=True
# must_revalidate=True
# proxy_revalidate=True
# max_age=num_seconds
# s_maxage=num_seconds
