# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings

__author__ = 'Matthieu Gallet'


def context_base(request):
    """Provide the following variables to templates when you RequestContext:

        * 'df_remote_authenticated': `True` if the user has been authenticated by
          `djangofloor.middleware.RemoteUserMiddleware`.
        * 'df_project_name': name of your project, as defined in settings.FLOOR_PROJECT_NAME,
        * 'df_user': the user (:class:`django.contrib.auth.models.AbstractUser`),
        * 'df_language_code': settings.LANGUAGE_CODE (:class:`str`),
        * 'df_user_agent': the User Agent or '' if not defined in the request (:class:`str`),
        * 'df_index_view': the default view name (:class:`str`)
        * 'df_window_key': a random value, unique to the window and allowing to identify
          successive JS calls (:class:`str`)

    :param request: a HTTP request
    :type request: :class:`django.http.HttpRequest`
    :return: a dict to update the global template context
    :rtype: :class:`dict`
    """
    # noinspection PyCallByClass,PyTypeChecker
    return {
        'ed_project_name': settings.PROJECT_NAME,
        'ed_user': request.user,
        'ed_language_code': settings.LANGUAGE_CODE,
        'ed_user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'ed_index_view': 'index',
        'ed_ws_token': request.window_key if hasattr(request, 'window_key') else None,
    }
