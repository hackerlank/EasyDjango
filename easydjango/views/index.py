# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging

from django.conf import settings
from django.contrib import messages
from django.views.generic import TemplateView

from easydjango.functions import TestForm
from easydjango.tasks import set_websocket_topics

logger = logging.getLogger('django.request')
__author__ = 'Matthieu Gallet'


class IndexView(TemplateView):
    template_name = 'easydjango/bootstrap3/index.html'

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
