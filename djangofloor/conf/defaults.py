# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os

from djangofloor.conf.config_values import Path, AutocreateDirectory, SettingReference, ExpandIterable, CallableSetting
from djangofloor.utils import is_package_present, guess_version
from djangofloor.log import generate_log_configuration
# noinspection PyUnresolvedReferences
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.translation import ugettext_lazy as _

__author__ = 'Matthieu Gallet'

# ######################################################################################################################
#
# detect if some external packages are available, to automatically customize some settings
#
# ######################################################################################################################
try:
    import django_redis  # does not work with is_package_present (???)

    USE_DJANGO_REDIS = True
except ImportError:
    django_redis = None
    USE_DJANGO_REDIS = False
USE_CELERY = is_package_present('celery')
USE_DJANGO_REDIS_SESSION = is_package_present('redis_sessions')
USE_SCSS = is_package_present('scss')
USE_PIPELINE = is_package_present('pipeline')
USE_DEBUG_TOOLBAR = is_package_present('debug_toolbar')
USE_REST_FRAMEWORK = is_package_present('rest_framework')
USE_ALLAUTH = is_package_present('allauth')

# ######################################################################################################################
#
# settings that can be kept as-is
# of course, you can override them in your default settings
#
# ######################################################################################################################
ADMINS = (('admin', '{ADMIN_EMAIL}',),)
ALLOWED_HOSTS = ['{SERVER_NAME}', '127.0.0.1', '::1']
if USE_DJANGO_REDIS:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': '{CACHE_REDIS_PROTOCOL}://:{CACHE_REDIS_PASSWORD}@{CACHE_REDIS_HOST}:{CACHE_REDIS_PORT}/'
                        '{CACHE_REDIS_DB}',
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}
        }
    }
else:
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'unique-snowflake'}}
CSRF_COOKIE_DOMAIN = '.{SERVER_NAME}'
DATABASES = {'default': {
    'ENGINE': '{DATABASE_ENGINE}', 'NAME': '{DATABASE_NAME}', 'USER': '{DATABASE_USER}',
    'OPTIONS': SettingReference('DATABASE_OPTIONS'),
    'PASSWORD': '{DATABASE_PASSWORD}', 'HOST': '{DATABASE_HOST}', 'PORT': '{DATABASE_PORT}'},
}
DEBUG = False
# you should create a "local_config.py" with "DEBUG = True" at the root of your project
DEFAULT_FROM_EMAIL = 'webmaster@{SERVER_NAME}'
FILE_UPLOAD_TEMP_DIR = AutocreateDirectory('{LOCAL_PATH}/tmp-uploads')
INSTALLED_APPS = [
    ExpandIterable('DF_INSTALLED_APPS'),
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'bootstrap3',
]
if USE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
if USE_PIPELINE:
    INSTALLED_APPS.append('pipeline')
if USE_REST_FRAMEWORK:
    INSTALLED_APPS.append('rest_framework')
INSTALLED_APPS.append('djangofloor')
LOGGING = CallableSetting(lambda x:
                          generate_log_configuration(log_directory=x['LOG_DIRECTORY'], project_name=x['PROJECT_NAME'],
                                                     script_name=x['SCRIPT_NAME'], debug=x['DEBUG']),
                          'DEBUG', 'PROJECT_NAME', 'SCRIPT_NAME', 'LOG_DIRECTORY')
MANAGERS = SettingReference('ADMINS')
MEDIA_ROOT = AutocreateDirectory('{LOCAL_PATH}/media')
MEDIA_URL = '/media/'
MIDDLEWARE_CLASSES = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'djangofloor.middleware.DjangoFloorMiddleware',
    ExpandIterable('DF_MIDDLEWARE_CLASSES'),
    'django.middleware.cache.FetchFromCacheMiddleware',
]
if USE_DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES.insert(-3, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'djangofloor.root_urls'
SERVER_EMAIL = 'root@{SERVER_NAME}'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # X-Forwarded-Proto or None
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
TEMPLATE_DEBUG = False  # SettingReference('DEBUG')
TEMPLATE_DIRS = ()
TEMPLATE_CONTEXT_PROCESSORS = ['django.contrib.auth.context_processors.auth',
                               'django.template.context_processors.debug',
                               'django.template.context_processors.i18n',
                               'django.template.context_processors.media',
                               'django.template.context_processors.static',
                               'django.template.context_processors.tz',
                               'django.contrib.messages.context_processors.messages',
                               ExpandIterable('DF_TEMPLATE_CONTEXT_PROCESSORS'),
                               'djangofloor.context_processors.context_base', ]
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader')
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True
USE_X_FORWARDED_HOST = True  # X-Forwarded-Host
X_FRAME_OPTIONS = 'SAMEORIGIN'
WSGI_APPLICATION = 'djangofloor.wsgi.django_application'

# django.contrib.auth
AUTHENTICATION_BACKENDS = (
    'djangofloor.backends.DefaultGroupsRemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',)

# django.contrib.sessions
if USE_DJANGO_REDIS_SESSION:
    SESSION_ENGINE = 'redis_sessions.session'

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
BROKER_URL = '{CELERY_PROTOCOL}://{CELERY_HOST}:{CELERY_PORT}/{CELERY_DB}'
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_TIMEZONE = '{TIME_ZONE}'
CELERY_RESULT_EXCHANGE = '{PROJECT_NAME}_results'
CELERY_ACCEPT_CONTENT = ['json', 'yaml', 'msgpack']
CELERY_APP = 'djangofloor'
CELERY_CREATE_DIRS = True
CELERY_TASK_SERIALIZER = 'json'

# django-npm
NPM_EXECUTABLE_PATH = 'npm'
NPM_ROOT_PATH = AutocreateDirectory('{LOCAL_PATH}/npm')
NPM_STATIC_FILES_PREFIX = 'vendor'

# django-rest-framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# djangofloor
DATA_PATH = AutocreateDirectory('{LOCAL_PATH}/data')
SERVER_NAME = CallableSetting(lambda x: urlparse(x['SERVER_BASE_URL']).hostname, 'SERVER_BASE_URL')  # ~ www.example.org
SERVER_PORT = CallableSetting(lambda x: urlparse(x['SERVER_BASE_URL']).port or (USE_SSL and 443) or 80,
                              'SERVER_BASE_URL', 'USE_SSL')  # ~ 443
SERVER_PROTOCOL = CallableSetting(lambda x: 'https' if x['USE_SSL'] else 'http', 'USE_SSL')  # ~ "https"


def url_prefix(values):
    p = urlparse(values['SERVER_BASE_URL']).path
    if not p.endswith('/'):
        p += '/'
    return p


URL_PREFIX = CallableSetting(url_prefix, 'SERVER_BASE_URL')  # ~ /prefix/
USE_HTTP_BASIC_AUTH = True  # HTTP-Authorization
USE_SSL = CallableSetting(lambda x: urlparse(x['SERVER_BASE_URL']).scheme == 'https', 'SERVER_BASE_URL')  # ~ True
USE_X_FORWARDED_FOR = True  # X-Forwarded-For
USE_X_SEND_FILE = False  # Apache module
X_ACCEL_REDIRECT = []  # paths used by nginx
DF_SYSTEM_CHECKS = ['djangofloor.views.monitoring.RequestCheck',
                    'djangofloor.views.monitoring.System',
                    'djangofloor.views.monitoring.CeleryStats',
                    'djangofloor.views.monitoring.Packages', ]
WINDOW_INFO_MIDDLEWARES = [
    'djangofloor.middleware.WindowKeyMiddleware',
    'djangofloor.middleware.DjangoAuthMiddleware',
    'djangofloor.middleware.Djangoi18nMiddleware', ]
COMMON_COMMANDS = {
    'queue-events': ('celery', 'events'),
    'purge-queue': ('celery', 'purge'),
    'queue-status': ('celery', 'status'),
    'worker': ('celery', 'worker'),
    'staticfiles': ('django', 'collectstatic'),
    'changepassword': ('django', 'changepassword'),
    'check': ('django', 'check'),
    'config': ('django', 'config'),
    'createsuperuser': ('django', 'createsuperuser'),
    'dbshell': ('django', 'dbshell'),
    'dumpdata': ('django', 'dumpdata'),
    'loaddata': ('django', 'loaddata'),
    'migrate': ('django', 'migrate'),
    'server-dev': ('django', 'runserver'),
    'sendtestemail': ('django', 'sendtestemail'),
    'shell': ('django', 'shell'),
    'server-gunicorn': ('gunicorn', ''),
    'server-uwsgi': ('uwsgi', ''),
}
# COMMON_COMMANDS["command_name"] = ("django", "command")
# COMMON_COMMANDS["other_command_name"] = ("celery", "other_command")

# ws4redis
WEBSOCKET_URL = '/ws/'
WS4REDIS_CONNECTION = {'host': '{WS4REDIS_HOST}', 'port': SettingReference('WS4REDIS_PORT'),
                       'db': SettingReference('WS4REDIS_DB'), 'password': '{WS4REDIS_PASSWORD}'}
WS4REDIS_TOPIC_SERIALIZER = 'djangofloor.websockets.topics.serialize_topic'
WS4REDIS_HEARTBEAT = '--HEARTBEAT--'
WS4REDIS_SIGNAL_DECODER = 'json.JSONDecoder'
WS4REDIS_SIGNAL_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'
WS4REDIS_PREFIX = 'ws'
WS4REDIS_THREAD_COUNT = 2

# django-pipeline
PIPELINE = {
    'PIPELINE_ENABLED': SettingReference('PIPELINE_ENABLED'),
    'JAVASCRIPT': SettingReference('PIPELINE_JS'),
    'STYLESHEETS': SettingReference('PIPELINE_CSS'),
    'CSS_COMPRESSOR': SettingReference('PIPELINE_CSS_COMPRESSOR'),
    'JS_COMPRESSOR': SettingReference('PIPELINE_JS_COMPRESSOR'),
}
PIPELINE_CSS = {
    'default': {
        'source_filenames': SettingReference('DF_CSS'),
        'output_filename': 'css/default-all.css', 'extra_context': {'media': 'all'},
    },
    'bootstrap3': {
        'source_filenames': ['vendor/bootstrap3/dist/css/bootstrap.min.css',
                             'vendor/bootstrap3/dist/css/bootstrap-theme.min.css',
                             'vendor/font-awesome/css/font-awesome.min.css',
                             'css/djangofloor-bootstrap3.css', ExpandIterable('DF_CSS')],
        'output_filename': 'css/bootstrap3-all.css', 'extra_context': {'media': 'all'},
    },
    'metro-ui': {
        'source_filenames': ['vendor/metro-ui/build/css/metro.min.css',
                             'vendor/metro-ui/build/css/metro-icons.min.css',
                             'vendor/metro-ui/build/css/metro-responsive.min.css',
                             'vendor/font-awesome/css/font-awesome.min.css',
                             'css/djangofloor-metro-ui.css', ExpandIterable('DF_CSS')],
        'output_filename': 'css/metro-ui-all.css', 'extra_context': {'media': 'all'},
    },
    'ie9': {
        'source_filenames': [],
        'output_filename': 'css/ie9.css', 'extra_context': {'media': 'all'},
    },
}
PIPELINE_MIMETYPES = (
    (b'text/coffeescript', '.coffee'),
    (b'text/less', '.less'),
    (b'text/javascript', '.js'),
    (b'text/x-sass', '.sass'),
    (b'text/x-scss', '.scss')
)
PIPELINE_JS = {
    'default': {
        'source_filenames': ['vendor/jquery/dist/jquery.min.js', 'js/djangofloor.js', ExpandIterable('DF_JS')],
        'output_filename': 'js/default.js',
    },
    'bootstrap3': {
        'source_filenames': ['vendor/jquery/dist/jquery.min.js', 'vendor/bootstrap3/dist/js/bootstrap.min.js',
                             'js/djangofloor.js', 'vendor/bootstrap-notify/bootstrap-notify.min.js',
                             'js/djangofloor-bootstrap3.js', ExpandIterable('DF_JS')],
        'output_filename': 'js/bootstrap3.js',
    },
    'metro-ui': {
        'source_filenames': ['vendor/jquery/dist/jquery.min.js', 'vendor/metro-ui/build/js/metro.min.js',
                             'js/djangofloor.js', 'js/djangofloor-metro-ui.js', ExpandIterable('DF_JS')],
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
    PIPELINE_COMPILERS = ('djangofloor.middleware.PyScssCompiler',)

# Django-Debug-Toolbar
DEBUG_TOOLBAR_CONFIG = {'JQUERY_URL': '{STATIC_URL}vendor/jquery/dist/jquery.min.js', }
DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ('127.0.0.1', '::1', )

# Django-Bootstrap3
BOOTSTRAP3 = {
    'jquery_url': '{STATIC_URL}vendor/jquery/dist/jquery.min.js',
    'base_url': '{STATIC_URL}vendor/bootstrap3/dist/',
    'theme_url': None, 'include_jquery': False, 'horizontal_label_class': 'col-md-3',
    'horizontal_field_class': 'col-md-9', 'set_disabled': True, 'set_placeholder': False,
    'formset_renderers': {'default': 'bootstrap3.renderers.FormsetRenderer'},
    'form_renderers': {'default': 'bootstrap3.renderers.FormRenderer'},
    'field_renderers': {'default': 'bootstrap3.renderers.FieldRenderer',
                        'inline': 'bootstrap3.renderers.InlineFieldRenderer'},
}

# ######################################################################################################################
#
# settings that should be customized for each project
# of course, you can redefine or override any setting
#
# ######################################################################################################################
# djangofloor
DF_CSS = SettingReference('FLOOR_EXTRA_CSS')
DF_JS = SettingReference('FLOOR_EXTRA_JS')
DF_INDEX_VIEW = 'djangofloor.views.index.IndexView'
DF_SITE_SEARCH_VIEW = 'djangofloor.views.search.UserSearchView'
DF_LOGIN_VIEW = 'djangofloor.views.auth.LoginView'

DF_URL_CONF = '{PROJECT_NAME}.urls.urlpatterns'
DF_INSTALLED_APPS = ['{PROJECT_NAME}']
DF_MIDDLEWARE_CLASSES = []
DF_REMOTE_USER_HEADER = None  # HTTP-REMOTE-USER
DF_FAKE_AUTHENTICATION_USERNAME = 'testuser'
DF_DEFAULT_GROUPS = [_('Users')]
DF_TEMPLATE_CONTEXT_PROCESSORS = []
DF_CHECKED_REQUIREMENTS = ['django>=1.12', 'django<=1.13', 'celery', 'django-bootstrap3', 'redis', 'pip',
                           'psutil', 'django-redis-sessions']
DF_PROJECT_VERSION = CallableSetting(guess_version)

# django-npm
NPM_FILE_PATTERNS = {
    'bootstrap-notify': ['*.js'],
    'bootstrap3': ['dist/*'],
    'font-awesome': ['css/*', 'fonts/*'],
    'html5shiv': ['dist/*'],
    'jquery': ['dist/*'],
    'jquery-file-upload': ['css/*', 'js/*'],
    'metro-ui': ['build/*'],
    'respond.js': ['dest/*'],
}

# ws4redis
WS4REDIS_EXPIRE = 36000
WS4REDIS_PUBLIC_WS_LIST = True
# do not check for each WS signal/function before sending its name to the client

# ######################################################################################################################
#
# settings that should be customized for each deployment
# {PROJECT_NAME}.iniconf:INI_MAPPING should be a list of ConfigField, allowing to define these settings in a .ini file
#
# ######################################################################################################################
ADMIN_EMAIL = 'admin@{SERVER_NAME}'
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
EMAIL_SUBJECT_PREFIX = '{SERVER_NAME}'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
LANGUAGE_CODE = 'fr-fr'
SECRET_KEY = 'secret_key'
SECURE_HSTS_SECONDS = 0
TIME_ZONE = 'Europe/Paris'

# djangofloor
LISTEN_ADDRESS = 'localhost:9000'
LOCAL_PATH = './django_data'
__split_path = __file__.split(os.path.sep)
if 'lib' in __split_path:
    prefix = os.path.join(*__split_path[:__split_path.index('lib')])
    LOCAL_PATH = AutocreateDirectory('/%s/var/{PROJECT_NAME}' % prefix)
SERVER_BASE_URL = 'http://localhost:9000/'
LOG_DIRECTORY = '{LOCAL_PATH}/logs'

# django_redis
CACHE_REDIS_PROTOCOL = 'redis'
CACHE_REDIS_HOST = 'localhost'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_DB = 2
CACHE_REDIS_PASSWORD = ''

# django-redis-sessions
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 3
SESSION_REDIS_PASSWORD = ''

# ws4redis
WS4REDIS_HOST = 'localhost'
WS4REDIS_PORT = 6379
WS4REDIS_DB = 11
WS4REDIS_PASSWORD = ''

# celery
CELERY_PROTOCOL = 'redis'
CELERY_DB = 13
CELERY_HOST = 'localhost'
CELERY_PORT = 6379
CELERY_PASSWORD = ''

UWSGI_PROCESSES = 3
UWSGI_THREADS = 20


# deprecated settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[{SERVER_NAME}] '
ACCOUNT_EMAIL_VERIFICATION = None
BIND_ADDRESS = SettingReference('LISTEN_ADDRESS')
FLOOR_AUTHENTICATION_HEADER = SettingReference('DF_REMOTE_USER_HEADER')
FLOOR_BACKUP_SINGLE_TRANSACTION = False
FLOOR_DEFAULT_GROUP_NAME = _('Users')
FLOOR_EXTRA_CSS = []
FLOOR_EXTRA_JS = []
FLOOR_FAKE_AUTHENTICATION_USERNAME = SettingReference('DF_FAKE_AUTHENTICATION_USERNAME')
FLOOR_INDEX = None
FLOOR_PROJECT_NAME = SettingReference('PROJECT_NAME')
FLOOR_PROJECT_VERSION = CallableSetting(guess_version)
FLOOR_SIGNAL_DECODER = SettingReference('WS4REDIS_SIGNAL_DECODER')
FLOOR_SIGNAL_ENCODER = SettingReference('WS4REDIS_SIGNAL_ENCODER')
FLOOR_URL_CONF = SettingReference('DF_URL_CONF')
FLOOR_USE_WS4REDIS = False
FLOOR_WS_FACILITY = 'djangofloor'
LOG_PATH = Path('{LOCAL_PATH}/log')
LOGOUT_URL = '/df/logout/'
MAX_REQUESTS = 10000
PROTOCOL = SettingReference('SERVER_PROTOCOL')
REDIS_HOST = SettingReference('CELERY_HOST')
REDIS_PORT = SettingReference('CELERY_PORT')
REVERSE_PROXY_IPS = ['127.0.0.1', ]
REVERSE_PROXY_PORT = None  #
REVERSE_PROXY_SSL_KEY_FILE = None
REVERSE_PROXY_SSL_CRT_FILE = None
REVERSE_PROXY_TIMEOUT = 300
THREADS = SettingReference('UWSGI_THREADS')
USE_SCSS = False
WORKERS = 1
WS4REDIS_EMULATION_INTERVAL = 0
WS4REDIS_SUBSCRIBER = 'djangofloor.df_ws4redis.Subscriber'
BROKER_DB = SettingReference('CELERY_DB')
