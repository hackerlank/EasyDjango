# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging

# noinspection PyUnresolvedReferences
from easydemo.forms import TestForm
from django.contrib import messages
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers
from django.views.generic import TemplateView
from easydjango.tasks import set_websocket_topics

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
        template_values = {'form': form}
        return self.render_to_response(template_values)

    def post(self, request):
        set_websocket_topics(request)
        form = TestForm(request.POST)
        form.is_valid()
        template_values = {'form': form}
        return self.render_to_response(template_values)


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
