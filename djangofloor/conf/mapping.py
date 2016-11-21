# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from djangofloor.conf.fields import CharConfigField, IntegerConfigField, BooleanConfigField

__author__ = 'Matthieu Gallet'

INI_MAPPING = [
    CharConfigField('global.admin_email', 'ADMIN_EMAIL'),
    CharConfigField('global.data', 'LOCAL_PATH'),
    CharConfigField('global.language_code', 'LANGUAGE_CODE'),
    CharConfigField('global.listen_address', 'LISTEN_ADDRESS'),
    CharConfigField('global.secret_key', 'SECRET_KEY'),
    CharConfigField('global.server_url', 'SERVER_BASE_URL'),
    CharConfigField('global.time_zone', 'TIME_ZONE'),

    CharConfigField('database.db', 'DATABASE_NAME'),
    CharConfigField('database.engine', 'DATABASE_ENGINE'),
    CharConfigField('database.host', 'DATABASE_HOST'),
    CharConfigField('database.password', 'DATABASE_PASSWORD'),
    IntegerConfigField('database.port', 'DATABASE_PORT'),
    CharConfigField('database.user', 'DATABASE_USER'),

    IntegerConfigField('cache.db', 'CACHE_REDIS_DB'),
    CharConfigField('cache.host', 'CACHE_REDIS_HOST'),
    CharConfigField('cache.password', 'CACHE_REDIS_PASSWORD'),
    IntegerConfigField('cache.port', 'CACHE_REDIS_PORT'),

    IntegerConfigField('session.db', 'SESSION_REDIS_DB'),
    CharConfigField('session.host', 'SESSION_REDIS_HOST'),
    CharConfigField('session.password', 'SESSION_REDIS_PASSWORD'),
    IntegerConfigField('session.port', 'SESSION_REDIS_PORT'),

    IntegerConfigField('websocket.db', 'WS4REDIS_DB'),
    CharConfigField('websocket.host', 'WS4REDIS_HOST'),
    CharConfigField('websocket.password', 'WS4REDIS_PASSWORD'),
    IntegerConfigField('websocket.port', 'WS4REDIS_PORT'),

    IntegerConfigField('celery.db', 'CELERY_DB'),
    CharConfigField('celery.host', 'CELERY_HOST'),
    CharConfigField('celery.password', 'CELERY_PASSWORD'),
    IntegerConfigField('celery.port', 'CELERY_PORT'),

    CharConfigField('email.host', 'EMAIL_HOST'),
    CharConfigField('email.password', 'EMAIL_HOST_PASSWORD'),
    IntegerConfigField('email.port', 'EMAIL_PORT'),
    CharConfigField('email.user', 'EMAIL_HOST_USER'),
    BooleanConfigField('email.use_tls', 'EMAIL_USE_TLS'),
    BooleanConfigField('email.use_ssl', 'EMAIL_USE_SSL'),

]
