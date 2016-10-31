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

import base64
import logging
import socket
import select

import django
import re
from hashlib import md5, sha1

import errno

import six
from django.utils.encoding import force_str
from easydjango.websockets.exceptions import HandshakeError, UpgradeRequiredError
from easydjango.websockets.websocket import WebSocket
from easydjango.websockets.wsgi_server import WebsocketWSGIServer
from gunicorn.workers.async import ALREADY_HANDLED

__author__ = 'Matthieu Gallet'

logger = logging.getLogger('django.request')


class WebsocketRunServer(WebsocketWSGIServer):
    WS_GUID = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    WS_VERSIONS = ('13', '8', '7')

    def upgrade_websocket(self, environ, start_response):
        """
        Attempt to upgrade the socket environ['wsgi.input'] into a websocket enabled connection.
        """
        websocket_version = environ.get('HTTP_SEC_WEBSOCKET_VERSION', '')
        if not websocket_version:
            raise UpgradeRequiredError
        elif websocket_version not in self.WS_VERSIONS:
            raise HandshakeError('Unsupported WebSocket Version: {0}'.format(websocket_version))

        key = environ.get('HTTP_SEC_WEBSOCKET_KEY', '').strip()
        if not key:
            raise HandshakeError('Sec-WebSocket-Key header is missing/empty')
        try:
            key_len = len(base64.b64decode(key))
        except TypeError:
            raise HandshakeError('Invalid key: {0}'.format(key))
        if key_len != 16:
            # 5.2.1 (3)
            raise HandshakeError('Invalid key: {0}'.format(key))

        sec_ws_accept = base64.b64encode(sha1(six.b(key) + self.WS_GUID).digest())
        if six.PY3:
            sec_ws_accept = sec_ws_accept.decode('ascii')
        headers = [
            ('Upgrade', 'websocket'),
            ('Connection', 'Upgrade'),
            ('Sec-WebSocket-Accept', sec_ws_accept),
            ('Sec-WebSocket-Version', str(websocket_version)),
        ]
        logger.debug('WebSocket request accepted, switching protocols')
        start_response(force_str('101 Switching Protocols'), headers)
        print(environ)
        # six.get_method_self(start_response).finish_content()
        return WebSocket(environ['wsgi.input'])

    def select(self, rlist, wlist, xlist, timeout=None):
        return select.select(rlist, wlist, xlist, timeout)
