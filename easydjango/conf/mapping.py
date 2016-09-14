# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from easydjango.conf.fields import CharConfigField, IntegerConfigField, BooleanConfigField

__author__ = 'Matthieu Gallet'

INI_MAPPING = [
    BooleanConfigField('global.debug', 'DEBUG'),
    CharConfigField('database.name', 'DATABASE_NAME'),
    CharConfigField('database.engine', 'DATABASE_ENGINE'),
    CharConfigField('database.user', 'DATABASE_USER'),
    IntegerConfigField('database.port', 'DATABASE_PORT'),
    CharConfigField('database.password', 'DATABASE_PASSWORD'),
    CharConfigField('database.host', 'DATABASE_HOST'),

]
