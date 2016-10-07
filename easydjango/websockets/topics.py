# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib.auth import get_user_model
from django.db.models import Model

from easydjango.tasks import BROADCAST, USER, WINDOW

__author__ = 'Matthieu Gallet'


def serialize_topic(request, obj):
    if obj is BROADCAST:
        return '-broadcast'
    elif obj is WINDOW:
        return '-window.%s' % request.window_key
    elif isinstance(obj, Model):
        # noinspection PyProtectedMember
        meta = obj._meta
        return '-%s.%s.%s' % (meta.app_label, meta.model_name, obj.pk)
    elif obj is USER:
        # noinspection PyProtectedMember
        meta = get_user_model()._meta
        return '-%s.%s.%s' % (meta.app_label, meta.model_name, request.user_pk)
    return '-%s.%s' % (obj.__class__.__name__, hash(obj))
