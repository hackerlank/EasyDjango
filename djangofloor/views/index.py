# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.views.generic import TemplateView

__author__ = 'Matthieu Gallet'


class IndexView(TemplateView):
    template_name = 'djangofloor/bootstrap3/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context(request)
        return self.render_to_response(context)

    def get_context(self, request):
        return {}
