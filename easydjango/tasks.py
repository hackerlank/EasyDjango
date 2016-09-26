# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import uuid

from celery import shared_task

from easydjango.websockets.wsgi_server import call_ws_signal

__author__ = 'Matthieu Gallet'


@shared_task(serializer='json')
def server_signal_call(signal_name, request_dict, args=None, kwargs=None,
                       from_client=False, serialized_client_topics=None, to_server=False):
    if serialized_client_topics:
        signal_id = str(uuid.uuid4())
        for topic in serialized_client_topics:
            call_ws_signal(signal_name, signal_id, topic, kwargs)
    if not to_server:
        return
    elif from_client:
        pass
