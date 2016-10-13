# coding=utf-8
""" "Main" functions for Django, Celery, Gunicorn and uWSGI
========================================================

Define "main" functions for your scripts using the Django `manage.py` system or Gunicorn/Celery/uWSGI.
"""
from __future__ import unicode_literals, absolute_import, print_function

import glob
import os
import re
import subprocess
import sys
from argparse import ArgumentParser

from easydjango.conf.merger import SettingMerger
from easydjango.conf.providers import PythonModuleProvider, PythonFileProvider, IniConfigProvider, \
    PythonConfigFieldsProvider

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
    """ Should be used after set_env()
       determine all available settings in this order:
        easydjango.defaults
        {project_name}.defaults (overrides easydjango.defaults)
        {root}/etc/{project_name}/*.ini (overrides {project_name}.settings)
        {root}/etc/{project_name}/*.py (overrides {root}/etc/{project_name}/*.ini)
        ./local_config.ini (overrides {root}/etc/{project_name}/*.py)
        ./local_config.py (overrides ./local_config.ini)
    """

    project_name = os.environ['EASYDJANGO_PROJECT_NAME']
    project_name = project_name.replace('-', '_')

    prefix = os.path.abspath(sys.prefix)
    if prefix == '/usr':
        prefix = ''

    def search_providers(suffix, cls):
        default_ini_filename = '%s/etc/%s/*.%s' % (prefix, project_name, suffix)
        ini_filenames = [default_ini_filename] + glob.glob(default_ini_filename)
        ini_filenames.sort()
        return [cls(x) for x in ini_filenames]

    config_providers = [PythonModuleProvider('easydjango.conf.defaults')]
    if project_name != 'easydjango':
        config_providers.append(PythonModuleProvider('%s.defaults' % project_name))
        mapping = '%s.iniconf:INI_MAPPING' % project_name
    else:
        mapping = 'easydjango.conf.mapping:INI_MAPPING'
    config_providers += search_providers('ini', IniConfigProvider)
    config_providers += search_providers('py', PythonFileProvider)
    config_providers += [IniConfigProvider(os.path.abspath('local_config.ini'))]
    config_providers += [PythonFileProvider(os.path.abspath('local_config.py'))]

    fields_provider = PythonConfigFieldsProvider(mapping)
    return SettingMerger(project_name, fields_provider, config_providers)


def set_env():
    """Set the environment variable `EASYDJANGO_PROJECT_NAME` with the project name and all settings
    The value looks like "project_name:settings1,settings2,settings3"

    determine the project name

        if the script is {xxx}-[gunicorn|manage][.py], then the project_name is assumed to be {xxx}
        if option --dfproject {xxx} is available, then the project_name is assumed to be {xxx}

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
    os.environ.setdefault('EASYDJANGO_PROJECT_NAME', project_name)
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


def django():
    """
    Main function, calling Django code for management commands. Retrieve some default values from Django settings.
    """
    set_env()
    from django.conf import settings
    from django.core.management import execute_from_command_line
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    options, extra_args = parser.parse_known_args()
    if len(extra_args) == 1 and extra_args[0] == 'runserver':
        sys.argv += [settings.LISTEN_ADDRESS]
    return execute_from_command_line(sys.argv)


def gunicorn():
    """ wrapper around gunicorn. Retrieve some default values from Django settings.

    :return:
    """
    from gunicorn.app.wsgiapp import run

    set_env()
    from django.conf import settings
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    parser.add_argument('-b', '--bind', action='store', default=settings.LISTEN_ADDRESS)
    options, extra_args = parser.parse_known_args()
    sys.argv[1:] = extra_args
    __set_default_option(options, 'bind')
    application = 'djangofloor.wsgi_http:application'
    if application not in sys.argv:
        sys.argv.append(application)
    return run()


def celery():
    set_env()
    from celery.bin.celery import main as celery_main
    parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
    parser.add_argument('-A', '--app', action='store', default='easydjango')
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


def create_project():
    import easydjango
    base_path = os.path.dirname(easydjango.__file__)
    template_base_path = os.path.join(base_path, 'templates', 'easydjango', 'create_project')
    template_values = {'author_name': '', 'version': '',
                       'project_name': '', 'package_name': '',
                       }
    dest_path = None
    for root, dirnames, filenames in os.walk(template_base_path):
        for dirname in dirnames:
            src_path = os.path.join(root, dirname)
            dst_path = os.path.relpath(src_path, template_base_path)
            dst_path = dst_path.format(**template_values)
        for filename in filenames:
            src_path = os.path.join(root, filename)
            dst_path = os.path.relpath(src_path, template_base_path)
            dst_path = dst_path.format(**template_values)
