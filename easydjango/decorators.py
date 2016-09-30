# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
try:
    from inspect import signature
except ImportError:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from funcsigs import signature

__author__ = 'Matthieu Gallet'

REGISTERED_SIGNALS = {}


# noinspection PyUnusedLocal
def server_side(request):
    return False


# noinspection PyUnusedLocal
def everyone(request):
    return True


def is_authenticated(request):
    return request.is_authenticated()


def is_anonymous(request):
    return request.is_anonymous()


class SignalConnection(object):
    def __init__(self, fn, path=None, is_allowed_to=server_side):
        self.function = fn
        # noinspection PyTypeChecker
        self.path = path or (hasattr(fn, '__name__') and fn.__name__)
        self.is_allowed_to = is_allowed_to
        self.accept_kwargs = False
        self.argument_types = {}
        self.required_arguments_names = []
        self.optional_arguments_names = []

        # fetch signature to analyze arguments
        sig = signature(fn)
        request_present = False
        for key, param in sig.parameters.items():
            if key in ('request', ):
                request_present = True
                continue
            if param.kind == param.VAR_KEYWORD:  # corresponds to "fn(**kwargs)"
                self.accept_kwargs = True
            elif param.kind == param.VAR_POSITIONAL:  # corresponds to "fn(*args)"
                raise ValueError('Cannot connect a signal using the *%s syntax' % key)
            elif param.default == param.empty:  # "fn(foo)" : kind = POSITIONAL_ONLY or POSITIONAL_OR_KEYWORD
                self.required_arguments_names.append(key)
                if param.annotation != param.empty and callable(param.annotation):
                    self.argument_types[key] = param.annotation
            else:  # "fn(foo=bar)" : kind = POSITIONAL_OR_KEYWORD or KEYWORD_ONLY
                self.optional_arguments_names.append(key)
                if param.annotation != param.empty and callable(param.annotation):
                    self.argument_types[key] = param.annotation
        if not request_present:
            raise ValueError('Your signal must takes "request" as first argument')
        REGISTERED_SIGNALS.setdefault(path, []).append(self)
        # noinspection PyTypeChecker
        if hasattr(fn, '__name__'):
            self.__name__ = fn.__name__

    def check(self, **kwargs):
        return True

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


def connect(fn=None, path=None, is_allowed_to=server_side):
    def wrapped(fn_):
        return SignalConnection(fn=fn_, path=path, is_allowed_to=is_allowed_to)
    if fn is not None:
        wrapped = wrapped(fn)
    return wrapped
