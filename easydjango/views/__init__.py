# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.http import HttpResponsePermanentRedirect
from django.template.response import TemplateResponse
from django.utils.lru_cache import lru_cache

from easydjango.decorators import REGISTERED_SIGNALS, REGISTERED_FUNCTIONS
from easydjango.request import SignalRequest
from easydjango.tasks import import_signals_and_functions

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
    # noinspection PyTypeChecker
    if hasattr(settings, 'PIPELINE_MIMETYPES'):
        for (mimetype, ext) in settings.PIPELINE_MIMETYPES:
            if ext == '.js':
                return mimetype
    return 'text/javascript'


def signals(request):
    signal_request = SignalRequest.from_request(request)
    import_signals_and_functions()
    if settings.WS4REDIS_PUBLIC_WS_LIST:
        valid_signal_names = list(REGISTERED_SIGNALS.keys())
        valid_function_names = list(REGISTERED_FUNCTIONS.keys())
    else:
        valid_signal_names = []
        for signal_name, list_of_connections in REGISTERED_SIGNALS.items():
            if any(x.is_allowed_to(signal_request) for x in list_of_connections):
                valid_signal_names.append(signal_name)
        valid_function_names = []
        for function_name, connection in REGISTERED_FUNCTIONS.items():
            if connection.is_allowed_to(signal_request):
                valid_function_names.append(function_name)
    # noinspection PyTypeChecker
    csrf_header_name = getattr(settings, 'CSRF_HEADER_NAME', 'HTTP_X_CSRFTOKEN')
    return TemplateResponse(request, 'easydjango/signals.html',
                            {'SIGNALS': valid_signal_names,
                             'FUNCTIONS': valid_function_names,
                             'WS4REDIS_HEARTBEAT': settings.WS4REDIS_HEARTBEAT,
                             'WEBSOCKET_URL': 'ws://localhost:9000' + settings.WEBSOCKET_URL,
                             'CSRF_COOKIE_NAME': settings.CSRF_COOKIE_NAME,
                             'CSRF_HEADER_NAME': csrf_header_name[5:].replace('_', '-')},
                            content_type=__get_js_mimetype())


def system_check(request):
    pass
