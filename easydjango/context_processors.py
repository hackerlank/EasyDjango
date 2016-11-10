# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from easydjango.models import Notification

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
        'ed_has_index_view': bool(settings.EASYDJANGO_INDEX_VIEW),
        'ed_has_login_view': bool(settings.EASYDJANGO_LOGIN_VIEW),
        'ed_has_site_search_view': bool(settings.EASYDJANGO_SITE_SEARCH_VIEW),
        'ed_project_name': settings.PROJECT_NAME,
        'ed_remote_username': getattr(request, 'remote_username'),
        'ed_user': getattr(request, 'user', None),
        'ed_get_notifications': lambda: Notification.get_notifications(request),
        'ed_user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'ed_ws_token': getattr(request, 'window_key', None),
        'ed_has_ws_topics': getattr(request, 'has_websocket_topics', False),
    }
