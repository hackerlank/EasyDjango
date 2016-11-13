# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging

# noinspection PyUnresolvedReferences
from easydemo.forms import TestForm, ChatLoginForm
from django.contrib import messages
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers
from django.views.generic import TemplateView
from djangofloor.tasks import set_websocket_topics, WINDOW

logger = logging.getLogger('django.request')
__author__ = 'Matthieu Gallet'


class IndexView(TemplateView):
    template_name = 'easydemo/index.html'

    def get(self, request, *args, **kwargs):
        logger.debug('debug log message')
        logger.info('info log message')
        logger.warn('warn log message')
        logger.error('error log message')
        messages.error(request, 'message (error)')
        set_websocket_topics(request)
        form = TestForm()
        template_values = {'form': form, 'title': 'Hello, world!'}
        return self.render_to_response(template_values)

    def post(self, request):
        set_websocket_topics(request)
        form = TestForm(request.POST)
        form.is_valid()
        template_values = {'form': form, 'title': 'Hello, world!'}
        return self.render_to_response(template_values)


@cache_page(60)
def cache_60(request):
    logger.warn("compute cache_60 page")
    return TemplateResponse(request, 'easydemo/index.html', {'form': TestForm(), 'title': 'Cached during 60s'})


@cache_page(60)
@vary_on_headers('User-Agent')
def cache_vary_on_headers(request):
    logger.warn("compute cache_vary_on_headers page (User-Agent=%s)" % request.META.get('HTTP_USER_AGENT'))
    return TemplateResponse(request, 'easydemo/index.html', {'form': TestForm(), 'title': 'Cache by User-Agent'})


@cache_control(private=True)
def cache_private(request):
    logger.warn("compute cache_private page")
    return TemplateResponse(request, 'easydemo/index.html', {'form': TestForm(), 'title': 'Cached for public'})


@never_cache
def cache_nevercache(request):
    logger.warn("compute never_cache page")
    return TemplateResponse(request, 'easydemo/index.html', {'form': TestForm(), 'title': 'Never cache'})


def chat(request):
    name = None
    if request.method == 'POST':
        form = ChatLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            form = None
            set_websocket_topics(request, WINDOW, 'chat-%s' % name)
    else:
        form = ChatLoginForm()
        set_websocket_topics(request, WINDOW)

    template_values = {'form': form, 'name': name}
    return TemplateResponse(request, 'easydemo/chat.html', template_values)
