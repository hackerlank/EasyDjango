# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os

from easydjango.conf.config_values import Path, AutocreateDirectory, SettingReference, ExpandIterable
from easydjango.utils import is_package_present

__author__ = 'Matthieu Gallet'

# ######################################################################################################################
#
# detect if some external packages are available, to automatically customize some settings
#
# ######################################################################################################################
USE_DJANGO_REDIS = is_package_present('dango_redis')
USE_CELERY = is_package_present('celery')
USE_SCSS = is_package_present('scss')
USE_PIPELINE = is_package_present('pipeline')
USE_DEBUG_TOOLBAR = is_package_present('debug_toolbar')

# ######################################################################################################################
#
# settings that can be kept as-is
# of course, you can override them in your default settings
#
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
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'unique-snowflake'}}
CSRF_COOKIE_DOMAIN = '.{SERVER_FQDN}'
DATABASES = {'default': {
    'ENGINE': '{DATABASE_ENGINE}', 'NAME': '{DATABASE_NAME}', 'USER': '{DATABASE_USER}',
    'OPTIONS': SettingReference('DATABASE_OPTIONS'),
    'PASSWORD': '{DATABASE_PASSWORD}', 'HOST': '{DATABASE_HOST}', 'PORT': '{DATABASE_PORT}'},
}
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
]
if USE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
if USE_PIPELINE:
    INSTALLED_APPS.append('pipeline')
INSTALLED_APPS.append('easydjango')
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
    'easydjango.middleware.EasyDjangoMiddleware',
    ExpandIterable('EASYDJANGO_MIDDLEWARE_CLASSES'),
)

ROOT_URLCONF = 'easydjango.root_urls'
SERVER_EMAIL = 'root@{SERVER_FQDN}'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # X-Forwarded-Proto
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': SettingReference('TEMPLATE_DIRS'),
        'OPTIONS': {'context_processors': SettingReference('TEMPLATE_CONTEXT_PROCESSORS'),
                    'loaders': SettingReference('TEMPLATE_LOADERS')},
    },
]
TEMPLATE_DIRS = ()
TEMPLATE_CONTEXT_PROCESSORS = ['django.contrib.auth.context_processors.auth',
                               'django.template.context_processors.debug',
                               'django.template.context_processors.i18n',
                               'django.template.context_processors.media',
                               'django.template.context_processors.static',
                               'django.template.context_processors.tz',
                               'django.contrib.messages.context_processors.messages',
                               ExpandIterable('EASYDJANGO_TEMPLATE_CONTEXT_PROCESSORS'),
                               'easydjango.context_processors.context_base', ]
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader')
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True
USE_X_FORWARDED_HOST = True  # X-Forwarded-Host
WSGI_APPLICATION = 'easydjango.wsgi.application'

# django.contrib.auth
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

# django.contrib.sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# django.contrib.sites
SITE_ID = 1

# django.contrib.staticfiles
STATIC_ROOT = AutocreateDirectory('{LOCAL_PATH}/static')
STATIC_URL = '/static/'
if USE_PIPELINE:
    STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATICFILES_FINDERS = ['django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder']
if USE_PIPELINE:
    STATICFILES_FINDERS.append('pipeline.finders.PipelineFinder')

# celery
BROKER_URL = '{CELERY_PROTOCOL}://{CELERY_SERVER}:{CELERY_PORT}/{CELERY_DB}'
CELERY_TIMEZONE = '{TIME_ZONE}'
CELERY_RESULT_EXCHANGE = '{PROJECT_NAME}_results'
CELERY_ACCEPT_CONTENT = ['json', 'yaml', 'msgpack']
CELERY_APP = 'easydjango'
CELERY_CREATE_DIRS = True
CELERY_TASK_SERIALIZER = 'json'

# django-npm
NPM_EXECUTABLE_PATH = 'npm'
NPM_ROOT_PATH = AutocreateDirectory('{LOCAL_PATH}/npm')
NPM_STATIC_FILES_PREFIX = 'vendor'

# easydjango
DATA_PATH = AutocreateDirectory('{LOCAL_PATH}/data')
USE_HTTP_BASIC_AUTH = True  # HTTP-Authorization
USE_X_FORWARDED_FOR = True  # X-Forwarded-For

# ws4redis
WEBSOCKET_URL = '/ws/'
WS4REDIS_CONNECTION = {'host': '{WS4REDIS_SERVER}', 'port': SettingReference('WS4REDIS_PORT'),
                       'db': SettingReference('WS4REDIS_DB'), 'password': '{WS4REDIS_PASSWORD}'}
WS4REDIS_TOPIC_SERIALIZER = 'django.core.serializers.json.DjangoJSONEncoder'
WS4REDIS_HEARTBEAT = '--HEARTBEAT--'
WS4REDIS_SIGNAL_DECODER = 'json.JSONDecoder'
WS4REDIS_SIGNAL_ENCODER = 'easydjango.websockets.topics.serialize_topic'
WS4REDIS_PREFIX = 'ws'
WS4REDIS_EXPIRE = 36000
# django-pipeline
PIPELINE = {
    'PIPELINE_ENABLED': SettingReference('PIPELINE_ENABLED'),
    'JAVASCRIPT': SettingReference('PIPELINE_JS'),
    'STYLESHEETS': SettingReference('PIPELINE_CSS'),
    'CSS_COMPRESSOR': SettingReference('PIPELINE_CSS_COMPRESSOR'),
    'JS_COMPRESSOR': SettingReference('PIPELINE_JS_COMPRESSOR'),
}
PIPELINE_CSS = {
    'bootstrap3': {
        'source_filenames': ['vendor/bootstrap3/dist/css/bootstrap.min.css',
                             'vendor/bootstrap3/dist/css/bootstrap-theme.min.css',
                             'vendor/font-awesome/css/font-awesome.min.css',
                             'css/easydjango-bootstrap3.css', ExpandIterable('EASYDJANGO_CSS')],
        'output_filename': 'css/bootstrap3-all.css', 'extra_context': {'media': 'all'},
    },
    'metro-ui': {
        'source_filenames': ['vendor/metro-ui/build/css/metro.min.css',
                             'vendor/metro-ui/build/css/metro-icons.min.css',
                             'vendor/metro-ui/build/css/metro-responsive.min.css',
                             'vendor/font-awesome/css/font-awesome.min.css',
                             'css/easydjango-metro-ui.css', ExpandIterable('EASYDJANGO_CSS')],
        'output_filename': 'css/metro-ui-all.css', 'extra_context': {'media': 'all'},
    },
}
PIPELINE_JS = {
    'bootstrap3': {
        'source_filenames': ['vendor/jquery/dist/jquery.min.js', 'vendor/bootstrap3/dist/js/bootstrap.min.js',
                             'js/easydjango.js', 'js/easydjango-bootstrap3.js', ExpandIterable('EASYDJANGO_JS')],
        'output_filename': 'js/bootstrap3.js',
    },
    'metro-ui': {
        'source_filenames': ['vendor/jquery/dist/jquery.min.js', 'vendor/metro-ui/build/js/metro.min.js',
                             'js/easydjango.js', 'js/easydjango-metro-ui.js', ExpandIterable('EASYDJANGO_JS')],
        'output_filename': 'js/metro-ui.js',
    },
    'ie9': {
        'source_filenames': ['vendor/html5shiv/dist/html5shiv.min.js', 'vendor/respond.js/dest/respond.min.js', ],
        'output_filename': 'js/ie9.js',
    }
}
PIPELINE_ENABLED = True
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
if USE_SCSS:
    PIPELINE_COMPILERS = ('djangofloor.middleware.PyScssCompiler', )

# ######################################################################################################################
#
# settings that should be customized for each project
# of course, you can define or override any setting
#
# ######################################################################################################################
# easydjango
EASYDJANGO_URL_CONF = '{PROJECT_NAME}.urls.urlpatterns'
EASYDJANGO_INDEX = '{PROJECT_NAME}.views.index'
EASYDJANGO_INSTALLED_APPS = ['{PROJECT_NAME}']
EASYDJANGO_MIDDLEWARE_CLASSES = []
EASYDJANGO_REMOTE_USER_HEADER = None  # Remote-User
EASYDJANGO_TEMPLATE_CONTEXT_PROCESSORS = []
EASYDJANGO_CSS = []
EASYDJANGO_JS = []
EASYDJANGO_TEMPLATE_BASE = 'metro-ui'  # or "bootstrap3". Unused if you use your own templates

# django-npm
NPM_FILE_PATTERNS = {
    'metro-ui': ['build/*'], 'bootstrap3': ['dist/*'], 'font-awesome': ['css/*', 'fonts/*'],
    'html5shiv': ['dist/*'], 'respond.js': ['dest/*'], 'jquery': ['dist/*'],
}

# ws4redis
WS4REDIS_EXPIRE = 7200

# ######################################################################################################################
#
# settings that should be customized for each deployment
# {PROJECT_NAME}.iniconf:INI_MAPPING should be a list of ConfigField, allowing to define these settings in a .ini file
#
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
SECRET_KEY = 'secret_key'
SECURE_HSTS_SECONDS = 0
TIME_ZONE = 'Europe/Paris'

# easydjango
LISTEN_ADDRESS = 'localhost:9000'
LOCAL_PATH = './django_data'
__split_path = __file__.split(os.path.sep)
if 'lib' in __split_path:
    prefix = os.path.join(*__split_path[:__split_path.index('lib')])
    LOCAL_PATH = AutocreateDirectory('/%s/var/{PROJECT_NAME}' % prefix)
SERVER_FQDN = 'localhost'

# django_redis
CACHE_REDIS_PROTOCOL = 'redis'
CACHE_REDIS_SERVER = 'localhost'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_DB = 10
CACHE_REDIS_PASSWORD = ''

# ws4redis
WS4REDIS_SERVER = 'localhost'
WS4REDIS_PORT = 6379
WS4REDIS_DB = 11
WS4REDIS_PASSWORD = ''

# celery
CELERY_PROTOCOL = 'redis'
CELERY_DB = 13
CELERY_SERVER = 'localhost'
CELERY_PORT = 6379
CELERY_PASSWORD = ''
