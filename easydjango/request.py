# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.template.loader import render_to_string as raw_render_to_string
from django.utils.module_loading import import_string

__author__ = 'Matthieu Gallet'

middlewares = [import_string(x)() for x in settings.SIGNAL_REQUEST_MIDDLEWARES]


class SignalRequest(object):
    """ Built to store the username and the window key and must be supplied to any Python signal call.
    All attributes are set by "SignalRequestMiddleware"'s.

    Can be constructed from a standard :class:`django.http.HttpRequest` or from a dict.
    """

    def __init__(self, init=True):
        if init:
            for mdw in middlewares:
                mdw.new_request(self)

    @classmethod
    def from_dict(cls, values):
        signal_request = cls(init=False)
        for mdw in middlewares:
            mdw.from_dict(signal_request, values=values)
        return signal_request

    def to_dict(self):
        """Convert this :class:`djangofloor.decorators.SignalRequest` to a :class:`dict` which can be provided to JSON.

        :return: a dict ready to be serialized in JSON
        :rtype: :class:`dict`
        """
        result = {}
        for mdw in middlewares:
            extra_values = mdw.to_dict(self)
            if extra_values:
                result.update(extra_values)
        return result

    @classmethod
    def from_request(cls, request):
        """ return a :class:`djangofloor.decorators.SignalRequest` from a :class:`django.http.HttpRequest`.

        If the request already is a :class:`djangofloor.decorators.SignalRequest`,
        then it is returned as-is (not copied!).

        :param request: standard Django request
        :type request: :class:`django.http.HttpRequest` or :class:`djangofloor.decorators.SignalRequest`
        :return: a valid request
        :rtype: :class:`djangofloor.decorators.SignalRequest`
        """
        if isinstance(request, SignalRequest):
            return request
        signal_request = cls(init=False)
        for mdw in middlewares:
            mdw.from_request(request, signal_request)
        return signal_request


for mdw_ in middlewares:
    mdw_.install_methods(SignalRequest)


def get_signal_context(request):
    context = {}
    for mdw in middlewares:
        context.update(mdw.get_context(request))
    return context


def render_to_string(template_name, context=None, request=None, using=None):
    if request is not None:
        request_context = get_signal_context(request)
        request_context.update(context)
    else:
        request_context = context
    return raw_render_to_string(template_name, context=request_context, using=using)
