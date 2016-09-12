# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os

from django.utils.six import text_type

__author__ = 'Matthieu Gallet'

MISSING_VALUE = [[]]


def bool_setting(value):
    return text_type(value).lower() in {'1', 'ok', 'yes', 'true', 'on'}


def str_or_none(text):
    return text or None


def str_or_blank(value):
    return '' if value is None else text_type(value)


def guess_relative_path(value):
    if value is None:
        return ''
    elif os.path.exists(value):
        value = os.path.abspath(value)
        return value.replace(os.path.abspath(os.getcwd()), '.')
    return value


def strip_split(value):
    """Split the value on "," and strip spaces of the result. Remove empty values.

    >>> strip_split('keyword1, keyword2 ,,keyword3')
    ["keyword1", "keyword2", "keyword3"]

    >>> strip_split('')
    []

    >>> strip_split(None)
    []

    :param value:
    :type value:
    :return:
    :rtype:
    """
    if value:
        return [x.strip() for x in value.split(',') if x.strip()]
    return []


class ConfigField(object):
    def __init__(self, name, setting_name, from_str=str, to_str=str_or_blank, help_str=None,
                 default=None):
        """class that maps an option in a .ini file to a setting.

        :param name: the section and the option in a .ini file (like "database.engine")
        :type name: `str`
        :param setting_name: the name of the setting (like "DATABASE_ENGINE")
        :type setting_name: `str`
        :param from_str: any callable that takes a text value and returns an object. Default to `str_or_none`
        :type from_str: `callable`
        :param to_str: any callable that takes the Python value and that converts it to str
            only used for writing sample config file. Default to `str`
        :type to_str: `callable`
        :param help_str: any text that can serve has help in documentation.
            If None, then `settings.%s_HELP % setting_name` will be used as help text.
        :type help_str: `str`
        :param default: the value that will be used in documentation.
        The current setting value will be used if left to `None`.
        :type default: `object`
        """
        self.name = name
        self.setting_name = setting_name
        self.from_str = from_str
        self.to_str = to_str
        self.__doc__ = help_str
        self.value = default

    def __str__(self):
        return self.name
