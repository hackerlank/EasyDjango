# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib.auth import get_user_model
from django.db.models import Model
from djangofloor.wsgi.window_info import Session

from djangofloor.tasks import BROADCAST, USER, WINDOW

__author__ = 'Matthieu Gallet'


def serialize_topic(window_info, obj):
    if obj is BROADCAST:
        return '-broadcast'
    elif obj is WINDOW:
        if window_info is None:
            return None
        return '-window.%s' % window_info.window_key
    elif isinstance(obj, Model):
        # noinspection PyProtectedMember
        meta = obj._meta
        return '-%s.%s.%s' % (meta.app_label, meta.model_name, obj.pk)
    elif obj is USER:
        if window_info is None:
            return None
        # noinspection PyProtectedMember
        meta = get_user_model()._meta
        return '-%s.%s.%s' % (meta.app_label, meta.model_name, window_info.user_pk)
    elif isinstance(obj, Session):
        return '-session.%s' % obj.key
    return '-%s.%s' % (obj.__class__.__name__, hash(obj))
