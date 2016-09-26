# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.core.wsgi import get_wsgi_application
from django.conf import settings

__author__ = 'Matthieu Gallet'

http_application = get_wsgi_application()
ws_application = None

if settings.USE_CELERY:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import gevent.socket
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import redis.connection
    from easydjango.websockets.uwsgi_runserver import uWSGIWebsocketServer
    redis.connection.socket = gevent.socket
    ws_application = uWSGIWebsocketServer()


def application(environ, start_response):
    """
    Return a WSGI application which is patched to be used with websockets.

    :return: a HTTP app, or a WS app (depending on the URL path)
    """
    if settings.USE_CELERY and environ.get('PATH_INFO', '').startswith(settings.WEBSOCKET_URL):
        return ws_application(environ, start_response)
    return http_application(environ, start_response)
