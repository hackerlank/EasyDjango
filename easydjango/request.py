# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.template.loader import render_to_string as raw_render_to_string
from django.utils.module_loading import import_string

__author__ = 'Matthieu Gallet'

middlewares = [import_string(x)() for x in settings.WINDOW_INFO_MIDDLEWARES]


class WindowInfo(object):
    """ Built to store the username and the window key and must be supplied to any Python signal call.
    All attributes are set by "WindowInfoMiddleware"'s.

    Can be constructed from a standard :class:`django.http.HttpRequest` or from a dict.
    """

    def __init__(self, init=True):
        if init:
            for mdw in middlewares:
                mdw.new_window_info(self)

    @classmethod
    def from_dict(cls, values):
        window_info = cls(init=False)
        for mdw in middlewares:
            mdw.from_dict(window_info, values=values)
        return window_info

    def to_dict(self):
        """Convert this :class:`djangofloor.decorators.WindowInfo` to a :class:`dict` which can be provided to JSON.

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
        """ return a :class:`djangofloor.decorators.WindowInfo` from a :class:`django.http.HttpRequest`.

        If the request already is a :class:`djangofloor.decorators.WindowInfo`,
        then it is returned as-is (not copied!).

        :param request: standard Django request
        :type request: :class:`django.http.HttpRequest` or :class:`djangofloor.decorators.SignalRequest`
        :return: a valid request
        :rtype: :class:`djangofloor.decorators.SignalRequest`
        """
        if isinstance(request, WindowInfo):
            return request
        window_info = cls(init=False)
        for mdw in middlewares:
            mdw.from_request(request, window_info)
        return window_info


for mdw_ in middlewares:
    mdw_.install_methods(WindowInfo)


def get_window_context(window_info):
    context = {}
    for mdw in middlewares:
        context.update(mdw.get_context(window_info))
    return context


def render_to_string(template_name, context=None, window_info=None, using=None):
    if window_info is not None:
        window_context = get_window_context(window_info)
        window_context.update(context)
    else:
        window_context = context
    return raw_render_to_string(template_name, context=window_context, using=using)
