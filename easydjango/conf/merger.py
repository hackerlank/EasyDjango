# -*- coding: utf-8 -*-
"""Classes and functions used for the DjangoFloor settings system
==============================================================

Define several helpers classes and internal functions for the DjangoFloor settings system, allowing to merge
settings from different sources. This file must be importable while Django is not loaded yet.
"""
from __future__ import unicode_literals, absolute_import

from collections import OrderedDict
from distutils.version import LooseVersion

from django import get_version

from easydjango.conf.fields import ConfigField
from easydjango.conf.providers import ConfigProvider
from easydjango.conf.py_values import ExpandIterable, EasyDjangoValue

try:
    # noinspection PyCompatibility
    from configparser import ConfigParser
except ImportError:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from ConfigParser import ConfigParser
import os
import string
from django.utils import six

__author__ = 'Matthieu Gallet'


class SettingMerger(object):
    """Load different settings modules and config files and merge them.
    """

    def __init__(self, project_name, settings_list, providers):
        self.settings_list = settings_list
        self.providers = providers
        self.project_name = project_name
        self.__formatter = string.Formatter()
        self.settings = {}
        self.raw_settings = OrderedDict()
        self.raw_settings['PROJECT_NAME'] = OrderedDict()
        self.raw_settings['PROJECT_NAME'][None] = project_name
        # raw_settings[setting_name] = [(source, value), (source, value), ...]
        self.__working_stack = set()

    def process(self):
        self.load_raw_settings()
        self.load_settings()

    def load_raw_settings(self):
        for field in self.settings_list:
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

    def get_setting_value(self, setting_name):
        if setting_name in self.settings:
            return self.settings[setting_name]
        elif setting_name in self.__working_stack:
            raise ValueError('Unresolvable cycling values:' + ', '.join(self.__working_stack))
        elif setting_name not in self.raw_settings:
            raise ValueError('Invaid setting reference: %s' % setting_name)
        self.__working_stack.add(setting_name)
        raw_value = self.raw_settings[setting_name][-1][1]
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
        elif isinstance(obj, EasyDjangoValue):
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
                for key in 'TEMPLATE_DIRS', 'TEMPLATE_CONTEXT_PROCESSORS', 'TEMPLATE_LOADERS':
                    if key in self.settings:
                        del self.settings[key]

    @staticmethod
    def ensure_dir(path_, parent_=True):
        """Ensure that the given directory exists

        :param path_: the path to check
        :param parent_: only ensure the existence of the parent directory

        """
        dirname_ = os.path.dirname(path_) if parent_ else path_
        if not os.path.isdir(dirname_):
            try:
                os.makedirs(dirname_)
                print('Directory %s created.' % dirname_)
            except IOError:
                print('Unable to create directory %s.' % dirname_)
