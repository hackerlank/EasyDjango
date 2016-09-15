# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

__author__ = 'Matthieu Gallet'


# noinspection PyUnusedLocal
def favicon(request):
    return HttpResponsePermanentRedirect('%sfavicon/favicon.ico' % settings.STATIC_URL)


def index(request):
    template_values = {}
    return render_to_response('easydjango/%s/index.html' % settings.EASYDJANGO_TEMPLATE_BASE,
                              template_values, RequestContext(request))
