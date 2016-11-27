# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging
import re
import warnings

from django import forms
from django.conf import settings
from django.http import QueryDict
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from djangofloor.utils import RemovedInDjangoFloor110Warning

try:
    from inspect import signature
except ImportError:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from funcsigs import signature

__author__ = 'Matthieu Gallet'
logger = logging.getLogger('djangofloor.signals')

REGISTERED_SIGNALS = {}
REGISTERED_FUNCTIONS = {}


# noinspection PyUnusedLocal
def server_side(window_info):
    """does not allow a signal to be called from WebSockets

    >>> @signal(is_allowed_to=server_side)
    >>> def my_signal(window_info, arg1=None):
    >>>     print(window_info, arg1)
    """
    return False


# noinspection PyUnusedLocal
def everyone(window_info):
    """allow everyone to call a WS signal or function

    >>> @signal(is_allowed_to=everyone)
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    return True


def is_authenticated(window_info):
    """restrict a WS signal or a WS function to authenticated users

    >>> @signal(is_allowed_to=is_authenticated)
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    return window_info and window_info.is_authenticated()


def is_anonymous(window_info):
    """restrict a WS signal or a WS function to anonymous users

    >>> @signal(is_allowed_to=is_anonymous)
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    return window_info and window_info.is_anonymous()


def is_staff(window_info):
    return window_info and window_info.is_staff


def is_superuser(window_info):
    return window_info and window_info.is_superuser


# noinspection PyPep8Naming
class has_perm(object):
    """restrict a WS signal or a WS function to users with permission "perm"

    >>> @signal(is_allowed_to=has_perm('app_label.codename'))
    >>> def my_signal(request, arg1=None):
    >>>     print(request, arg1)
    """
    def __init__(self, perm):
        self.perm = perm

    def __call__(self, window_info):
        return window_info and window_info.has_perm(self.perm)


class Connection(object):
    def __init__(self, fn, path=None, is_allowed_to=server_side, queue=None):
        self.function = fn
        # noinspection PyTypeChecker
        self.path = path or (hasattr(fn, '__name__') and fn.__name__)
        if not re.match(r'^([_a-zA-Z]\w*)(\.[_a-zA-Z]\w*)*$', self.path):
            raise ValueError('Invalid identifier: %s' % self.path)
        self.is_allowed_to = is_allowed_to
        self.queue = queue or settings.CELERY_DEFAULT_QUEUE
        self.accept_kwargs = False
        self.argument_types = {}
        self.required_arguments_names = set()
        self.optional_arguments_names = set()
        self.accepted_argument_names = set()
        self.signature_check(fn)
        # noinspection PyTypeChecker
        if hasattr(fn, '__name__'):
            self.__name__ = fn.__name__

    def signature_check(self, fn):
        # fetch signature to analyze arguments
        sig = signature(fn)
        window_info_is_present = False
        for key, param in sig.parameters.items():
            if key in ('window_info', ):
                window_info_is_present = True
                continue
            if param.kind == param.VAR_KEYWORD:  # corresponds to "fn(**kwargs)"
                self.accept_kwargs = True
            elif param.kind == param.VAR_POSITIONAL:  # corresponds to "fn(*args)"
                raise ValueError('Cannot connect a signal using the *%s syntax' % key)
            elif param.default == param.empty:  # "fn(foo)" : kind = POSITIONAL_ONLY or POSITIONAL_OR_KEYWORD
                self.required_arguments_names.add(key)
                if param.annotation != param.empty and callable(param.annotation):
                    self.argument_types[key] = param.annotation
                self.accepted_argument_names.add(key)
            else:  # "fn(foo=bar)" : kind = POSITIONAL_OR_KEYWORD or KEYWORD_ONLY
                self.optional_arguments_names.add(key)
                self.accepted_argument_names.add(key)
                if param.annotation != param.empty and callable(param.annotation):
                    self.argument_types[key] = param.annotation
        if not window_info_is_present:
            raise ValueError('%s(%s) must takes "window_info" as first argument' % (self.__class__.__name__, self.path))

    def check(self, kwargs):
        cls = self.__class__.__name__
        for k, v in self.argument_types.items():
            try:
                if k in kwargs:
                    kwargs[k] = v(kwargs[k])
            except ValueError:
                logger.info('%s("%s"): Invalid value %r for argument "%s".' % (cls, self.path, v, k))
                return None
        for k in self.required_arguments_names:
            if k not in kwargs:
                logger.info('%s("%s"): Missing required argument "%s".' % (cls, self.path, k))
                return None
        if not self.accept_kwargs:
            for k in kwargs:
                if k not in self.accepted_argument_names:
                    logger.info('%s("%s"): Invalid argument "%s".' % (cls, self.path, k))
                    return None
        return kwargs

    def __call__(self, window_info, **kwargs):
        return self.function(window_info, **kwargs)

    def register(self):
        raise NotImplementedError

    def get_queue(self, path, window_info, original_kwargs):
        if callable(self.queue):
            return self.queue(path, window_info, original_kwargs)
        return text_type(self.queue) or settings.CELERY_DEFAULT_QUEUE


class SignalConnection(Connection):
    def register(self):
        REGISTERED_SIGNALS.setdefault(self.path, []).append(self)


class FunctionConnection(Connection):
    def register(self):
        REGISTERED_FUNCTIONS[self.path] = self


def signal(fn=None, path=None, is_allowed_to=server_side, queue=None, cls=SignalConnection):
    def wrapped(fn_):
        wrapper = cls(fn=fn_, path=path, is_allowed_to=is_allowed_to, queue=queue)
        wrapper.register()
        return fn_

    if fn is not None:
        wrapped = wrapped(fn)
    return wrapped


def function(fn=None, path=None, is_allowed_to=server_side, queue=None):
    """

    .. code-block:: javascript

    $.dfws.path({}).then(function(x) { alert(x); });

     """
    return signal(fn=fn, path=path, is_allowed_to=is_allowed_to, queue=queue, cls=FunctionConnection)


class FormValidator(FunctionConnection):
    def signature_check(self, fn):
        if not isinstance(fn, type) or not issubclass(fn, forms.BaseForm):
            raise ValueError('validate_form only apply to Django Forms')
        self.required_arguments_names = set()
        self.optional_arguments_names = {'data'}
        self.accepted_argument_names = {'data'}

    def __call__(self, window_info, data=None):
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
        def test(window_info, value: RE("\d{3}a\d{3}")):
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
        def test(window_info, value: Choice([True, False])):
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
        def test(window_info, value: SerializedForm(SimpleForm), other: int):
            print(value.is_valid())

    How to use it with Python2:

    .. code-block:: python

        @signal(path='myproject.signals.test')
        def test(window_info, value, other):
            value = SerializedForm(SimpleForm)(value)
            print(value.is_valid())


    On the JS side, the easiest way is to serialize the form with JQuery:

    .. code-block:: html

        <form onsubmit="return $.df.call('myproject.signals.test', {value: $(this).serializeArray(), other: 42})">
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


class LegacySignalConnection(SignalConnection):
    def __call__(self, window_info, **kwargs):
        result = super(LegacySignalConnection, self).__call__(window_info, **kwargs)
        if result:
            # noinspection PyUnresolvedReferences
            from djangofloor.tasks import df_call
            for data in result:
                df_call(data['signal'], window_info, sharing=data.get('sharing'), from_client=False,
                        kwargs=data['options'])


def connect(fn=None, path=None, delayed=False, allow_from_client=True, auth_required=True):
    delayed = delayed
    if not delayed:
        warnings.warn('The "delayed" argument is deprecated and useless.', RemovedInDjangoFloor110Warning)
    if allow_from_client and auth_required:
        is_allowed_to = is_authenticated
    elif allow_from_client:
        is_allowed_to = everyone
    else:
        is_allowed_to = server_side
    return signal(fn=fn, path=path, is_allowed_to=is_allowed_to)
