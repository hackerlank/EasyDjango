# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
try:
    from inspect import signature
except ImportError:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from funcsigs import signature

__author__ = 'Matthieu Gallet'

REGISTERED_SIGNALS = {}
REGISTERED_FUNCTIONS = {}


# noinspection PyUnusedLocal
def server_side(request):
    """does not allow a signal to be called from WebSockets

    >>> @signal(is_allowed_to=server_side)
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    return False


# noinspection PyUnusedLocal
def everyone(request):
    """allow everyone to call a WS signal or function

    >>> @signal(is_allowed_to=everyone)
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    return True


def is_authenticated(request):
    """restrict a WS signal or a WS function to authenticated users

    >>> @signal(is_allowed_to=is_authenticated)
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    return request.is_authenticated()


def is_anonymous(request):
    """restrict a WS signal or a WS function to anonymous users

    >>> @signal(is_allowed_to=is_anonymous)
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    return request.is_anonymous()


# noinspection PyPep8Naming
class has_perm(object):
    """restrict a WS signal or a WS function to users with permission "perm"

    >>> @signal(is_allowed_to=has_perm('app_label.codename'))
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    def __init__(self, perm):
        self.perm = perm

    def __call__(self, request):
        return request.has_perm(self.perm)


class Connection(object):
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
        # noinspection PyTypeChecker
        if hasattr(fn, '__name__'):
            self.__name__ = fn.__name__
        self.register()

    def check(self, **kwargs):
        return True

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def register(self):
        raise NotImplementedError


class SignalConnection(Connection):
    def register(self):
        REGISTERED_SIGNALS.setdefault(self.path, []).append(self)


class FunctionConnection(Connection):
    def register(self):
        REGISTERED_FUNCTIONS[self.path] = self


def signal(fn=None, path=None, is_allowed_to=server_side):
    def wrapped(fn_):
        return SignalConnection(fn=fn_, path=path, is_allowed_to=is_allowed_to)
    if fn is not None:
        wrapped = wrapped(fn)
    return wrapped


def function(fn=None, path=None, is_allowed_to=server_side):
    def wrapped(fn_):
        return FunctionConnection(fn=fn_, path=path, is_allowed_to=is_allowed_to)
    if fn is not None:
        wrapped = wrapped(fn)
    return wrapped
