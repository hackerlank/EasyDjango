# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging
import os

import time

import sys
import warnings

from django.core.management import color_style
from django.utils.log import AdminEmailHandler as BaseAdminEmailHandler
from djangofloor.utils import ensure_dir

__author__ = 'Matthieu Gallet'


class ColorizedFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.style = color_style()
        super(ColorizedFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        msg = record.msg
        level = record.levelno
        if level <= logging.DEBUG:
            msg = self.style.HTTP_SUCCESS(msg)
        elif level <= logging.INFO:
            msg = self.style.HTTP_NOT_MODIFIED(msg)
        elif level <= logging.WARNING:
            msg = self.style.HTTP_INFO(msg)
        else:
            # Any 5XX, or any other response
            msg = self.style.HTTP_SERVER_ERROR(msg)
        record.msg = msg
        return super(ColorizedFormatter, self).format(record)


# noinspection PyClassHasNoInit
class AdminEmailHandler(BaseAdminEmailHandler):
    previous_email_time = None
    min_interval = 600

    def send_mail(self, subject, message, *args, **kwargs):
        if self.can_send_email():
            try:
                super(AdminEmailHandler, self).send_mail(subject, message, *args, **kwargs)
            except Exception as e:
                print("Unable to send e-mail to admin. Please checks your e-mail settings [%r]." % e)

    def can_send_email(self):
        now = time.time()
        previous = AdminEmailHandler.previous_email_time
        AdminEmailHandler.previous_email_time = now
        can_send = True
        if previous and now - previous < self.min_interval:
            can_send = False
        return can_send


# noinspection PyTypeChecker
def generate_log_configuration(log_directory=None, project_name=None, script_name=None, debug=False):
    fmt_server = 'django.server' if sys.stdout.isatty() else None
    fmt_stderr = 'colorized' if sys.stderr.isatty() else None
    fmt_stdout = 'colorized' if sys.stdout.isatty() else None
    formatters = {
        'django.server': {'()': 'django.utils.log.ServerFormatter', 'format': '[%(server_time)s] %(message)s'},
        'colorized': {'()': 'djangofloor.log.ColorizedFormatter'}}

    loggers = {'django': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'django.db.backends': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'django.request': {'handlers': [], 'level': 'INFO', 'propagate': True},
               'django.security': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'django.server': {'handlers': [], 'level': 'INFO', 'propagate': True},
               'pip.vcs': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'py.warnings': {'handlers': [], 'level': 'WARN', 'propagate': True}, }
    root = {'handlers': [], 'level': 'INFO'}
    handlers = {}
    config = {'version': 1, 'disable_existing_loggers': True, 'formatters': formatters,
              'handlers': handlers, 'loggers': loggers, 'root': root}
    if debug:
        warnings.simplefilter('always', DeprecationWarning)
        logging.captureWarnings(True)
        loggers['django.request'].update({'level': 'DEBUG'})
        loggers['django.server'].update({'handlers': ['django.server'], 'propagate': False})
        loggers['py.warnings'].update({'level': 'INFO'})
        handlers.update({'django.server': {'class': 'logging.StreamHandler', 'level': 'DEBUG',
                                           'stream': 'ext://sys.stdout', 'formatter': fmt_server},
                         'stderr': {'class': 'logging.StreamHandler', 'level': 'ERROR',
                                    'stream': 'ext://sys.stderr', 'formatter': fmt_stderr},
                         'stdout': {'class': 'logging.StreamHandler', 'level': 'DEBUG',
                                    'stream': 'ext://sys.stdout', 'formatter': fmt_stdout}})
        root.update({'handlers': ['stdout', 'stderr'], 'level': 'DEBUG'})
        return config
    elif log_directory is None:
        loggers['django.request'].update({'level': 'WARN'})
        loggers['django.server'].update({'handlers': ['django.server'], 'propagate': False})
        handlers.update({'django.server': {'class': 'logging.StreamHandler', 'level': 'INFO',
                                           'stream': 'ext://sys.stdout', 'formatter': fmt_server},
                         "mail_admins": {'class': 'djangofloor.log.AdminEmailHandler', 'level': 'ERROR', },
                         'stderr': {'class': 'logging.StreamHandler', 'level': 'ERROR',
                                    'stream': 'ext://sys.stderr', 'formatter': fmt_stderr},
                         'stdout': {'class': 'logging.StreamHandler', 'level': 'INFO',
                                    'stream': 'ext://sys.stdout', 'formatter': fmt_stdout}})
        root.update({'handlers': ['mail_admins', 'stdout', 'stderr']})
        return config
    ensure_dir(log_directory, parent=False)
    handlers.update({'info_rotating': {'class': 'logging.handlers.RotatingFileHandler', 'level': 'INFO',
                                       'filename': os.path.join(log_directory,
                                                                '%s-%s-info.log' % (project_name, script_name)),
                                       'maxBytes': 1000000, 'backupCount': 3},
                     'error_rotating': {'class': 'logging.handlers.RotatingFileHandler', 'level': 'ERROR',
                                        'filename': os.path.join(log_directory,
                                                                 '%s-%s-error.log' % (project_name, script_name)),
                                        'maxBytes': 1000000, 'backupCount': 3},
                     'mail_admins': {'level': 'ERROR', 'class': 'djangofloor.log.AdminEmailHandler'}})
    root.update({'handlers': ['mail_admins', 'error_rotating', 'info_rotating']})
    return config
