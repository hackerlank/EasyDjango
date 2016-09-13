# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os

from easydjango.conf.py_values import Path, AutocreateDirectory

__author__ = 'Matthieu Gallet'
INSTALLED_APPS = ['easydjango', ]
SECRET_KEY = 'secret_key'

LOCAL_PATH = './django_data'
split_path = __file__.split(os.path.sep)
if 'lib' in split_path:
    prefix = os.path.join(*split_path[:split_path.index('lib')])
    LOCAL_PATH = AutocreateDirectory('/%s/var/{PROJECT_NAME}' % prefix)
DATA_PATH = AutocreateDirectory('{LOCAL_PATH}/data')

DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASE_ENGINE_HELP = "SQL database engine, can be 'django.db.backends.[postgresql_psycopg2|mysql|sqlite3|oracle]'."
DATABASE_NAME = Path('{DATA_PATH}/database.sqlite3')
DATABASE_NAME_HELP = 'Name of your database, or path to database file if using sqlite3.'
DATABASE_USER = ''
DATABASE_USER_HELP = 'Database user (not used with sqlite3)'
DATABASE_PASSWORD = ''
DATABASE_PASSWORD_HELP = 'Database password (not used with sqlite3)'
DATABASE_HOST = ''
DATABASE_HOST_HELP = 'Empty for localhost through domain sockets or "127.0.0.1" for localhost + TCP'
DATABASE_PORT = ''
DATABASE_PORT_HELP = 'Database port, leave it empty for default (not used with sqlite3)'
DATABASES = {
    'default': {
        'ENGINE': '{DATABASE_ENGINE}',
        'NAME': '{DATABASE_NAME}',
        # The following settings are not used with sqlite3:
        'USER': '{DATABASE_USER}',
        'PASSWORD': '{DATABASE_PASSWORD}',
        'HOST': '{DATABASE_HOST}',
        'PORT': '{DATABASE_PORT}',
    },
}
DATABASES_HELP = 'A dictionary containing the settings for all databases to be used with Django.'
