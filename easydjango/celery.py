# coding=utf-8
"""load Celery and discover tasks
==============================

You should not use this module (or rename it), as it is only used to auto-discover tasks.
"""
from __future__ import unicode_literals, absolute_import, print_function
import logging.config
from django.conf import settings
from easydjango.scripts import set_env
import celery
# used to avoid strange import bug with Python 3.2/3.3
# noinspection PyStatementEffect
celery.__file__
from celery import Celery, signals

__author__ = 'Matthieu Gallet'
project_name = set_env()
app = Celery(project_name)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# noinspection PyUnusedLocal
@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    """Use to setup the logs, overriding the default Celery configuration """
    logging.config.dictConfig(settings.LOGGING)

# Moving the call here works
app.log.setup()
