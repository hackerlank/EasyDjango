# -*- coding: utf-8 -*-
"""
Structure of the redis database, with `prefix = settings.WS4REDIS_PREFIX`:

  * pubsub topics "{prefix}{topic}" where topic-key is given by the user-defined function
  * HSET "{prefix}topics-{window-key}" to list of topics with EXPIRE


"""
import json
import logging
import sys

import django
if django.VERSION[:2] >= (1, 7):
    django.setup()
from django.conf import settings
import django.utils.six as six
from django.core import signing
from django.utils.lru_cache import lru_cache
from django.utils.module_loading import import_string
# noinspection PyUnresolvedReferences
from django.utils.six.moves import http_client
from easydjango.decorators import REGISTERED_FUNCTIONS
from redis import StrictRedis

from easydjango.request import WindowInfo
# noinspection PyProtectedMember
from easydjango.tasks import _call_signal, SERVER, _server_function_call, import_signals_and_functions

from django.contrib.auth import get_user
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import PermissionDenied
from django import http
from django.utils.encoding import force_str, force_text
from easydjango.websockets.exceptions import WebSocketError, HandshakeError, UpgradeRequiredError

try:
    # django >= 1.8 && python >= 2.7
    # https://docs.djangoproject.com/en/1.8/releases/1.7/#django-utils-dictconfig-django-utils-importlib
    from importlib import import_module
except ImportError:
    # RemovedInDjango19Warning: django.utils.importlib will be removed in Django 1.9.
    # noinspection PyUnresolvedReferences
    from django.utils.importlib import import_module


logger = logging.getLogger('django.request')
signer = signing.Signer()
topic_serializer = import_string(settings.WS4REDIS_TOPIC_SERIALIZER)
signal_decoder = import_string(settings.WS4REDIS_SIGNAL_DECODER)


# noinspection PyCallingNonCallable
@lru_cache()
def _get_redis_connection():
    return StrictRedis(**settings.WS4REDIS_CONNECTION)


def get_websocket_topics(request):
    signed_token = request.GET.get('token', '')
    try:
        token = signer.unsign(signed_token)
    except signing.BadSignature:
        return []
    redis_key = '%s%s' % (settings.WS4REDIS_PREFIX, token)
    connection = _get_redis_connection()
    topics = connection.lrange(redis_key, 0, -1)
    return [x.decode('utf-8') for x in topics]


class WebsocketWSGIServer(object):
    def __init__(self, redis_connection=None):
        """
        redis_connection can be overriden by a mock object.
        """
        self._redis_connection = redis_connection or _get_redis_connection()

    def upgrade_websocket(self, environ, start_reponse):
        raise NotImplementedError

    def select(self, rlist, wlist, xlist, timeout=None):
        raise NotImplementedError

    # noinspection PyMethodMayBeStatic
    def assure_protocol_requirements(self, environ):
        if environ.get('REQUEST_METHOD') != 'GET':
            raise HandshakeError('HTTP method must be a GET')

        if environ.get('SERVER_PROTOCOL') != 'HTTP/1.1':
            raise HandshakeError('HTTP server protocol must be 1.1')

        if environ.get('HTTP_UPGRADE', '').lower() != 'websocket':
            raise HandshakeError('Client does not wish to upgrade to a websocket')

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        request.session = None
        request.user = None
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        if session_key is not None:
            engine = import_module(settings.SESSION_ENGINE)
            request.session = engine.SessionStore(session_key)
            request.user = get_user(request)
        window_info = WindowInfo.from_request(request)
        signed_token = request.GET.get('token', '')
        try:
            window_info.window_key = signer.unsign(signed_token)
        except signing.BadSignature:
            pass
        return window_info

    # noinspection PyMethodMayBeStatic
    def process_subscriptions(self, request):
        channels = get_websocket_topics(request)
        echo_message = bool(request.GET.get('echo', ''))
        return channels, echo_message

    @staticmethod
    def publish_message(window_info, message):
        if not message:
            return
        if message == settings.WS4REDIS_HEARTBEAT:
            return
        try:
            unserialized_message = json.loads(message)
            kwargs = unserialized_message['opts']
            if 'signal' in unserialized_message:
                signal_name = unserialized_message['signal']
                eta = int(unserialized_message.get('eta', 0)) or None
                expires = int(unserialized_message.get('expires', 0)) or None
                countdown = int(unserialized_message.get('countdown', 0)) or None
                _call_signal(window_info, signal_name, to=[SERVER], kwargs=kwargs, from_client=True, eta=eta,
                             expires=expires, countdown=countdown)
            elif 'func' in unserialized_message:
                function_name = unserialized_message['func']
                result_id = unserialized_message['result_id']
                import_signals_and_functions()
                if function_name in REGISTERED_FUNCTIONS:
                    fn = REGISTERED_FUNCTIONS[function_name]
                    _server_function_call.apply_async([function_name, window_info.to_dict(), result_id, kwargs],
                                                      queue=fn.queue or settings.CELERY_DEFAULT_QUEUE)
                else:
                    logger.warning('Unknown function "%s" called by client "%s"' %
                                   (function_name, window_info.window_key))
        except TypeError:
            pass
        except ValueError:
            logger.error('Invalid Websocket JSON message %r' % message)
            pass
        except KeyError:
            pass

    def __call__(self, environ, start_response):
        """
        Hijack the main loop from the original thread and listen on events on the Redis
        and the Websocket filedescriptors.
        """
        response = http.HttpResponse(status=200, content='Websocket Closed')
        websocket = None
        try:
            self.assure_protocol_requirements(environ)
            request = WSGIRequest(environ)
            # noinspection PyTypeChecker
            window_info = self.process_request(request)
            websocket = self.upgrade_websocket(environ, start_response)
            channels, echo_message = self.process_subscriptions(request)
            self.process_websocket(window_info, websocket, channels)
        except WebSocketError as excpt:
            logger.warning('WebSocketError: {}'.format(excpt), exc_info=sys.exc_info())
            response = http.HttpResponse(status=1001, content='Websocket Closed')
        except UpgradeRequiredError as excpt:
            logger.info('Websocket upgrade required')
            response = http.HttpResponseBadRequest(status=426, content=excpt)
        except HandshakeError as excpt:
            logger.warning('HandshakeError: {}'.format(excpt), exc_info=sys.exc_info())
            response = http.HttpResponseBadRequest(content=excpt)
        except PermissionDenied as excpt:
            logger.warning('PermissionDenied: {}'.format(excpt), exc_info=sys.exc_info())
            response = http.HttpResponseForbidden(content=excpt)
        except Exception as excpt:
            logger.error('Other Exception: {}'.format(excpt), exc_info=sys.exc_info())
            response = http.HttpResponseServerError(content=excpt)
        else:
            response = http.HttpResponse()
        finally:
            # pubsub.release()
            if websocket:
                websocket.close(code=1001, message='Websocket Closed')
            else:
                logger.warning('Starting late response on websocket')
                status_text = http_client.responses.get(response.status_code, 'UNKNOWN STATUS CODE')
                status = '{0} {1}'.format(response.status_code, status_text)
                # noinspection PyProtectedMember
                headers = response._headers.values()
                if six.PY3:
                    headers = list(headers)
                start_response(force_str(status), headers)
                logger.info('Finish non-websocket response with status code: {}'.format(response.status_code))
        return response

    def process_websocket(self, window_info, websocket, channels):
        websocket_fd = websocket.get_file_descriptor()
        listening_fds = [websocket_fd]
        redis_fd, pubsub = None, None
        if channels:
            pubsub = self._redis_connection.pubsub()
            pubsub.subscribe(*channels)
            logger.debug('Subscribed to channels: {0}'.format(', '.join(map(repr, channels))))
            # noinspection PyProtectedMember
            redis_fd = pubsub.connection._sock.fileno()
            if redis_fd:
                listening_fds.append(redis_fd)
        # subscriber.send_persited_messages(websocket)
        while websocket and not websocket.closed:
            selected_fds = self.select(listening_fds, [], [], 10.0)
            ready = selected_fds[0]
            if not ready:
                # flush empty socket
                websocket.flush()
            for fd in ready:
                if fd == websocket_fd:
                    message = websocket.receive()
                    self.publish_message(window_info, message)
                elif fd == redis_fd:
                    kind, topic, message = pubsub.parse_response()
                    kind = kind.decode('utf-8')
                    if kind == 'message':
                        websocket.send(message)
                else:
                    logger.error('Invalid file descriptor: {0}'.format(fd))
            # Check again that the websocket is closed before sending the heartbeat,
            # because the websocket can closed previously in the loop.
            if settings.WS4REDIS_HEARTBEAT and not websocket.closed and not ready:
                websocket.send(settings.WS4REDIS_HEARTBEAT)
        logger.error('websocket closed')
