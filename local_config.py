# -*- coding: utf-8 -*-
DEBUG = True
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache', 'LOCATION': 'unique-snowflake'}}
PIPELINE_ENABLED = not DEBUG
EASYDJANGO_REMOTE_USER_HEADER = 'http-remote-user'  # HTTP-REMOTE-USER
