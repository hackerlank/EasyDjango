# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.core.wsgi import get_wsgi_application

__author__ = 'Matthieu Gallet'

http_application = get_wsgi_application()
django_ws_application = None
gunicorn_ws_application = None
uwsgi_ws_application = None

if settings.USE_CELERY:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import gevent.socket
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import redis.connection
    from djangofloor.websockets.django_runserver import WebsocketRunServer
    from djangofloor.websockets.gunicorn_runserver import GunicornWebsocketServer
    try:
        from djangofloor.websockets.uwsgi_runserver import uWSGIWebsocketServer
        redis.connection.socket = gevent.socket
        uwsgi_ws_application = uWSGIWebsocketServer()
    except ImportError:
        uWSGIWebsocketServer = None
    django_ws_application = WebsocketRunServer()
    gunicorn_ws_application = GunicornWebsocketServer()


def application(environ, start_response):
    """
    Return a WSGI application which is patched to be used with websockets.

    :return: a HTTP app, or a WS app (depending on the URL path)
    """
    if environ.get('PATH_INFO', '').startswith(settings.WEBSOCKET_URL):
        return uwsgi_ws_application(environ, start_response)
    return http_application(environ, start_response)


def django_application(environ, start_response):
    """
    Return a WSGI application which is patched to be used with websockets.

    :return: a HTTP app, or a WS app (depending on the URL path)
    """
    if environ.get('PATH_INFO', '').startswith(settings.WEBSOCKET_URL):
        return django_ws_application(environ, start_response)
    return http_application(environ, start_response)


def gunicorn_application(environ, start_response):
    """
    Return a WSGI application which is patched to be used with websockets.

    :return: a HTTP app, or a WS app (depending on the URL path)
    """
    if environ.get('PATH_INFO', '').startswith(settings.WEBSOCKET_URL):
        return gunicorn_ws_application(environ, start_response)
    return http_application(environ, start_response)


def aiohttp_application(environ, start_response):
    """
    Return a WSGI application which is patched to be used with websockets.

    :return: a HTTP app, or a WS app (depending on the URL path)
    """
    if environ.get('PATH_INFO', '').startswith(settings.WEBSOCKET_URL):
        return gunicorn_ws_application(environ, start_response)
    return http_application(environ, start_response)
