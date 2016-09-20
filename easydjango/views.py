# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

__author__ = 'Matthieu Gallet'


# noinspection PyUnusedLocal
def favicon(request):
    return HttpResponsePermanentRedirect('%sfavicon/favicon.ico' % settings.STATIC_URL)


def robots(request):
    current_site = get_current_site(request)
    base_url = add_domain(current_site.domain, '/', request.is_secure())[:-1]
    template_values = {'base_url': base_url}
    return render_to_response('easydjango/robots.txt', template_values, RequestContext(request),
                              content_type='text/plain')


def index(request):
    # messages.info(request, 'message (info)')
    # messages.success(request, 'message (success)')
    # messages.warning(request, 'message (warning)')
    # messages.error(request, 'message (error)')
    template_values = {}
    return render_to_response('easydjango/%s/index.html' % settings.EASYDJANGO_TEMPLATE_BASE,
                              template_values, RequestContext(request))
