# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import re

from django import forms
from django.http import QueryDict

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


def is_staff(request):
    return request.is_staff


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
        self.signature_check(fn)
        # noinspection PyTypeChecker
        if hasattr(fn, '__name__'):
            self.__name__ = fn.__name__

    def signature_check(self, fn):
        # fetch signature to analyze arguments
        sig = signature(fn)
        request_present = False
        for key, param in sig.parameters.items():
            if key in ('request',):
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

    def check(self, kwargs):
        return kwargs

    def __call__(self, request, **kwargs):
        return self.function(request, **kwargs)

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
        wrapper = SignalConnection(fn=fn_, path=path, is_allowed_to=is_allowed_to)
        wrapper.register()
        return fn_

    if fn is not None:
        wrapped = wrapped(fn)
    return wrapped


def function(fn=None, path=None, is_allowed_to=server_side):
    """

    .. code-block:: javascript

    $.edws.path({}).then(function(x) { alert(x); });

     """
    def wrapped(fn_):
        wrapper = FunctionConnection(fn=fn_, path=path, is_allowed_to=is_allowed_to)
        wrapper.register()
        return fn_

    if fn is not None:
        wrapped = wrapped(fn)
    return wrapped


class FormValidator(FunctionConnection):
    def signature_check(self, fn):
        if not isinstance(fn, type) or not issubclass(fn, forms.BaseForm):
            raise ValueError('validate_form only apply to Django Forms')
        self.required_arguments_names = ['request']
        self.optional_arguments_names = ['data']

    def __call__(self, request, data=None):
        form = SerializedForm(self.function)(data)
        valid = form.is_valid()
        return {'valid': valid, 'errors': {f: e.get_json_data(escape_html=False) for f, e in form.errors.items()},
                'help_texts': {f: e.help_text for (f, e) in form.fields.items() if e.help_text}}


def validate_form(form_cls=None, path=None, is_allowed_to=server_side):
    if path is None or is_allowed_to == server_side:
        # @validate_form
        # class MyForm(forms.Form):
        #     ...
        raise ValueError('is_allowed_to and path are not configured for the validate_form decorator')

    def wrapped(form_cls_):
        wrapper = FormValidator(form_cls_, path=path, is_allowed_to=is_allowed_to)
        wrapper.register()
        return form_cls_

    if form_cls:
        return wrapped(form_cls)
    return wrapped


class RE(object):
    """ used to check in a string value match a given regexp.

    Example (requires Python 3.2+), for a function that can only handle a string on the form 123a456:

    .. code-block:: python

        @signal(path='myproject.signals.test')
        def test(request, value: RE("\d{3}a\d{3}")):
            pass

    Your code wan't be called if value has not the right form.


    :param value: the pattern of the regexp
    :type value: `str`
    :param caster: if not `None`, any callable applied to the value (if valid)
    :type caster: `callable` or `None`
    :param flags: regexp flags passed to `re.compile`
    :type flags: `int`
    """
    def __init__(self, value, caster=None, flags=0):
        self.caster = caster
        self.regexp = re.compile(value, flags=flags)

    def __call__(self, value):
        matcher = self.regexp.match(value)
        if not matcher:
            raise ValueError
        value = matcher.group(1) if matcher.groups() else value
        return self.caster(value) if self.caster else value


class Choice(object):
    """ used to check if a value is among some valid choices.

    Example (requires Python 3.2+), for a function that can only two values:

    .. code-block:: python

        @signal(path='myproject.signals.test')
        def test(request, value: Choice([True, False])):
            pass

    Your code wan't be called if value is not True or False.

    :param caster: callable to convert the provided deserialized JSON data before checking its validity.
    """
    def __init__(self, values, caster=None):
        self.values = set(values)
        self.caster = caster

    def __call__(self, value):
        value = self.caster(value) if self.caster else value
        if value not in self.values:
            raise ValueError
        return value


class SerializedForm(object):
    """Transform values sent by JS to a Django form.

    Given a form and a :class:`list` of :class:`dict`, transforms the :class:`list` into a
    :class:`django.http.QueryDict` and initialize the form with it.

    >>> from django import forms
    >>> class SimpleForm(forms.Form):
    ...    field = forms.CharField()
    ...
    >>> x = SerializedForm(SimpleForm)
    >>> form = x([{'field': 'object'}])
    >>> form.is_valid()
    True

    How to use it with Python3:

    .. code-block:: python

        @signal(path='myproject.signals.test')
        def test(request, value: SerializedForm(SimpleForm), other: int):
            print(value.is_valid())

    How to use it with Python2:

    .. code-block:: python

        @signal(path='myproject.signals.test')
        def test(request, value, other):
            value = SerializedForm(SimpleForm)(value)
            print(value.is_valid())


    On the JS side, the easiest way is to serialize the form with JQuery:

    .. code-block:: html

        <form onsubmit="return $.ed.call('myproject.signals.test', {value: $(this).serializeArray(), other: 42})">
            <input name='field' value='test' type='text'>
        </form>


    """
    def __init__(self, form_cls):
        self.form_cls = form_cls

    def __call__(self, value, *args, **kwargs):
        """
        :param value:
        :type value: :class:`list` of :class:`dict`
        :return:
        :rtype: :class:`django.forms.Form`
        """
        query_dict = QueryDict('', mutable=True)
        for obj in value:
            query_dict.update({obj['name']: obj['value']})
        return self.form_cls(query_dict, *args, **kwargs)
