
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page, cache_control, never_cache
from django.views.decorators.vary import vary_on_headers

from easydjango.functions import TestForm

__author__ = 'Matthieu Gallet'


@cache_page(60)
def cache_60(request):
    print("compute cache_60 page")
    return TemplateResponse(request, 'easydjango/bootstrap3/index.html', {'form': TestForm(), })


@vary_on_headers('User-Agent')
def cache_vary_on_headers(request):
    print("compute cache_vary_on_headers page")
    return TemplateResponse(request, 'easydjango/bootstrap3/index.html', {'form': TestForm(), })


@cache_control(private=True)
def cache_private(request):
    print("compute cache_private page")
    return TemplateResponse(request, 'easydjango/bootstrap3/index.html', {'form': TestForm(), })


@never_cache
def cache_nevercache(request):
    print("compute never_cache page")
    return TemplateResponse(request, 'easydjango/bootstrap3/index.html', {'form': TestForm(), })

#
# public=True
# private=True
# no_cache=True
# no_transform=True
# must_revalidate=True
# proxy_revalidate=True
# max_age=num_seconds
# s_maxage=num_seconds
