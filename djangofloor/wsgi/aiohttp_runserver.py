# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging

# noinspection PyPackageRequirements
import aiohttp
# noinspection PyPackageRequirements
import aiohttp.web
# noinspection PyPackageRequirements
import aiohttp.web_reqrep
from aiohttp_wsgi import WSGIHandler
import asyncio
# noinspection PyPackageRequirements
import asyncio_redis
from django.conf import settings
from django.contrib.auth import get_user
from django.core import signing
from django.core.wsgi import get_wsgi_application
from django.http import HttpRequest
from djangofloor.wsgi.window_info import WindowInfo
from djangofloor.utils import import_module
from djangofloor.wsgi.wsgi_server import signer, WebsocketWSGIServer

__author__ = 'Matthieu Gallet'
logger = logging.getLogger('django.request')


def get_window_info(aiohttp_request):
    django_request = get_http_request(aiohttp_request)
    session_key = django_request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    if session_key is not None:
        engine = import_module(settings.SESSION_ENGINE)
        django_request.session = engine.SessionStore(session_key)
        django_request.user = get_user(django_request)
    window_info = WindowInfo.from_request(django_request)
    signed_token = django_request.GET.get('token', '')
    try:
        window_info.window_key = signer.unsign(signed_token)
    except signing.BadSignature:
        pass
    return window_info


def get_http_request(aiohttp_request):
    assert isinstance(aiohttp_request, aiohttp.web_reqrep.Request)
    django_request = HttpRequest()
    django_request.GET = aiohttp_request.rel_url.query
    django_request.COOKIES = aiohttp_request.cookies
    django_request.session = None
    django_request.user = None
    return django_request


# noinspection PyCompatibility
class WebsocketEchoHandler(object):
    @asyncio.coroutine
    def __call__(self, request):
        ws = aiohttp.web.WebSocketResponse()
        # noinspection PyDeprecation
        ws.start(request)
        django_request = get_http_request(request)
        window_info = WebsocketWSGIServer.process_request(django_request)
        channels, echo_message = WebsocketWSGIServer.process_subscriptions(django_request)

        connection = yield from asyncio_redis.Connection.create(**settings.WS4REDIS_CONNECTION)
        subscriber = yield from connection.start_subscribe()
        yield from subscriber.subscribe(channels)
        # noinspection PyBroadException
        try:
            # noinspection PyTypeChecker
            yield from asyncio.gather(self.handle_ws(window_info, ws), self.handle_redis(window_info, ws, subscriber))
        except Exception as e:  # Don't do except: pass
            print(e)
            import traceback
            traceback.print_exc()
        return ws

    @asyncio.coroutine
    def handle_ws(self, window_info, ws):
        while True:
            msg_ws = yield from ws.receive()
            if msg_ws:
                # noinspection PyTypeChecker
                self.on_msg_from_ws(window_info, ws, msg_ws)

    @staticmethod
    def on_msg_from_ws(window_info, ws, msg):
        if not msg:
            pass
        elif msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                ws.close()
            elif msg.data == settings.WS4REDIS_HEARTBEAT:
                ws.send_str(settings.WS4REDIS_HEARTBEAT)
            else:
                WebsocketWSGIServer.publish_message(window_info, msg.data)
                # ws.send_str(msg.data + '/answer')

    # noinspection PyUnusedLocal
    @staticmethod
    def on_msg_from_redis(window_info, ws, msg):
        message = msg.value
        ws.send_str(message)

    @asyncio.coroutine
    def handle_redis(self, window_info, ws, subscriber):
        while True:
            msg_redis = yield from subscriber.next_published()
            if msg_redis:
                # noinspection PyTypeChecker
                self.on_msg_from_redis(window_info, ws, msg_redis)


def run_server(host, port):
    # noinspection PyUnresolvedReferences
    import djangofloor.celery
    app = aiohttp.web.Application()
    http_application = get_wsgi_application()
    wsgi_handler = WSGIHandler(http_application)
    app.router.add_route('GET', settings.WEBSOCKET_URL, WebsocketEchoHandler())
    app.router.add_route("*", "/{path_info:.*}", wsgi_handler)

    loop = asyncio.get_event_loop()
    handler = app.make_handler()

    f = loop.create_server(handler, host=host, port=port, )
    srv = loop.run_until_complete(f)
    logger.info("Server started at {sock[0]}:{sock[1]}".format(sock=srv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(handler.finish_connections(1.0))
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.cleanup())
    loop.close()
