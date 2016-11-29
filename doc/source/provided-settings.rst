Provided settings
=================

DjangoFloor sets several settings used by Django (or third-party packages) and defines some new settings, specifically
used by DjangoFloor.

DjangoFloor also allows references between settings: for example, you only defines `SERVER_BASE_URL`
(like 'https://www.example.com/site/' ) and `SERVER_NAME` ('www.example.com'), `SERVER_PORT` ('443'),
`USE_SSL` ('True'), `SERVER_PROTOCOL` ('https') and `URL_PREFIX` ('/site/') are deduced.

These settings are defined in :mod:`djangofloor.conf.defaults`.
Settings that should be customized on each installation (like the server name or the database password) can be
 written in .ini files. The mapping between the Python setting and the [section/option] system is defined in
 :mod:`djangofloor.conf.mapping`.

Here is the list of settings defined by DjangoFloor with examples of values.

  * `ADMIN_EMAIL`, aliased to section "global", option "admin_email" (e.g. "admin@{SERVER_NAME}")
  * `LANGUAGE_CODE`, aliased to section "global", option "language_code" (e.g. "fr_FR")
  * `LISTEN_ADDRESS`, aliased to section "global", option "listen_address" (e.g. "localhost:9010")
  * `LOCAL_PATH`, aliased to section "global", option "data" (e.g. "/var/data/myproject", by default all data like logs, static files or media will be stored into subfolders of this folder)
  * `SECRET_KEY`, aliased to section "global", option "secret_key" (e.g. "dsjdqsjdqjd1838y0xuc1s9u0u")
  * `SERVER_BASE_URL`, aliased to section "global", option "server_url" (e.g. "https://www.myexample.org/" )
  * `TIME_ZONE`, aliased to section "global", option "time_zone" (e.g. "Europe/Paris")
  * `CACHE_REDIS_DB`, aliased to section "cache", option "db" (e.g. "12")
  * `CACHE_REDIS_HOST`, aliased to section "cache", option "host" (e.g. "localhost")
  * `CACHE_REDIS_PASSWORD`, aliased to section "cache", option "password" (e.g. "")
  * `CACHE_REDIS_PORT`, aliased to section "cache", option "port" (e.g. "6579")
  * `CELERY_DB`, aliased to section "celery", option "db" (e.g. "13")
  * `CELERY_HOST`, aliased to section "celery", option "host" (e.g. "localhost")
  * `CELERY_PASSWORD`, aliased to section "celery", option "password" (e.g. "")
  * `CELERY_PORT`, aliased to section "celery", option "port" (e.g. "6579")
  * `DATABASE_NAME`, aliased to section "database", option "db" (e.g. "myproject")
  * `DATABASE_ENGINE`, aliased to section "database", option "engine" (e.g. "mysql", "oracle", "postgresql", "sqlite3" or the standard, dotted, name of any database engine like "django.db.backends.postgresql_psycopg2")
  * `DATABASE_HOST`, aliased to section "database", option "host" (e.g. "localhost")
  * `DATABASE_PASSWORD`, aliased to section "database", option "password" (e.g. "toto")
  * `DATABASE_PORT`, aliased to section "database", option "port" (e.g. "5432")
  * `DATABASE_USER`, aliased to section "database", option "user" (e.g. "user")
  * `EMAIL_HOST`, aliased to section "email", option "host" (e.g. "localhost")
  * `EMAIL_HOST_PASSWORD`, aliased to section "email", option "password" (e.g. "toto")
  * `EMAIL_PORT`, aliased to section "email", option "port" (e.g. "465")
  * `EMAIL_HOST_USER`, aliased to section "email", option "user" (e.g. "user")
  * `EMAIL_USE_TLS`, aliased to section "email", option "use_tls" (e.g. "on")
  * `EMAIL_USE_SSL`, aliased to section "email", option "use_ssl" (e.g. "off")
  * `LOG_REMOTE_URL`, aliased to section "global", option "log_remote_url" (e.g. "syslog://localhost:514/daemon")
  * `SESSION_REDIS_DB`, aliased to section "session", option "db" (e.g. "14")
  * `SESSION_REDIS_HOST`, aliased to section "session", option "host" (e.g. "localhost")
  * `SESSION_REDIS_PASSWORD`, aliased to section "session", option "password" (e.g. "")
  * `SESSION_REDIS_PORT`, aliased to section "session", option "port" (e.g. "6579")
  * `WEBSOCKET_REDIS_DB`, aliased to section "websocket", option "db" (e.g. "15")
  * `WEBSOCKET_REDIS_HOST`, aliased to section "websocket", option "host" (e.g. "localhost")
  * `WEBSOCKET_REDIS_PASSWORD`, aliased to section "websocket", option "password" (e.g. "")
  * `WEBSOCKET_REDIS_PORT`, aliased to section "websocket", option "port" (e.g. "6579")

Some settings are defined mostly for internal use. You should have no reason to override them:

  * `DATA_PATH`: corresponds to database path (mainly for sqlite3),
  * `SERVER_NAME`: defined from `SERVER_BASE_URL` (e.g. 'www.example.com'),
  * `SERVER_PORT`: defined from `SERVER_BASE_URL` (e.g. '443'),
  * `SERVER_PROTOCOL`: defined from `SERVER_BASE_URL` (e.g. 'https'),
  * `URL_PREFIX`: defined from `SERVER_BASE_URL` (e.g. 'www.example.com'),
  * `USE_HTTP_BASIC_AUTH`: set to 'True' if you want to use HTTP Basic Auth with the Django auth framework,
  * `USE_SSL`: defined from `SERVER_BASE_URL` (e.g. 'True'),
  * `USE_X_SEND_FILE`: set to True if you use Apache and 'mod_auth_send_file',
  * `X_ACCEL_REDIRECT`: if you use nginx and x-accel-redirect, set a list of (),
  * `DF_FAKE_AUTHENTICATION_USERNAME`: you should set it in your local config file, for faking a HTTP automatic authentication,
  * `DF_PROJECT_VERSION`: set it to the version of your project. By default, read `yourproject/__init__.py` and check for something like '__version__ = '1.0.0',
  * `DF_PUBLIC_SIGNAL_LIST`: set to 'False' if you do not want to publish the whole list of available signals (but this takes some time on each web page),
  * `DF_SYSTEM_CHECKS`: list of check components for the monitoring view,
  * `WINDOW_INFO_MIDDLEWARES`: list of middlewares used for populating the WindowInfo object from the HttpRequest,
  * `WEBSOCKET_URL`: URL of the websocket view ("/ws/" by default),
  * `WEBSOCKET_REDIS_CONNECTION`: dict collecting all 'WEBSOCKET_REDIS_*' settings,
  * `WEBSOCKET_TOPIC_SERIALIZER`: applied on each topic to serialize it to a string (the default function can handle any Django model or Python object),
  * `WEBSOCKET_HEARTBEAT`: the default message when there is no activity on the websocket,
  * `WEBSOCKET_SIGNAL_DECODER`: JSON-decoder used to deserialize encoded signals,
  * `WEBSOCKET_SIGNAL_ENCODER`: JSON-encoder used to serialize signal data,
  * `WEBSOCKET_REDIS_PREFIX`: prefix used for storing websocket data in the Redis DB,
  * `WEBSOCKET_REDIS_EXPIRE`: stores in Redis the list of allowed topics for a given window key this number of seconds (set to a long value if people stay a long time on each webpage).

Finally, there are some settings that you probably want to override, prefixed by 'DF_'.


  * `DF_CSS`: list of CSS files to include (relative to the static path),
  * `DF_JS`: list of JS files to include (relative to the static path),
  * `DF_INDEX_VIEW`: dotted path of the class-based index view (corresponding to '/'),
  * `DF_SITE_SEARCH_VIEW`: dotted path of the class-based default search view,
  * `DF_LOGIN_VIEW`: dotted path of the class-based default login view,
  * `DF_URL_CONF`: list of url patterns,
  * `DF_INSTALLED_APPS`: list of extra installed apps,
  * `DF_MIDDLEWARE_CLASSES`: list of extra middlewares,
  * `DF_REMOTE_USER_HEADER`: the HTTP header used for HTTP authentication (can be set to None),
  * `DF_DEFAULT_GROUPS`: list of groups for new users (only for HTTP auth),
  * `DF_TEMPLATE_CONTEXT_PROCESSORS`: list of extra template context processors,
  * `DF_CHECKED_REQUIREMENTS`: list of Python requirements, checked on the monitoring view,
  * `NPM_FILE_PATTERNS`: used the same setting as 'django-npm' (allowing the 'npm' managing command for collecting JS files using the npm package manager).
