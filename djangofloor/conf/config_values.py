# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os

__author__ = 'Matthieu Gallet'


class ConfigValue(object):
    """Base class for special setting values. When a setting is a :class:`easydjango.settings.ConfigValue`,
      then the method `get_value(merger)` is called for getting the definitive value.
    """
    def __init__(self, value):
        self.value = value

    def get_value(self, merger):
        """ Return the intepreted value
        :param merger: merger object, with all interpreted settings
        :type merger: :class:`djangofloor.utils.SettingMerger`
        :return:
        :rtype:
        """
        raise NotImplementedError


class RawValue(ConfigValue):

    def get_value(self, merger):
        return self.value


class Path(ConfigValue):

    def get_value(self, merger):
        return merger.analyze_raw_value(self.value)

    def __repr__(self):
        return str(self.value)


class AutocreateDirectory(Path):
    """Represent a directory that must be created on startup
    """

    def get_value(self, merger):
        value = merger.analyze_raw_value(self.value)
        if not os.path.isdir(value):
            os.makedirs(value)
        return value


class AutocreateFile(Path):
    """Represent a file, whose parent directory should be created on startup
    """

    def get_value(self, merger):
        value = merger.analyze_raw_value(self.value)
        dirname = os.path.dirname(value)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return value


class SettingReference(ConfigValue):
    """Reference any setting object by its name.
    Allow to reuse a list defined in another setting file.

    in `defaults.py`:

    >>> SETTING_1 = True
    >>> SETTING_2 = SettingReference('SETTING_1')

    In `local_settings.py`

    >>> SETTING_1 = False

    In your code:

    >>> from django.conf import settings

    Then `settings.SETTING_2` is equal to `False`
    """

    def __init__(self, value, func=None):
        super(SettingReference, self).__init__(value)
        self.func = func

    def get_value(self, merger):
        result = merger.get_setting_value(self.value)
        if self.func:
            result = self.func(result)
        return result


class CallableSetting(ConfigValue):
    """
    Require a function(kwargs) as argument, this function will be called with all already computed settings in a dict.

    >>> SETTING_1 = True
    >>> SETTING_2 = CallableSetting(lambda x: not x['SETTING_1'], 'SETTING_1')

    In `local_settings.py`

    >>> SETTING_1 = False

    In your code:

    >>> from django.conf import settings

    Then `settings.SETTING_2` is equal to `True`

    You can provide a list of required settings that must be available before the call to your function.
    """

    def __init__(self, value, *required):
        super(CallableSetting, self).__init__(value)
        self.required = required

    def get_value(self, merger):
        for required in self.required:
            merger.get_setting_value(required)
        return self.value(merger.settings)


class ExpandIterable(SettingReference):
    """Allow to import an existing list inside a list setting.
    in `defaults.py`:

    >>> LIST_1 = [0, ]
    >>> LIST_2 = [1, ExpandIterable('LIST_1'), 2, ]
    >>> DICT_1 = {0: 0, }
    >>> DICT_2 = {1: 1, None: ExpandIterable('DICT_1'), 2: 2, }

    In case of dict, the key is ignored when the referenced dict is expanded.
    In `local_settings.py`

    >>> LIST_1 = [3, ]
    >>> DICT_1 = {3: 3, }

    In your code:

    >>> from django.conf import settings

    Then `settings.LIST_2` is equal to `[1, 3, 2]`.
    `settings.DICT_2` is equal to `{1: 1, 2: 2, 3: 3, }`.

    """
