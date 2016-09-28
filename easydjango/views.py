# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.http import HttpResponsePermanentRedirect
from django.template.response import TemplateResponse
from django.utils.lru_cache import lru_cache

from easydjango.signals.connection import REGISTERED_SIGNALS
from easydjango.signals.request import SignalRequest
from easydjango.tasks import WINDOW, set_websocket_topics, BROADCAST

__author__ = 'Matthieu Gallet'


# noinspection PyUnusedLocal
def favicon(request):
    return HttpResponsePermanentRedirect('%sfavicon/favicon.ico' % settings.STATIC_URL)


def robots(request):
    current_site = get_current_site(request)
    base_url = add_domain(current_site.domain, '/', request.is_secure())[:-1]
    template_values = {'base_url': base_url}
    return TemplateResponse('easydjango/robots.txt', template_values, content_type='text/plain')


@lru_cache()
def __get_js_mimetype():
    if hasattr(settings, 'PIPELINE_MIMETYPES'):
        for (mimetype, ext) in settings.PIPELINE_MIMETYPES:
            if ext == '.js':
                return mimetype
    return 'text/javascript'


def signals(request):
    signal_request = SignalRequest.from_request(request)
    valid_signal_names = []
    for signal_name, list_of_connections in REGISTERED_SIGNALS.items():
        if any(x.is_allowed_to(signal_request) for x in list_of_connections):
            valid_signal_names.append(signal_name)
    csrf_header_name = getattr(settings, 'CSRF_HEADER_NAME', 'HTTP_X_CSRFTOKEN')
    return TemplateResponse(request, 'easydjango/signals.html',
                            {'signals': valid_signal_names,
                             'WS4REDIS_HEARTBEAT': settings.WS4REDIS_HEARTBEAT,
                             'WEBSOCKET_URL': 'ws://localhost:9000' + settings.WEBSOCKET_URL,
                             'CSRF_COOKIE_NAME': settings.CSRF_COOKIE_NAME,
                             'CSRF_HEADER_NAME': csrf_header_name[5:].replace('_', '-')},
                            content_type=__get_js_mimetype())


def index(request):
    # messages.info(request, 'message (info)')
    # messages.success(request, 'message (success)')
    # messages.warning(request, 'message (warning)')
    # messages.error(request, 'message (error)')
    set_websocket_topics(request, WINDOW, BROADCAST)
    template_values = {}
    return TemplateResponse(request, 'easydjango/%s/index.html' % settings.EASYDJANGO_TEMPLATE_BASE, template_values)
