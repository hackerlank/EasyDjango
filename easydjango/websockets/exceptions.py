# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from socket import error as socket_error

from django.http import BadHeaderError

__author__ = 'Matthieu Gallet'


# noinspection PyClassHasNoInit
class WebSocketError(socket_error):
    """
    Raised when an active websocket encounters a problem.
    """


class NoWindowKeyException(ValueError):
    """raise when the middleware EasyDjangoMiddleware is not used."""


# noinspection PyClassHasNoInit
class FrameTooLargeException(WebSocketError):
    """
    Raised if a received frame is too large.
    """


class HandshakeError(BadHeaderError):
    """
    Raised if an error occurs during protocol handshake.
    """


class UpgradeRequiredError(HandshakeError):
    """
    Raised if protocol must be upgraded.
    """
