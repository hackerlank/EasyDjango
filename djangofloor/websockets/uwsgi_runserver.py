# -*- coding: utf-8 -*-
import logging

import uwsgi
import gevent.select
from djangofloor.websockets.exceptions import WebSocketError
from djangofloor.websockets.wsgi_server import WebsocketWSGIServer

logger = logging.getLogger('django.request')


class uWSGIWebsocket(object):
    def __init__(self):
        self._closed = False

    def get_file_descriptor(self):
        """Return the file descriptor for the given websocket"""
        try:
            return uwsgi.connection_fd()
        except IOError as e:
            self.close()
            raise WebSocketError(e)

    @property
    def closed(self):
        return self._closed

    def receive(self):
        if self._closed:
            raise WebSocketError("Connection is already closed")
        try:
            return uwsgi.websocket_recv_nb().decode('utf-8')
        except IOError as e:
            self.close()
            raise WebSocketError(e)

    def flush(self):
        try:
            uwsgi.websocket_recv_nb()
        except IOError:
            self.close()

    def send(self, message, binary=None):
        try:
            uwsgi.websocket_send(message)
        except IOError as e:
            self.close()
            raise WebSocketError(e)

    def close(self, code=1000, message=''):
        self._closed = True


class uWSGIWebsocketServer(WebsocketWSGIServer):
    def upgrade_websocket(self, environ, start_response):
        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
        return uWSGIWebsocket()

    def get_ws_file_descriptor(self, websocket):
        return websocket.get_file_descriptor()

    def select(self, rlist, wlist, xlist, timeout=None):
        return gevent.select.select(rlist, wlist, xlist, timeout)

    def flush_websocket(self, websocket):
        return websocket.flush()
