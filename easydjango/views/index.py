# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.contrib import messages
from django.views.generic import TemplateView

from easydjango.functions import TestForm
from easydjango.tasks import set_websocket_topics

__author__ = 'Matthieu Gallet'


class IndexView(TemplateView):
    template_name = 'easydjango/bootstrap3/index.html'

    def get(self, request, *args, **kwargs):
        messages.info(request, 'message (info)')
        messages.success(request, 'message (success)')
        messages.warning(request, 'message (warning)')
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
