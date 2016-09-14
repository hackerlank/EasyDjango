# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os

from easydjango.conf.py_values import Path, AutocreateDirectory, SettingReference, ExpandIterable

__author__ = 'Matthieu Gallet'
try:
    import ws4redis
    USE_WS4REDIS = True
except ImportError:
    ws4redis = None
    USE_WS4REDIS = False
try:
    # noinspection PyUnresolvedReferences
    import dango_redis
    USE_DJANGO_REDIS = True
except ImportError:
    django_redis = None
    USE_DJANGO_REDIS = False
# ######################################################################################################################
# settings that can be kept as-is
# of course, you can override them in your default settings
# ######################################################################################################################
ADMINS = (('admin', '{ADMIN_EMAIL}',),)
ALLOWED_HOSTS = ['{SERVER_FQDN}']
if USE_DJANGO_REDIS:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': '{CACHE_REDIS_PROTOCOL}://:{CACHE_REDIS_PASSWORD}@{CACHE_REDIS_SERVER}:{CACHE_REDIS_PORT}/'
                        '{CACHE_REDIS_DB}',
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}
        }
    }
else:
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'unique-snowflake'}, }
CSRF_COOKIE_DOMAIN = '.{SERVER_FQDN}'
DATABASES = {'default': {
    'ENGINE': '{DATABASE_ENGINE}', 'NAME': '{DATABASE_NAME}', 'USER': '{DATABASE_USER}',
    'OPTIONS': SettingReference('DATABASE_OPTIONS'),
    'PASSWORD': '{DATABASE_PASSWORD}', 'HOST': '{DATABASE_HOST}', 'PORT': '{DATABASE_PORT}'},
}
DATA_PATH = AutocreateDirectory('{LOCAL_PATH}/data')
DEBUG = False
# you should create a "local_config.py" with "DEBUG = True" at the root of your project
DEFAULT_FROM_EMAIL = 'webmaster@{SERVER_FQDN}'
FILE_UPLOAD_TEMP_DIR = AutocreateDirectory('{LOCAL_PATH}/tmp-uploads')
INSTALLED_APPS = [
    ExpandIterable('EASYDJANGO_INSTALLED_APPS'),
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'debug_toolbar',
    'easydjango',
]  # TODO
if USE_WS4REDIS:
    INSTALLED_APPS.append('ws4redis')
LOGGING = {}  # TODO
MANAGERS = SettingReference('ADMINS')
MEDIA_ROOT = AutocreateDirectory('{LOCAL_PATH}/media')
MEDIA_URL = '/media/'
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    ExpandIterable('EASYDJANGO_MIDDLEWARE_CLASSES'),
)

ROOT_URLCONF = 'easydjango.root_urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', 'APP_DIRS': True,
        'DIRS': SettingReference('TEMPLATE_DIRS'),
        'OPTIONS': {'context_processors': SettingReference('TEMPLATE_CONTEXT_PROCESSORS'),
                    'loaders': SettingReference('TEMPLATE_LOADERS')},
    },
]
SERVER_EMAIL = 'root@{SERVER_FQDN}'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # X-Forwarded-Proto
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
TEMPLATE_DIRS = ()
TEMPLATE_CONTEXT_PROCESSORS = ['django.contrib.auth.context_processors.auth',
                               'django.template.context_processors.debug',
                               'django.template.context_processors.i18n',
                               'django.template.context_processors.media',
                               'django.template.context_processors.static',
                               'django.template.context_processors.tz',
                               'django.contrib.messages.context_processors.messages',
                               ExpandIterable('EASYDJANGO_TEMPLATE_CONTEXT_PROCESSORS')]
if USE_WS4REDIS:
    TEMPLATE_CONTEXT_PROCESSORS.append('ws4redis.context_processors.default')
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader')
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True
USE_X_FORWARDED_FOR = True  # X-Forwarded-For
USE_X_FORWARDED_HOST = True  # X-Forwarded-Host
USE_HTTP_BASIC_AUTH = True  # HTTP-Authorization
WSGI_APPLICATION = 'easydjango.wsgi.application'
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SITE_ID = 1
STATIC_ROOT = AutocreateDirectory('{LOCAL_PATH}/static')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder')
WEBSOCKET_URL = '/ws/'
WS4REDIS_CONNECTION = {
    'host': '{WS4REDIS_SERVER}',
    'port': SettingReference('WS4REDIS_PORT'),
    'db': SettingReference('WS4REDIS_DB'),
    'password': '{WS4REDIS_PASSWORD}',
}
WS4REDIS_PREFIX = 'ws'
WS4REDIS_SUBSCRIBER = 'myapp.redis_store.RedisSubscriber'

# ######################################################################################################################
# settings that should be customized for each project
# of course, you can define or override any setting
# ######################################################################################################################

EASYDJANGO_URL_CONF = '{PROJECT_NAME}.urls'
EASYDJANGO_INDEX = 'easydjango.views.index'
EASYDJANGO_INSTALLED_APPS = []
EASYDJANGO_MIDDLEWARE_CLASSES = []
EASYDJANGO_REMOTE_USER_HEADER = None  # Remote-User
EASYDJANGO_TEMPLATE_CONTEXT_PROCESSORS = []
WS4REDIS_EXPIRE = 7200
# ######################################################################################################################
# settings that should be customized for each deployment
# {PROJECT_NAME}.iniconf:INI_MAPPING should be a list of ConfigField, allowing to define these settings in a .ini file
# ######################################################################################################################
ADMIN_EMAIL = 'admin@{SERVER_FQDN}'
DATABASE_ENGINE = 'django.db.backends.sqlite3'
DATABASE_NAME = Path('{DATA_PATH}/database.sqlite3')
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''
DATABASE_OPTIONS = {}
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_SUBJECT_PREFIX = '{SERVER_FQDN}'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
LANGUAGE_CODE = 'fr-fr'
LOCAL_PATH = './django_data'

__split_path = __file__.split(os.path.sep)
if 'lib' in __split_path:
    prefix = os.path.join(*__split_path[:__split_path.index('lib')])
    LOCAL_PATH = AutocreateDirectory('/%s/var/{PROJECT_NAME}' % prefix)
SECRET_KEY = 'secret_key'
SECURE_HSTS_SECONDS = 0
SERVER_FQDN = 'localhost'
TIME_ZONE = 'Europe/Paris'

WS4REDIS_SERVER = 'localhost'
WS4REDIS_PORT = 6379
WS4REDIS_DB = 11
WS4REDIS_PASSWORD = ''

CACHE_REDIS_PROTOCOL = 'redis'
CACHE_REDIS_SERVER = 'localhost'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_DB = 10
CACHE_REDIS_PASSWORD = ''
