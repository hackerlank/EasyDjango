# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import logging
import os
import sys

import pkg_resources
import time
from django.core.management import color_style
from django.utils import six
from django.utils.log import AdminEmailHandler as BaseAdminEmailHandler

__author__ = 'Matthieu Gallet'


def is_package_present(package_name):
    try:
        import_module(package_name)
        return True
    except ImportError:
        return False


def ensure_dir(path, parent=True):
    """Ensure that the given directory exists

    :param path: the path to check
    :param parent: only ensure the existence of the parent directory

    """
    dirname = os.path.dirname(path) if parent else path
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


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

    def send_mail(self, subject, message, *args, **kwargs):
        now = time.time()
        previous = AdminEmailHandler.previous_email_time
        AdminEmailHandler.previous_email_time = now
        if previous and now - previous < 600:
            return
        try:
            super(AdminEmailHandler, self).send_mail(subject, message, *args, **kwargs)
        except Exception as e:
            print("Unable to send e-mail to admin. Please checks your e-mail settings [%r]." % e)


def generate_log_configuration(root_directory=None, project_name=None, script_name=None, debug=False):
    fmt_server = 'django.server' if sys.stdout.isatty() else None
    fmt_stderr = 'colorized' if sys.stderr.isatty() else None
    fmt_stdout = 'colorized' if sys.stdout.isatty() else None
    formatters = {
        'django.server': {'()': 'django.utils.log.ServerFormatter', 'format': '[%(server_time)s] %(message)s'},
        'colorized': {'()': 'easydjango.utils.ColorizedFormatter'}}
    if debug:
        return {
            'version': 1, 'disable_existing_loggers': True,
            'formatters': formatters,
            'handlers': {
                'django.server': {'class': 'logging.StreamHandler', 'level': 'DEBUG',
                                  'stream': 'ext://sys.stdout', 'formatter': fmt_server},
                'stderr': {'class': 'logging.StreamHandler', 'level': 'ERROR',

                           'stream': 'ext://sys.stderr', 'formatter': fmt_stderr},
                'stdout': {'class': 'logging.StreamHandler', 'level': 'DEBUG',
                           'stream': 'ext://sys.stdout', 'formatter': fmt_stdout},
            },
            'loggers': {
                'django': {'handlers': [], 'level': 'WARN', 'propagate': True},
                'django.db.backends': {'handlers': [], 'level': 'WARN', 'propagate': True},
                'django.request': {'handlers': [], 'level': 'DEBUG', 'propagate': True},
                'django.security': {'handlers': [], 'level': 'WARN', 'propagate': True},
                'django.server': {'handlers': ['django.server'], 'level': 'INFO', 'propagate': False},
                'py.warnings': {'handlers': [], 'level': 'INFO', 'propagate': True},
            },
            'root': {
                'handlers': ['stdout', 'stderr'], 'level': 'DEBUG'
            }
        }
    elif root_directory is None:
        return {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': formatters,
            'handlers': {
                'django.server': {'level': 'INFO', 'class': 'logging.StreamHandler', 'formatter': fmt_server},
                'mail_admins': {'level': 'ERROR', 'class': 'easydjango.utils.AdminEmailHandler'},
                'stderr': {
                    'class': 'logging.StreamHandler', 'level': 'ERROR',
                    'stream': 'ext://sys.stderr', 'formatter': fmt_stderr},
                'stdout': {
                    'class': 'logging.StreamHandler', 'level': 'INFO',
                    'stream': 'ext://sys.stdout', 'formatter': fmt_stdout},
            },
            'loggers': {
                'django': {'handlers': [], 'level': 'WARN', 'propagate': True},
                'django.db.backends': {'handlers': [], 'level': 'WARN', 'propagate': True},
                'django.request': {'handlers': [], 'level': 'WARN', 'propagate': True},
                'django.security': {'handlers': [], 'level': 'WARN', 'propagate': True},
                'django.server': {'handlers': ['django.server'], 'level': 'INFO', 'propagate': False},
                'py.warnings': {'handlers': [], 'level': 'WARN', 'propagate': True},
            },
            'root': {
                'handlers': ['mail_admins', 'stdout', 'stderr'], 'level': 'INFO'
            }
        }
    ensure_dir(root_directory, parent=False)
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'handlers': {
            'info_rotating': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(root_directory, '%s-%s-info.log' % (project_name, script_name)),
                'maxBytes': 1000000,
                'backupCount': 3,
            },
            'error_rotating': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(root_directory, '%s-%s-error.log' % (project_name, script_name)),
                'maxBytes': 1000000,
                'backupCount': 3,
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'easydjango.utils.AdminEmailHandler',
            }
        },
        'loggers': {
            'django': {'handlers': [], 'level': 'WARN', 'propagate': True},
            'django.db.backends': {'handlers': [], 'level': 'WARN', 'propagate': True},
            'django.request': {'handlers': [], 'level': 'INFO', 'propagate': True},
            'django.security': {'handlers': [], 'level': 'WARN', 'propagate': True},
            'django.server': {'handlers': [], 'level': 'INFO', 'propagate': True},
            'py.warnings': {'handlers': [], 'level': 'WARN', 'propagate': True},
        },
        'root': {
            'handlers': ['mail_admins', 'error_rotating', 'info_rotating'], 'level': 'INFO'
        }
    }


def walk(module_name, dirname, topdown=True):
    """
    Copy of :func:`os.walk`, please refer to its doc. The only difference is that we walk in a package_resource
    instead of a plain directory.
    :type module_name: basestring
    :param module_name: module to search in
    :type dirname: basestring
    :param dirname: base directory
    :type topdown: bool
    :param topdown: if True, perform a topdown search.
    """

    def rec_walk(root):
        """
        Recursively list subdirectories and filenames from the root.
        :param root: the root path
        :type root: basestring
        """
        dirnames = []
        filenames = []
        for name in pkg_resources.resource_listdir(module_name, root):
            fullname = root + '/' + name
            isdir = pkg_resources.resource_isdir(module_name, fullname)
            if isdir:
                dirnames.append(name)
                if not topdown:
                    rec_walk(fullname)
            else:
                filenames.append(name)
        yield root, dirnames, filenames
        if topdown:
            for name in dirnames:
                for values in rec_walk(root + '/' + name):
                    yield values

    return rec_walk(dirname)


def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in range(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level package")
    return "%s.%s" % (package[:dot], name)


if six.PY3:
    # noinspection PyUnresolvedReferences
    from importlib import import_module
else:
    def import_module(name, package=None):
        """Import a module.

        The 'package' argument is required when performing a relative import. It
        specifies the package to use as the anchor point from which to resolve the
        relative import to an absolute import.

        """
        if name.startswith('.'):
            if not package:
                raise TypeError("relative imports require the 'package' argument")
            level = 0
            for character in name:
                if character != '.':
                    break
                level += 1
            name = _resolve_name(name[level:], package, level)
        __import__(name)
        return sys.modules[name]
