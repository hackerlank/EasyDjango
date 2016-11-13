# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from djangofloor.models import Notification

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
    # noinspection PyTypeChecker
    return {
        'df_has_index_view': bool(settings.EASYDJANGO_INDEX_VIEW),
        'df_has_login_view': bool(settings.EASYDJANGO_LOGIN_VIEW),
        'df_has_site_search_view': bool(settings.EASYDJANGO_SITE_SEARCH_VIEW),
        'df_project_name': settings.PROJECT_NAME,
        'df_remote_username': getattr(request, 'remote_username', None),
        'df_remote_authenticated': bool(getattr(request, 'remote_username', None)),
        'df_user': getattr(request, 'user', None),
        'df_get_notifications': lambda: Notification.get_notifications(request),
        'df_user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'df_window_key': getattr(request, 'window_key', None),
        'df_has_ws_topics': getattr(request, 'has_websocket_topics', False),

        'df_index_view': 'index',  # TODO remove this line
        'df_language_code': settings.LANGUAGE_CODE,  # TODO remove this line
    }
