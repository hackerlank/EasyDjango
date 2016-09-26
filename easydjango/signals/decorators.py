# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from easydjango.signals import SignalConnection, server_side


def connect(fn=None, path=None, is_allowed_to=server_side):
    def wrapped(fn_):
        return SignalConnection(fn=fn_, path=path, is_allowed_to=is_allowed_to)
    if fn is not None:
        wrapped = wrapped(fn)
    return wrapped
