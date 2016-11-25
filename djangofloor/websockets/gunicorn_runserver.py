# -*- coding: utf-8 -*-
"""
WSGI config for djangofloor project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
from __future__ import unicode_literals, print_function, absolute_import

import logging
import select

from django.utils import six
from djangofloor.websockets.wsgi_server import WebsocketWSGIServer

__author__ = 'Matthieu Gallet'

logger = logging.getLogger('djangofloor.websocket')

if six.PY3:
    # noinspection PyShadowingBuiltins
    xrange = range


class GunicornWebsocketServer(WebsocketWSGIServer):
    WS_GUID = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    WS_VERSIONS = (b'13', b'8', b'7')

    def get_ws_file_descriptor(self, websocket):
        return websocket.stream.handler.socket.fileno()

    def flush_websocket(self, websocket):
        pass

    def upgrade_websocket(self, environ, start_response):
        return environ['wsgi.websocket']

    def select(self, rlist, wlist, xlist, timeout=None):
        # return gevent.select.select(rlist, wlist, xlist, timeout)
        return select.select(rlist, wlist, xlist, timeout)

    def verify_client(self, ws):
        pass

    def ws_send_bytes(self, websocket, message):
        return websocket.send(message)

    def ws_receive_bytes(self, websocket):
        return websocket.receive()
