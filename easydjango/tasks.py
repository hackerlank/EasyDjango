# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import json
import uuid

from celery import shared_task
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.lru_cache import lru_cache
from redis import StrictRedis

from easydjango.signals.connection import BROADCAST, SERVER, WINDOW, USER

__author__ = 'Matthieu Gallet'


signal_encoder = import_string(settings.WS4REDIS_SIGNAL_ENCODER)
topic_serializer = import_string(settings.WS4REDIS_TOPIC_SERIALIZER)


# noinspection PyCallingNonCallable
@lru_cache()
def _get_redis_connection():
    return StrictRedis(**settings.WS4REDIS_CONNECTION)


def call(request, signal_name, to=None, **kwargs):
    return _call_signal(request, signal_name, to=to, kwargs=kwargs, from_client=False)


def delay_signal(request, signal_name, to=None, kwargs=None, countdown=None, expires=None, eta=None):
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
            serialized_client_topics.append(topic_serializer(request, serialized_topic))
    celery_kwargs = {}
    if expires:
        celery_kwargs['expires'] = expires
    if eta:
        celery_kwargs['eta'] = eta
    if countdown:
        celery_kwargs['countdown'] = countdown

    if celery_kwargs:
        _server_signal_call.apply_async([signal_name, request.to_dict(), kwargs, from_client, serialized_client_topics,
                                         to_server], **celery_kwargs)
    else:
        if to_server:
            _server_signal_call.apply_async([signal_name, request.to_dict(), kwargs, from_client, [], to_server])
        if serialized_client_topics:
            signal_id = str(uuid.uuid4())
            for topic in serialized_client_topics:
                _call_ws_signal(signal_name, signal_id, topic, kwargs)


def _call_ws_signal(signal_name, signal_id, serialized_topic, kwargs):
    connection = _get_redis_connection()
    serialized_message = json.dumps({'signal': signal_name, 'opts': kwargs, 'id': signal_id}, cls=signal_encoder)
    connection.publish(serialized_topic, serialized_message.encode('utf-8'))


@shared_task(serializer='json')
def _server_signal_call(signal_name, request_dict, args=None, kwargs=None,
                        from_client=False, serialized_client_topics=None, to_server=False):
    if serialized_client_topics:
        signal_id = str(uuid.uuid4())
        for topic in serialized_client_topics:
            _call_ws_signal(signal_name, signal_id, topic, kwargs)
    if not to_server:
        return
    elif from_client:
        pass
