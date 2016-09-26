# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from easydjango.signals.connection import WINDOW, USER, BROADCAST

__author__ = 'Matthieu Gallet'


def serialize_topic(request, obj):
    if obj is BROADCAST:
        return '-broadcast'
    elif obj is WINDOW:
        return '-window%s' % request.window_key
    elif obj is USER:
        return '-user%s' % request.user_pk
    elif isinstance(obj, get_user_model()):
        return '-user%s' % obj.pk
    return '%s%s' % (obj.__class__.__name__, hash(obj))
