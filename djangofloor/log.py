# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging
import logging.handlers
import os

import time

import sys
import warnings

import re
from django.core.management import color_style
from django.utils.log import AdminEmailHandler as BaseAdminEmailHandler
# noinspection PyUnresolvedReferences
from django.utils.six.moves.urllib.parse import urlparse
from djangofloor.utils import ensure_dir

__author__ = 'Matthieu Gallet'


class ColorizedFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self.style = color_style()
        kwargs.setdefault('fmt', '%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
        kwargs.setdefault('datefmt', '%Y-%m-%d %H:%M:%S')
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
def generate_log_configuration(log_directory=None, project_name=None, script_name=None, debug=False,
                               log_remote_url=None):
    fmt_server = 'django.server' if sys.stdout.isatty() else None
    fmt_stderr = 'colorized' if sys.stderr.isatty() else None
    fmt_stdout = 'colorized' if sys.stdout.isatty() else None
    formatters = {
        'django.server': {'()': 'django.utils.log.ServerFormatter',
                          'format': '%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
                          'datefmt': '%Y-%m-%d %H:%M:%S'},
        'colorized': {'()': 'djangofloor.log.ColorizedFormatter'}}

    loggers = {'django': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'django.db.backends': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'django.request': {'handlers': [], 'level': 'INFO', 'propagate': True},
               'django.security': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'django.server': {'handlers': ['access'], 'level': 'INFO', 'propagate': False},
               'djangofloor.signals': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'aiohttp.access': {'handlers': ['access'], 'level': 'INFO', 'propagate': False},
               'gunicorn.access': {'handlers': ['access'], 'level': 'INFO', 'propagate': False},
               'gunicorn.error': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'geventwebsocket.handler': {'handlers': ['access'], 'level': 'INFO', 'propagate': False},
               'pip.vcs': {'handlers': [], 'level': 'WARN', 'propagate': True},
               'py.warnings': {'handlers': [], 'level': 'WARN', 'propagate': True}, }
    root = {'handlers': [], 'level': 'DEBUG'}
    handlers = {'access': {'class': 'logging.StreamHandler', 'level': 'INFO',
                                    'stream': 'ext://sys.stdout', 'formatter': fmt_server}}
    config = {'version': 1, 'disable_existing_loggers': True, 'formatters': formatters,
              'handlers': handlers, 'loggers': loggers, 'root': root}
    if debug:
        warnings.simplefilter('always', DeprecationWarning)
        logging.captureWarnings(True)
        loggers['django.request'].update({'level': 'DEBUG'})
        loggers['py.warnings'].update({'level': 'INFO'})
        loggers['djangofloor.signals'].update({'level': 'INFO'})
        handlers.update({'stdout': {'class': 'logging.StreamHandler', 'level': 'DEBUG',
                                    'stream': 'ext://sys.stdout', 'formatter': fmt_stdout}})
        root.update({'handlers': ['stdout'], 'level': 'INFO'})
        return config

    error_handler = {'class': 'logging.StreamHandler', 'stream': 'ext://sys.stderr', 'formatter': fmt_stderr}
    handlers.update({"mail_admins": {'class': 'djangofloor.log.AdminEmailHandler', 'level': 'ERROR', },
                     'info': {'class': 'logging.StreamHandler', 'level': 'INFO', 'stream': 'ext://sys.stdout',
                              'formatter': fmt_stdout}})
    if log_directory is not None:
        ensure_dir(log_directory, parent=False)
        error_handler = {'class': 'logging.handlers.RotatingFileHandler', 'maxBytes': 1000000, 'backupCount': 3,
                         'filename': os.path.join(log_directory, '%s-%s-error.log' % (project_name, script_name))}
        handlers.update({'info': {'class': 'logging.handlers.RotatingFileHandler', 'level': 'INFO',
                                  'filename': os.path.join(log_directory,
                                                           '%s-%s-info.log' % (project_name, script_name)),
                                  'maxBytes': 1000000, 'backupCount': 3},
                         'access': {'class': 'logging.handlers.RotatingFileHandler', 'level': 'INFO',
                                    'filename': os.path.join(log_directory,
                                                             '%s-%s-access.log' % (project_name, script_name)),
                                    'maxBytes': 1000000, 'backupCount': 3},
                         'mail_admins': {'level': 'ERROR', 'class': 'djangofloor.log.AdminEmailHandler'},
                         })
    if log_remote_url:
        parsed_log_url = urlparse(log_remote_url)
        scheme = parsed_log_url.scheme
        device, sep, facility_name = parsed_log_url.path.rpartition('/')
        if scheme == 'syslog' or scheme == 'syslog+tcp':
            import platform
            import socket
            import syslog
            if parsed_log_url.hostname and parsed_log_url.port and re.match('^\d+$', parsed_log_url.port):
                address = (parsed_log_url.hostname, int(parsed_log_url.port))
            elif device:
                address = device
            elif platform.system() == 'Darwin':
                address = '/var/run/syslog'
            elif platform.system() == 'Linux':
                address = '/dev/log'
            else:
                address = ('localhost', 514)
            socktype = socket.SOCK_DGRAM if scheme == 'syslog' else socket.SOCK_STREAM
            facility = logging.handlers.SysLogHandler.facility_names.get(facility_name, syslog.LOG_USER)
            error_handler = {'class': 'logging.handlers.SysLogHandler', 'address': address, 'facility': facility,
                             'socktype': socktype}
        elif scheme == 'logd':
            identifier = facility_name or project_name
            error_handler = {'class': 'systemd.journal.JournalHandler', 'SYSLOG_IDENTIFIER': identifier}

    error_handler['level'] = 'ERROR'
    handlers['error'] = error_handler
    loggers['django.request'].update({'level': 'WARN'})
    root.update({'handlers': ['mail_admins', 'error', 'info']})
    return config
