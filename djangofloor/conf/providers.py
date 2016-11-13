# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import hashlib
import os
import sys
from collections import OrderedDict

from django.utils.six import StringIO

from djangofloor.conf.fields import ConfigField
from djangofloor.utils import import_module

try:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from configparser import ConfigParser
except ImportError:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from ConfigParser import ConfigParser

__author__ = 'Matthieu Gallet'


class ConfigProvider(object):
    name = None

    def has_value(self, config_field):
        raise NotImplementedError

    def set_value(self, config_field):
        raise NotImplementedError

    def get_value(self, config_field):
        raise NotImplementedError

    def get_extra_settings(self):
        """
        :return an iterable of (setting_name, value)"""
        raise NotImplementedError

    def is_valid(self):
        raise NotImplementedError

    def to_str(self):
        raise NotImplementedError


class IniConfigProvider(ConfigProvider):
    name = '.ini file'

    def __init__(self, config_file=None):
        self.parser = ConfigParser()
        self.config_file = config_file
        if config_file:
            self.parser.read([config_file])

    def __str__(self):
        return self.config_file

    @staticmethod
    def __get_info(config_field):
        assert isinstance(config_field, ConfigField)
        section, sep, option = config_field.name.partition('.')
        return section, option

    def set_value(self, config_field):
        section, option = self.__get_info(config_field)
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, option, config_field.to_str(config_field.value))

    def get_value(self, config_field):
        section, option = self.__get_info(config_field)
        if self.parser.has_option(section=section, option=option):
            str_value = self.parser.get(section=section, option=option)
            return config_field.from_str(str_value)
        return config_field.value

    def has_value(self, config_field):
        section, option = self.__get_info(config_field)
        return self.parser.has_option(section=section, option=option)

    def get_extra_settings(self):
        return []

    def is_valid(self):
        return os.path.isfile(self.config_file)

    def to_str(self):
        fd = StringIO()
        self.parser.write(fd)
        return fd.getvalue()


class PythonModuleProvider(ConfigProvider):
    name = 'Python module'

    def __init__(self, module_name=None):
        self.module_name = module_name
        self.module = None
        self.values = OrderedDict()
        if module_name is not None:
            try:
                self.module = import_module(module_name, package=None)
            except ImportError:
                pass

    def __str__(self):
        return self.module_name

    def set_value(self, config_field):
        self.values[config_field.setting_name] = config_field.value

    def get_value(self, config_field):
        if self.module is None or not hasattr(self.module, config_field.name):
            return config_field.value
        return getattr(self.module, config_field.name)

    def has_value(self, config_field):
        return self.module is not None and hasattr(self.module, config_field.name)

    def get_extra_settings(self):
        if self.module is not None:
            for key, value in self.module.__dict__.items():
                if key.upper() != key or key.endswith('_HELP'):
                    continue
                yield key, value

    def is_valid(self):
        return bool(self.module)

    def to_str(self):
        fd = StringIO()
        fd.write('# -*- coding: utf-8 -*-\n')
        for k, v in self.values.items():
            fd.write('%s = %r\n' % (k, v))
        return fd.getvalue()


class PythonFileProvider(PythonModuleProvider):
    name = 'Python file'

    def __init__(self, module_filename):
        self.module_filename = module_filename
        super(PythonFileProvider, self).__init__()
        if not os.path.isfile(module_filename):
            return
        version = tuple(sys.version_info[0:1])
        md5 = hashlib.md5(module_filename.encode('utf-8')).hexdigest()
        module_name = "easydjango.__private" + md5
        if version >= (3, 5):
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, module_filename)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        elif version >= (3, 2):
            # noinspection PyCompatibility
            from importlib.machinery import SourceFileLoader
            module = SourceFileLoader(module_name, module_filename).load_module()
        else:
            # noinspection PyDeprecation
            import imp
            # noinspection PyDeprecation
            module = imp.load_source(module_name, module_filename)
        self.module = module

    def __str__(self):
        return self.module_filename


class DictProvider(ConfigProvider):
    name = 'dict'

    def __init__(self, values):
        self.values = values

    def get_extra_settings(self):
        for k, v in self.values.items():
            yield k, v

    def set_value(self, config_field):
        self.values[config_field.setting_name] = config_field.value

    def get_value(self, config_field):
        return self.values.get(config_field.setting_name, config_field.value)

    def has_value(self, config_field):
        return config_field.setting_name in self.values

    def __str__(self):
        return '%r' % self.values

    def is_valid(self):
        return True

    def to_str(self):
        return '%r' % self.values


class ConfigFieldsProvider(object):
    name = None

    def get_config_fields(self):
        raise NotImplementedError


class PythonConfigFieldsProvider(ConfigFieldsProvider):
    name = 'Python attribute'

    def __init__(self, value=None):
        if value is None:
            module_name, attribute_name = None, None
        else:
            module_name, sep, attribute_name = value.partition(':')
        self.module_name = module_name
        self.attribute_name = attribute_name
        self.module = None
        if module_name is not None:
            try:
                self.module = import_module(module_name, package=None)
            except ImportError:
                pass

    def get_config_fields(self):
        if self.module:
            return getattr(self.module, self.attribute_name)
        return []

    def __str__(self):
        return '%s:%s' % (self.module_name, self.attribute_name)
