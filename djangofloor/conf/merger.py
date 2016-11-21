# -*- coding: utf-8 -*-
"""Classes and functions used for the DjangoFloor settings system
==============================================================

Define several helpers classes and internal functions for the DjangoFloor settings system, allowing to merge
settings from different sources. This file must be importable while Django is not loaded yet.
"""
from __future__ import unicode_literals, absolute_import

import traceback
import warnings
from collections import OrderedDict
from distutils.version import LooseVersion

from django import get_version
from django.conf import LazySettings
from django.utils.functional import empty

from djangofloor.conf.config_values import ExpandIterable, ConfigValue
from djangofloor.conf.fields import ConfigField
from djangofloor.conf.providers import ConfigProvider, PythonConfigFieldsProvider

try:
    # noinspection PyCompatibility
    from configparser import ConfigParser
except ImportError:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from ConfigParser import ConfigParser
import string
from django.utils import six

__author__ = 'Matthieu Gallet'

_deprecated_settings = {
    'BIND_ADDRESS': 'Replaced by "LISTEN_ADDRESS".',
    'BROKER_DB': 'Replaced by "CELERY_DB"',
    'FLOOR_AUTHENTICATION_HEADER': 'Replaced by "DF_REMOTE_USER_HEADER"',
    'FLOOR_BACKUP_SINGLE_TRANSACTION': None,
    'FLOOR_DEFAULT_GROUP_NAME': 'Repladed by "DF_DEFAULT_GROUPS"',
    'FLOOR_EXTRA_CSS': 'Replaced by DF_CSS.',
    'FLOOR_EXTRA_JS': 'Replaced by DF_JS.',
    'FLOOR_FAKE_AUTHENTICATION_USERNAME': 'Replaced by "DF_FAKE_AUTHENTICATION_USERNAME"',
    'FLOOR_WS_FACILITY': None,
    'FLOOR_INDEX': 'Replaced by "DF_INDEX_VIEW" and class-based views.',
    'FLOOR_PROJECT_NAME': 'Replaced by "PROJECT_NAME"',
    'FLOOR_PROJECT_VERSION': 'Replaced by "DF_PROJECT_VERSION"',
    'FLOOR_SIGNAL_DECODER': 'Replaced by "WS4REDIS_SIGNAL_DECODER".',
    'FLOOR_SIGNAL_ENCODER': 'Replaced by "WS4REDIS_SIGNAL_ENCODER".',
    'FLOOR_URL_CONF': 'Replaced by "DF_URL_CONF".',
    'FLOOR_USE_WS4REDIS': 'ws4redis is not used anymore.',
    'LOG_PATH': 'Use "LOG_DIRECTORY" instead.',
    'LOGOUT_URL': None,
    'MAX_REQUESTS': None,
    'PROTOCOL': 'Use "SERVER_PROTOCOL" instead.',
    'REDIS_HOST': 'Replaced by "CELERY_HOST".',
    'REDIS_PORT': 'Replaced by "CELERY_PORT".',
    'REVERSE_PROXY_IPS': None,
    'REVERSE_PROXY_TIMEOUT': None,
    'REVERSE_PROXY_SSL_KEY_FILE': None,
    'REVERSE_PROXY_SSL_CRT_FILE': None,
    'REVERSE_PROXY_PORT': 'Use the port component of "SERVER_BASE_URL" instead.',
    'THREADS': 'Replaced by "UWSGI_THREADS".',
    'USE_SCSS': None,
    'WORKERS': None,
    'WS4REDIS_EMULATION_INTERVAL': None,
    'WS4REDIS_SUBSCRIBER': None,
}
_warned_settings = set()


def __getattr__(self, name):
    if name in _deprecated_settings and name not in _warned_settings:
        from djangofloor.utils import RemovedInDjangoFloor110Warning
        f = traceback.extract_stack()
        if not f[-1][0].endswith('/debug.py'):
            msg = 'Setting "%s" is deprecated. ' % name
            msg += _deprecated_settings[name] or ''
            warnings.warn(msg, RemovedInDjangoFloor110Warning, stacklevel=2)
            _warned_settings.add(name)
    if self._wrapped is empty:
        self._setup(name)
    return getattr(self._wrapped, name)


LazySettings.__getattr__ = __getattr__


class SettingMerger(object):
    """Load different settings modules and config files and merge them.
    """

    def __init__(self, fields_provider, providers, extra_values=None, read_only=False):
        self.fields_provider = fields_provider or PythonConfigFieldsProvider(None)
        extra_values = extra_values or {}
        self.providers = providers
        self.__formatter = string.Formatter()
        self.settings = {}
        self.raw_settings = OrderedDict()
        for key, value in extra_values.items():
            self.raw_settings[key] = OrderedDict()
            self.raw_settings[key][None] = value
        # raw_settings[setting_name][str(provider) or None] = raw_value
        self.__working_stack = set()
        self.read_only = read_only

    def process(self):
        self.load_raw_settings()
        self.load_settings()

    def load_raw_settings(self):
        for field in self.fields_provider.get_config_fields():
            assert isinstance(field, ConfigField)
            self.raw_settings.setdefault(field.setting_name, OrderedDict())
            self.raw_settings[field.setting_name][None] = field.value
            for provider in self.providers:
                assert isinstance(provider, ConfigProvider)
                if provider.has_value(field):
                    value = provider.get_value(field)
                    # noinspection PyTypeChecker
                    self.raw_settings[field.setting_name][str(provider)] = value
        for provider in self.providers:
            assert isinstance(provider, ConfigProvider)
            source_name = str(provider)
            for setting_name, value in provider.get_extra_settings():
                self.raw_settings.setdefault(setting_name, OrderedDict())
                self.raw_settings[setting_name][source_name] = value

    def has_setting_value(self, setting_name):
        return setting_name in self.raw_settings

    def get_setting_value(self, setting_name):
        if setting_name in self.settings:
            return self.settings[setting_name]
        elif setting_name in self.__working_stack:
            raise ValueError('Invalid cyclic dependency between ' + ', '.join(self.__working_stack))
        elif setting_name not in self.raw_settings:
            raise ValueError('Invalid setting reference: %s' % setting_name)
        self.__working_stack.add(setting_name)
        raw_value = None
        for raw_value in self.raw_settings[setting_name].values():
            pass
        value = self.analyze_raw_value(raw_value)
        self.settings[setting_name] = value
        self.__working_stack.remove(setting_name)
        return value

    def load_settings(self):
        for setting_name in self.raw_settings:
            self.get_setting_value(setting_name)

    def analyze_raw_value(self, obj):
        """Parse the object for replacing variables by their values.

        If `obj` is a string like "THIS_IS_{TEXT}", search for a setting named "TEXT" and replace {TEXT} by its value
        (say, "VALUE"). The returned object is then equal to "THIS_IS_VALUE".
        If `obj` is a list, a set, a tuple or a dict, its components are recursively parsed.
        If `obj` is a :class:`djangofloor.utils.DirectoryPath` or a :class:`djangofloor.utils.FilePath`,
        required parent directories are automatically created and the name is returned.
        Otherwise, `obj` is returned as-is.


        :param obj: object to analyze
        :return: the parsed setting
        """
        if isinstance(obj, six.string_types):
            values = {}
            for (literal_text, field_name, format_spec, conversion) in self.__formatter.parse(obj):
                if field_name is not None:
                    values[field_name] = self.get_setting_value(field_name)
            if values:
                return self.__formatter.format(obj, **values)
        elif isinstance(obj, ConfigValue):
            return obj.get_value(self)
        elif isinstance(obj, list) or isinstance(obj, tuple):
            result = []
            for sub_obj in obj:
                if isinstance(sub_obj, ExpandIterable):
                    result += self.get_setting_value(sub_obj.value)
                else:
                    result.append(self.analyze_raw_value(sub_obj))
            if isinstance(obj, tuple):
                return tuple(result)
            return result
        elif isinstance(obj, set):
            result = set()
            for sub_obj in obj:
                if isinstance(sub_obj, ExpandIterable):
                    result |= self.get_setting_value(sub_obj.value)
                else:
                    result.add(self.analyze_raw_value(sub_obj))
            return result
        elif isinstance(obj, dict):
            result = {}
            for sub_key, sub_obj in obj.items():
                if isinstance(sub_obj, ExpandIterable):
                    result.update(self.get_setting_value(sub_obj.value))
                else:
                    result[self.analyze_raw_value(sub_key)] = (self.analyze_raw_value(sub_obj))
            return result
        return obj

    def post_process(self):
        """Perform some cleaning on settings:

            * remove duplicates in `INSTALLED_APPS` (keeps only the first occurrence)
        """
        # remove duplicates in INSTALLED_APPS
        self.settings['INSTALLED_APPS'] = list(OrderedDict.fromkeys(self.settings['INSTALLED_APPS']))
        django_version = get_version()
        # remove deprecated settings
        if LooseVersion(django_version) >= LooseVersion('1.8'):
            if 'TEMPLATES' in self.settings:
                for key in 'TEMPLATE_DIRS', 'TEMPLATE_CONTEXT_PROCESSORS', 'TEMPLATE_LOADERS', 'TEMPLATE_DEBUG':
                    if key in self.settings:
                        del self.settings[key]
