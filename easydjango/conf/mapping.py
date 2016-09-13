# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from easydjango.conf.fields import CharConfigField, IntegerConfigField

__author__ = 'Matthieu Gallet'

INI_MAPPING = [
    CharConfigField('database.name', 'DATABASE_NAME'),
    CharConfigField('database.engine', 'DATABASE_ENGINE'),
    CharConfigField('database.user', 'DATABASE_USER'),
    IntegerConfigField('database.port', 'DATABASE_PORT'),
    CharConfigField('database.password', 'DATABASE_PASSWORD'),
    CharConfigField('database.host', 'DATABASE_HOST'),
]
