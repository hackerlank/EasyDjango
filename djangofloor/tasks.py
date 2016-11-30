# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import json
import logging
import os
import uuid
import warnings

from celery import shared_task
from django.conf import settings
from django.utils.lru_cache import lru_cache
from django.utils.module_loading import import_string
from django.utils.six import text_type
from redis import StrictRedis

from djangofloor.decorators import REGISTERED_SIGNALS, SignalConnection, REGISTERED_FUNCTIONS, FunctionConnection
from djangofloor.wsgi.window_info import WindowInfo
from djangofloor.utils import import_module, RemovedInDjangoFloor110Warning
from djangofloor.wsgi.exceptions import NoWindowKeyException

__author__ = 'Matthieu Gallet'
logger = logging.getLogger('djangofloor.signals')

SERVER = [[]]
SESSION = [[]]
WINDOW = [[]]
USER = [[]]
BROADCAST = [[]]

_signal_encoder = import_string(settings.WEBSOCKET_SIGNAL_ENCODER)
_topic_serializer = import_string(settings.WEBSOCKET_TOPIC_SERIALIZER)


# noinspection PyCallingNonCallable
@lru_cache()
def _get_redis_connection():
    return StrictRedis(**settings.WEBSOCKET_REDIS_CONNECTION)


def set_websocket_topics(request, *topics):
    # noinspection PyTypeChecker
    if not hasattr(request, 'window_key'):
        raise NoWindowKeyException('You should use the DjangoFloorMiddleware middleware')
    token = request.window_key
    request.has_websocket_topics = True
    prefix = settings.WEBSOCKET_REDIS_PREFIX
    request = WindowInfo.from_request(request)
    topic_strings = {_topic_serializer(request, x) for x in topics if x is not SERVER}
    # noinspection PyUnresolvedReferences,PyTypeChecker
    if getattr(request, 'user', None) and request.user.is_authenticated():
        topic_strings.add(_topic_serializer(request, USER))
    topic_strings.add(_topic_serializer(request, WINDOW))
    topic_strings.add(_topic_serializer(request, BROADCAST))
    connection = _get_redis_connection()
    redis_key = '%s%s' % (prefix, token)
    connection.delete(redis_key)
    for topic in topic_strings:
        if topic is not None:
            connection.rpush(redis_key, prefix + topic)
    connection.expire(redis_key, settings.WEBSOCKET_REDIS_EXPIRE)


def scall(window_info, signal_name, to=None, **kwargs):
    return _call_signal(window_info, signal_name, to=to, kwargs=kwargs, from_client=False)


def call(window_info, signal_name, to=None, kwargs=None, countdown=None, expires=None, eta=None, sharing=None,
         request=None, **other_kwargs):
    if sharing or request or other_kwargs:
        warnings.warn('djangofloor.tasks.call prototype has been changed.', RemovedInDjangoFloor110Warning)
        # noinspection PyProtectedMember
        from djangofloor.df_ws4redis import _sharing_to_topics
        window_info, signal_name = signal_name, window_info
        if request:
            window_info = request
        if to:
            other_kwargs['to'] = to
            to = _sharing_to_topics(window_info, sharing) + [SERVER]
        if kwargs:
            other_kwargs['kwargs'] = kwargs
        if countdown:
            other_kwargs['countdown'] = countdown
            countdown = None
        if expires:
            other_kwargs['expires'] = expires
            expires = None
        if eta:
            other_kwargs['eta'] = eta
            eta = None
        kwargs = other_kwargs
    return _call_signal(window_info, signal_name, to=to, kwargs=kwargs, countdown=countdown, expires=expires,
                        eta=eta, from_client=False)


def _call_signal(window_info, signal_name, to=None, kwargs=None, countdown=None, expires=None, eta=None,
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
    for topic in to:
        if topic is SERVER:
            to_server = True
        else:
            serialized_topic = _topic_serializer(window_info, topic)
            if serialized_topic is not None:
                serialized_client_topics.append(serialized_topic)
    celery_kwargs = {}
    if expires:
        celery_kwargs['expires'] = expires
    if eta:
        celery_kwargs['eta'] = eta
    if countdown:
        celery_kwargs['countdown'] = countdown
    import_signals_and_functions()
    queues = {x.get_queue(window_info, kwargs) for x in REGISTERED_SIGNALS.get(signal_name, [])}
    window_info_as_dict = None
    if window_info:
        window_info_as_dict = window_info.to_dict()
    if celery_kwargs:
        if serialized_client_topics:
            queues.add(settings.CELERY_DEFAULT_QUEUE)
        for queue in queues:
            topics = serialized_client_topics if queue == settings.CELERY_DEFAULT_QUEUE else []
            _server_signal_call.apply_async([signal_name, window_info_as_dict, kwargs, from_client, topics,
                                             to_server, queue], queue=queue, **celery_kwargs)
    else:
        if to_server:
            for queue in queues:
                _server_signal_call.apply_async([signal_name, window_info_as_dict, kwargs, from_client, [],
                                                 to_server, queue], queue=queue)
        if serialized_client_topics:
            signal_id = str(uuid.uuid4())
            for topic in serialized_client_topics:
                _call_ws_signal(signal_name, signal_id, topic, kwargs)


def _call_ws_signal(signal_name, signal_id, serialized_topic, kwargs):
    # connection = _get_redis_connection()
    connection = StrictRedis(**settings.WEBSOCKET_REDIS_CONNECTION)
    serialized_message = json.dumps({'signal': signal_name, 'opts': kwargs, 'signal_id': signal_id},
                                    cls=_signal_encoder)
    topic = settings.WEBSOCKET_REDIS_PREFIX + serialized_topic
    logger.debug("send message to topic %r" % topic)
    connection.publish(topic, serialized_message.encode('utf-8'))


def _return_ws_function_result(window_info, result_id, result, exception=None):
    """

    :param result_id:
    :param result:
    :param exception:
    :return:
    """
    # connection = _get_redis_connection()
    connection = StrictRedis(**settings.WEBSOCKET_REDIS_CONNECTION)
    json_msg = {'result_id': result_id, 'result': result, 'exception': text_type(exception) if exception else None}
    serialized_message = json.dumps(json_msg, cls=_signal_encoder)
    serialized_topic = _topic_serializer(window_info, WINDOW)
    if serialized_topic:
        topic = settings.WEBSOCKET_REDIS_PREFIX + serialized_topic
        logger.debug("send function result to topic %r" % topic)
        connection.publish(topic, serialized_message.encode('utf-8'))


@lru_cache()
def import_signals_and_functions():
    """Import all `signals.py` files to register signals.
    """
    for app in settings.INSTALLED_APPS:
        filename = None
        try:
            mod = import_module(app)
            filename = mod.__file__
        except ImportError:
            pass
        try:
            import_module('%s.signals' % app)
        except ImportError as e:
            if filename and os.path.isfile(os.path.join(os.path.dirname(filename), 'signals.py')):
                logger.exception(e)
        except Exception as e:
            logger.exception(e)
        try:
            import_module('%s.functions' % app)
        except ImportError as e:
            if filename and os.path.isfile(os.path.join(os.path.dirname(filename), 'functions.py')):
                logger.exception(e)
        except Exception as e:
            logger.exception(e)


@shared_task(serializer='json')
def _server_signal_call(signal_name, window_info_dict, kwargs=None, from_client=False, serialized_client_topics=None,
                        to_server=False, queue=None):
    logger.info('Signal "%s" called on queue "%s" to topics %s (from client?: %s, to server?: %s)' %
                (signal_name, queue, serialized_client_topics, from_client, to_server))
    try:
        if kwargs is None:
            kwargs = {}
        if serialized_client_topics:
            signal_id = str(uuid.uuid4())
            for topic in serialized_client_topics:
                _call_ws_signal(signal_name, signal_id, topic, kwargs)
        window_info = WindowInfo.from_dict(window_info_dict)
        import_signals_and_functions()
        if not to_server or signal_name not in REGISTERED_SIGNALS:
            return
        for connection in REGISTERED_SIGNALS[signal_name]:
            assert isinstance(connection, SignalConnection)
            if connection.get_queue(window_info, kwargs) != queue or \
                    (from_client and not connection.is_allowed_to(connection, window_info, kwargs)):
                continue
            new_kwargs = connection.check(kwargs)
            if new_kwargs is None:
                continue
            connection(window_info, **new_kwargs)
    except Exception as e:
        logger.exception(e)


@shared_task(serializer='json')
def _server_function_call(function_name, window_info_dict, result_id, kwargs=None):
    logger.info('Function %s called from client.' % function_name)
    e, result, window_info = None, None, None
    try:
        if kwargs is None:
            kwargs = {}
        window_info = WindowInfo.from_dict(window_info_dict)
        import_signals_and_functions()
        connection = REGISTERED_FUNCTIONS[function_name]
        assert isinstance(connection, FunctionConnection)
        if not connection.is_allowed_to(connection, window_info, kwargs):
            raise ValueError('Unauthorized function call %s' % connection.path)
        kwargs = connection.check(kwargs)
        if kwargs is not None:
            # noinspection PyBroadException
            result = connection(window_info, **kwargs)
    except Exception as e:
        logger.exception(e)
        result = None
    if window_info:
        _return_ws_function_result(window_info, result_id, result, exception=e)


# TODO remove the following functions
def import_signals():
    warnings.warn('djangofloor.tasks.import_signals() has been replaced by '
                  'djangofloor.tasks.import_signals_and_functions()', RemovedInDjangoFloor110Warning)
    return import_signals_and_functions()


def get_signal_encoder():
    warnings.warn('djangofloor.tasks.get_signal_encoder is deprecated', RemovedInDjangoFloor110Warning)
    return _signal_encoder


def get_signal_decoder():
    warnings.warn('djangofloor.tasks.get_signal_decoder is deprecated', RemovedInDjangoFloor110Warning)
    from djangofloor.wsgi.wsgi_server import signal_decoder
    return signal_decoder


@shared_task(serializer='json')
def signal_task(signal_name, request_dict, from_client, kwargs):
    warnings.warn('djangofloor.tasks.signal_task is deprecated.', RemovedInDjangoFloor110Warning)
    return _server_signal_call(signal_name, request_dict, kwargs=kwargs, from_client=from_client, to_server=True)


@shared_task(serializer='json')
def delayed_task(signal_name, request_dict, sharing, from_client, kwargs):
    warnings.warn('djangofloor.tasks.delayed_task is deprecated.', RemovedInDjangoFloor110Warning)
    import_signals()
    window_info = WindowInfo.from_dict(request_dict)
    # noinspection PyProtectedMember
    from djangofloor.df_ws4redis import _sharing_to_topics
    to = _sharing_to_topics(window_info, sharing) + [SERVER]
    return _server_signal_call(signal_name, request_dict, kwargs=kwargs, from_client=from_client,
                               serialized_client_topics=to, to_server=True)


def df_call(signal_name, request, sharing=None, from_client=False, kwargs=None, countdown=None, expires=None, eta=None):
    # noinspection PyUnusedLocal
    from_client = from_client
    warnings.warn('djangofloor.tasks.df_call is deprecated.', RemovedInDjangoFloor110Warning)
    # noinspection PyProtectedMember
    from djangofloor.df_ws4redis import _sharing_to_topics
    to = _sharing_to_topics(request, sharing) + [SERVER]
    call(signal_name, request, to=to, kwargs=kwargs, countdown=countdown, expires=expires, eta=eta)
