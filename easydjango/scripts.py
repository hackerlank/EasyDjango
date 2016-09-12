# coding=utf-8
""" "Main" functions for Django, Celery, Gunicorn and uWSGI
========================================================

Define "main" functions for your scripts using the Django `manage.py` system or Gunicorn/Celery/uWSGI.
"""
from __future__ import unicode_literals, absolute_import, print_function

import glob
from argparse import ArgumentParser
import subprocess
import re
import os
import sys

from easydjango.conf.merger import SettingMerger
from easydjango.conf.providers import PythonModuleProvider, PythonFileProvider, IniConfigProvider
from easydjango.utils import import_module

__author__ = 'Matthieu Gallet'


def __get_extra_option(name, default, *argnames):
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    parser.add_argument(*argnames, action='store', default=default)
    options, extra_args = parser.parse_known_args()
    sys.argv[1:] = extra_args
    return getattr(options, name)


def __set_default_option(options, name):
    option_name = name.replace('_', '-')
    if getattr(options, name):
        sys.argv += ['--%s' % option_name, getattr(options, name)]


def get_merger_from_env():
    easydjango_environment = os.environ['EASYDJANGO_ENVIRONMENT']

    project_name, mapping, providers_str = easydjango_environment.partition(';')
    try:
        module_name, sep, attribute = mapping.partition(':')
        module = import_module(module_name)
        settings_list = getattr(module, attribute)
    except ImportError:
        settings_list = []
    providers = []
    for provider_str in providers_str.split(','):
        kind, sep, value = provider_str.partition('://')
        if kind == 'pymodule':
            providers.append(PythonModuleProvider(value))
        elif kind == 'pyfile':
            providers.append(PythonFileProvider(value))
        elif kind == 'ini':
            providers.append(IniConfigProvider(value))
    return SettingMerger(project_name, settings_list, providers)


def set_env():
    """Set the environment variable `EASYDJANGO_ENVIRONMENT` with the project name and all settings
    The value looks like "project_name:settings1,settings2,settings3"

    1) determine the project name

        if the script is {xxx}-[gunicorn|manage][.py], then the project_name is assumed to be {xxx}
        if option --dfproject {xxx} is available, then the project_name is assumed to be {xxx}

    2) determine all available settings in this order:
        easydjango.defaults
        {project_name}.defaults (overrides easydjango.defaults)
        {root}/etc/{project_name}/*.ini (overrides {project_name}.settings)
        {root}/etc/{project_name}/*.py (overrides {root}/etc/{project_name}/*.ini)
        ./local_config.ini (overrides {root}/etc/{project_name}/*.py)
        ./local_config.py (overrides ./local_config.ini)

    """
    # django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easydjango.conf.settings')
    # project name
    script_re = re.match(r'^([\w_\-.]+)-(ctl|manage|gunicorn|celery|uwsgi)(\.py|\.pyc|)$',
                         os.path.basename(sys.argv[0]))
    if script_re:
        project_name = script_re.group(1)
    else:
        project_name = __get_extra_option('dfproject', 'easydjango', '--dfproject')
    project_name = project_name.replace('-', '_')

    prefix = sys.prefix
    if prefix == '/usr':
        prefix = ''

    providers_str = ['pymodule://easydjango.conf.defaults']
    if project_name != 'easydjango':
        providers_str.append('py://%s.defaults' % project_name)
        mapping = '%s.iniconf:INI_MAPPING' % project_name
    else:
        mapping = 'easydjango.conf.iniconf:INI_MAPPING'

    ini_filenames = glob.glob('%s/etc/%s/*.ini' % (prefix, project_name))
    ini_filenames.sort()
    providers_str += ['ini://%s' % x for x in ini_filenames]
    py_filenamess = glob.glob('%s/etc/%s/*.py' % (prefix, project_name))
    py_filenamess.sort()
    providers_str += ['pyfile://%s' % x for x in py_filenamess]

    if os.path.isfile('local_config.ini'):
        providers_str.append(os.path.abspath('local_config.ini'))
    if os.path.isfile('local_config.py'):
        providers_str.append(os.path.abspath('local_config.py'))

    os.environ.setdefault('EASYDJANGO_ENVIRONMENT', '%s;%s;%s' % (project_name, mapping, ','.join(providers_str)))
    return project_name


def load_celery():
    """ Import Celery application unless Celery is disabled.
    Allow to automatically load tasks
    """
    from django.conf import settings
    if settings.USE_CELERY:
        from easydjango.celery import app
        return app
    return None


def control():
    """Main user function, with commands for deploying, migrating data, backup or running services
    """


def manage():
    """
    Main function, calling Django code for management commands. Retrieve some default values from Django settings.
    """
    set_env()
    from django.conf import settings
    from django.core.management import execute_from_command_line
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    options, extra_args = parser.parse_known_args()
    if len(extra_args) == 1 and extra_args[0] == 'runserver':
        sys.argv += [settings.BIND_ADDRESS]
    return execute_from_command_line(sys.argv)


def gunicorn():
    """ wrapper around gunicorn. Retrieve some default values from Django settings.

    :return:
    """
    from gunicorn.app.wsgiapp import run

    set_env()
    from django.conf import settings
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    parser.add_argument('-b', '--bind', action='store', default=settings.BIND_ADDRESS, help=settings.BIND_ADDRESS_HELP)
    # parser.add_argument('--forwarded-allow-ips', action='store', default=','.join(settings.REVERSE_PROXY_IPS))
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('-t', '--timeout', action='store', default=str(settings.REVERSE_PROXY_TIMEOUT),
                        help=settings.REVERSE_PROXY_TIMEOUT_HELP)
    parser.add_argument('--proxy-allow-from', action='store', default=','.join(settings.REVERSE_PROXY_IPS),
                        help='Front-end\'s IPs from which allowed accept proxy requests (comma separate)')
    options, extra_args = parser.parse_known_args()
    sys.argv[1:] = extra_args
    __set_default_option(options, 'bind')
    # __set_default_option(options, 'forwarded_allow_ips')
    __set_default_option(options, 'timeout')
    __set_default_option(options, 'proxy_allow_from')
    application = 'djangofloor.wsgi_http:application'
    if application not in sys.argv:
        sys.argv.append(application)
    return run()


def celery():
    set_env()
    from celery.bin.celery import main as celery_main
    from django.conf import settings
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    parser.add_argument('-A', '--app', action='store', default='djangofloor', help=settings.BIND_ADDRESS_HELP)
    options, extra_args = parser.parse_known_args()
    sys.argv[1:] = extra_args
    __set_default_option(options, 'app')
    celery_main(sys.argv)


def uwsgi():
    set_env()
    from django.conf import settings
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    parser.add_argument('--mode', default='both', choices=('both', 'http', 'websockets'))
    parser.add_argument('-b', '--bind', action='store', default=settings.BIND_ADDRESS, help=settings.BIND_ADDRESS_HELP)
    options, extra_args = parser.parse_known_args()
    sys.argv[1:] = extra_args
    argv = list(sys.argv)
    # websocket + http
    # uwsgi --virtualenv /path/to/virtualenv --http :80 --gevent 100 --http-websockets --module wsgi
    # http only
    # uwsgi --virtualenv /path/to/virtualenv --socket /path/to/django.socket --buffer-size=32768 --workers=5 --master --module wsgi_django
    # websockets only
    # uwsgi --virtualenv /path/to/virtualenv --http-socket /path/to/web.socket --gevent 1000 --http-websockets --workers=2 --master --module wsgi_websocket

    if options.mode == 'both':
        argv += ['--module', 'djangofloor.wsgi']
        argv += ['--http', options.bind]
    elif options.mode == 'http':
        argv += ['--module', 'djangofloor.wsgi_http']
    elif options.mode == 'websocket':
        argv += ['--module', 'djangofloor.wsgi_websockets']

    # ok, we can now run uwsgi
    argv[0] = 'uwsgi'
    p = subprocess.Popen(argv)
    p.wait()
    sys.exit(p.returncode)
