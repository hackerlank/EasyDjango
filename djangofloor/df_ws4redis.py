# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib.auth import get_user_model
from django.utils.lru_cache import lru_cache
from django.utils.encoding import force_text
from django.utils.six import binary_type
from djangofloor.request import WindowInfo, Session
from djangofloor.tasks import SESSION, WINDOW, BROADCAST, USER, call

__author__ = 'Matthieu Gallet'


@lru_cache()
def get_pk(kind, value):
    if kind == 'user':
        return get_user_model().objects.get(username=value).pk


def ws_call(signal_name, request, sharing, kwargs):
    if isinstance(sharing, binary_type):
        sharing = force_text(sharing)
    to = []
    if sharing == SESSION:
        to = [Session(request.session_key)]
    elif sharing == WINDOW:
        to = [WINDOW]
    elif sharing == USER:
        to = [USER]
    elif sharing == BROADCAST:
        to = [BROADCAST]
    if BROADCAST in sharing:
        to = [BROADCAST]
    else:
        for username in sharing.get(USER, []):
            to.append(get_pk('user', username))
        for session in sharing.get(SESSION, []):
            to.append(Session(session))
    window_info = WindowInfo.from_request(request)
    call(window_info, signal_name, to=to, kwargs=kwargs)
