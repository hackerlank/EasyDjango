# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import json
import uuid

from celery import shared_task
from django.conf import settings
from django.utils.lru_cache import lru_cache
from django.utils.module_loading import import_string
from django.utils.six import text_type
from redis import StrictRedis

from easydjango.decorators import REGISTERED_SIGNALS, SignalConnection, REGISTERED_FUNCTIONS, FunctionConnection
from easydjango.request import SignalRequest
from easydjango.utils import import_module
from easydjango.websockets.exceptions import NoWindowKeyException

__author__ = 'Matthieu Gallet'

SERVER = [[]]
WINDOW = [[]]
USER = [[]]
BROADCAST = [[]]

_signal_encoder = import_string(settings.WS4REDIS_SIGNAL_ENCODER)
_topic_serializer = import_string(settings.WS4REDIS_TOPIC_SERIALIZER)


# noinspection PyCallingNonCallable
@lru_cache()
def _get_redis_connection():
    return StrictRedis(**settings.WS4REDIS_CONNECTION)


def set_websocket_topics(request, *topics):
    # noinspection PyTypeChecker
    if not hasattr(request, 'window_key'):
        raise NoWindowKeyException('You should use the EasyDjangoMiddleware middleware')
    token = request.window_key
    prefix = settings.WS4REDIS_PREFIX
    request = SignalRequest.from_request(request)
    topic_strings = {prefix + _topic_serializer(request, x) for x in topics if x is not SERVER}
    # noinspection PyUnresolvedReferences
    if request.user and request.user.is_authenticated():
        topic_strings.add(prefix + _topic_serializer(request, USER))
    topic_strings.add(prefix + _topic_serializer(request, WINDOW))
    topic_strings.add(prefix + _topic_serializer(request, BROADCAST))
    connection = _get_redis_connection()
    redis_key = '%s%s' % (prefix, token)
    connection.delete(redis_key)
    for topic in topic_strings:
        connection.rpush(redis_key, topic)
    connection.expire(redis_key, settings.WS4REDIS_EXPIRE)


def scall(request, signal_name, to=None, **kwargs):
    return _call_signal(request, signal_name, to=to, kwargs=kwargs, from_client=False)


def call(request, signal_name, to=None, kwargs=None, countdown=None, expires=None, eta=None):
    return _call_signal(request, signal_name, to=to, kwargs=kwargs, countdown=countdown, expires=expires,
                        eta=eta, from_client=False)


def _call_signal(request, signal_name, to=None, kwargs=None, countdown=None, expires=None, eta=None,
                 from_client=False):
    if kwargs is None:
        kwargs = {}
    for k in (SERVER, WINDOW, USER, BROADCAST):
        if to is k:
            to = [k]
    if to is None:
        to = [USER]
    serialized_client_topics = []
    to_server = False
    for serialized_topic in to:
        if serialized_topic is SERVER:
            to_server = True
        else:
            serialized_client_topics.append(_topic_serializer(request, serialized_topic))
    celery_kwargs = {}
    if expires:
        celery_kwargs['expires'] = expires
    if eta:
        celery_kwargs['eta'] = eta
    if countdown:
        celery_kwargs['countdown'] = countdown
    import_signals_and_functions()
    queues = {x.queue for x in REGISTERED_SIGNALS.get(signal_name, [])}
    if celery_kwargs:
        if serialized_client_topics:
            queues.add(settings.CELERY_DEFAULT_QUEUE)
        for queue in queues:
            topics = serialized_client_topics if queue == settings.CELERY_DEFAULT_QUEUE else []
            _server_signal_call.apply_async([signal_name, request.to_dict(), kwargs, from_client, topics,
                                             to_server, queue], queue=queue, **celery_kwargs)
    else:
        if to_server:
            for queue in queues:
                _server_signal_call.apply_async([signal_name, request.to_dict(), kwargs, from_client, [],
                                                 to_server, queue], queue=queue)
        if serialized_client_topics:
            signal_id = str(uuid.uuid4())
            for topic in serialized_client_topics:
                _call_ws_signal(signal_name, signal_id, topic, kwargs)


def _call_ws_signal(signal_name, signal_id, serialized_topic, kwargs):
    # connection = _get_redis_connection()
    connection = StrictRedis(**settings.WS4REDIS_CONNECTION)
    serialized_message = json.dumps({'signal': signal_name, 'opts': kwargs, 'signal_id': signal_id},
                                    cls=_signal_encoder)
    topic = settings.WS4REDIS_PREFIX + serialized_topic
    connection.publish(topic, serialized_message.encode('utf-8'))


def _return_ws_function_result(request, result_id, result, exception=None):
    """

    :param result_id:
    :param result:
    :param exception:
    :return:
    """
    # connection = _get_redis_connection()
    connection = StrictRedis(**settings.WS4REDIS_CONNECTION)
    json_msg = {'result_id': result_id, 'result': result, 'exception': text_type(exception) if exception else None}
    serialized_message = json.dumps(json_msg, cls=_signal_encoder)
    serialized_topic = _topic_serializer(request, WINDOW)
    topic = settings.WS4REDIS_PREFIX + serialized_topic
    connection.publish(topic, serialized_message.encode('utf-8'))


@lru_cache()
def import_signals_and_functions():
    """Import all `signals.py` files to register signals.
    """
    for app in settings.INSTALLED_APPS:
        try:
            import_module('%s.signals' % app)
        except ImportError:
            pass
        try:
            import_module('%s.functions' % app)
        except ImportError:
            pass


@shared_task(serializer='json')
def _server_signal_call(signal_name, request_dict, kwargs=None, from_client=False, serialized_client_topics=None,
                        to_server=False, queue=None):
    if kwargs is None:
        kwargs = {}
    if serialized_client_topics:
        signal_id = str(uuid.uuid4())
        for topic in serialized_client_topics:
            _call_ws_signal(signal_name, signal_id, topic, kwargs)
    request = SignalRequest.from_dict(request_dict)
    import_signals_and_functions()
    if not to_server or signal_name not in REGISTERED_SIGNALS:
        return
    for connection in REGISTERED_SIGNALS[signal_name]:
        assert isinstance(connection, SignalConnection)
        if connection.queue != queue or (from_client and not connection.is_allowed_to(request)):
            continue
        kwargs = connection.check(kwargs)
        if kwargs is None:
            continue
        connection(request, **kwargs)


@shared_task(serializer='json')
def _server_function_call(function_name, request_dict, result_id, kwargs=None):
    if kwargs is None:
        kwargs = {}
    request = SignalRequest.from_dict(request_dict)
    import_signals_and_functions()
    connection = REGISTERED_FUNCTIONS[function_name]
    assert isinstance(connection, FunctionConnection)
    # noinspection PyBroadException
    try:
        result = connection(request, **kwargs)
        e = None
    except Exception as e:
        result = None
    _return_ws_function_result(request, result_id, result, exception=e)
