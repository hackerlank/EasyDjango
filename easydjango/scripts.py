# coding=utf-8
""" "Main" functions for Django, Celery, Gunicorn and uWSGI
========================================================

Define "main" functions for your scripts using the Django `manage.py` system or Gunicorn/Celery/uWSGI.
"""
from __future__ import unicode_literals, absolute_import, print_function

import codecs
import os
import re
import shutil
import subprocess
import sys
from argparse import ArgumentParser

from django.utils.six import text_type
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

    project_name, sep, script = os.environ['EASYDJANGO_CONF_NAME'].partition(':')
    project_name = project_name.replace('-', '_')
    if sep != ':':
        script = None

    prefix = os.path.abspath(sys.prefix)
    if prefix == '/usr':
        prefix = ''

    def search_providers(basename, suffix, cls):
        default_ini_filename = '%s/etc/%s/%s.%s' % (prefix, project_name, basename, suffix)
        ini_filenames = [default_ini_filename]
        ini_filenames.sort()
        return [cls(x) for x in ini_filenames]

    config_providers = [PythonModuleProvider('easydjango.conf.defaults')]
    if project_name != 'easydjango':
        config_providers.append(PythonModuleProvider('%s.defaults' % project_name))
        mapping = '%s.iniconf:INI_MAPPING' % project_name
    else:
        mapping = 'easydjango.conf.mapping:INI_MAPPING'
    config_providers += search_providers('settings', 'ini', IniConfigProvider)
    config_providers += search_providers('settings', 'py', PythonFileProvider)
    if script:
        config_providers += search_providers(script, 'ini', IniConfigProvider)
        config_providers += search_providers(script, 'py', PythonFileProvider)
    config_providers += [IniConfigProvider(os.path.abspath('local_config.ini'))]
    config_providers += [PythonFileProvider(os.path.abspath('local_config.py'))]

    fields_provider = PythonConfigFieldsProvider(mapping)
    extra_values = {'PROJECT_NAME': project_name}
    if script:
        extra_values['SCRIPT_NAME'] = script
    return SettingMerger(fields_provider, config_providers, extra_values=extra_values)


def set_env():
    """Set the environment variable `EASYDJANGO_CONF_NAME` with the project name and the script name
    The value looks like "project_name:celery" or "project_name:django"

    determine the project name

        if the script is {xxx}-[gunicorn|manage][.py], then the project_name is assumed to be {xxx}
        if option --dfproject {xxx} is available, then the project_name is assumed to be {xxx}

    """
    # django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easydjango.conf.settings')
    # project name
    script_re = re.match(r'^([\w_\-.]+)-(ctl|gunicorn|celery|uwsgi|django)(\.py|\.pyc|)$',
                         os.path.basename(sys.argv[0]))
    if script_re:
        conf_name = '%s:%s' % (script_re.group(1), script_re.group(2))
    else:
        conf_name = __get_extra_option('dfproject', 'easydjango', '--dfproject')
    os.environ.setdefault('EASYDJANGO_CONF_NAME', conf_name)
    return conf_name


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
    set_env()
    import django as base_django
    if base_django.VERSION[:2] >= (1, 7):
        base_django.setup()
    from django.conf import settings
    from django.utils.translation import ugettext as _
    command_commands = settings.COMMON_COMMANDS
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    script, command = command_commands.get(cmd, (None, None))
    invalid_script = _('Invalid script name: %(cmd)s') % {'cmd': script}
    invalid_command = _('Usage: %(name)s %(cmd)s') % {'name': sys.argv[0], 'cmd': '|'.join(command_commands)}

    if len(sys.argv) == 1 or sys.argv[1] not in command_commands:
        print(invalid_command)
        return 1
    scripts = {'django': django, 'gunicorn': gunicorn, 'celery': celery, 'uwsgi': uwsgi}
    if script not in scripts:
        print(invalid_script)
        return 1
    project_name, sep, __ = os.environ['EASYDJANGO_CONF_NAME'].partition(':')
    os.environ['EASYDJANGO_CONF_NAME'] = '%s:%s' % (project_name, script)
    if command:
        sys.argv[1] = command
    else:
        sys.argv[1:2] = []
    return scripts[script]()


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
    application = 'easydjango.wsgi:gunicorn_application'
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
    cmd = ['uwsgi', '--plugin', 'python', '--module', 'easydjango.wsgi']
    parser.add_argument('--no-master', default=False, action='store_true',
                        help='disable master process')
    parser.add_argument('--no-http-websockets', default=False, action='store_true',
                        help='do not automatically detect websockets connections and put the session in raw mode')
    parser.add_argument('--no-enable-threads', default=False, action='store_true',
                        help='do not run each worker in prethreaded mode with the specified number of threads')
    parser.add_argument('-p', '--processes', default=settings.UWSGI_PROCESSES, type=int,
                        help='spawn the specified number of workers/processes')
    parser.add_argument('--workers', default=None, type=int,
                        help='spawn the specified number of workers/processes')
    parser.add_argument('--threads', default=settings.UWSGI_THREADS, type=int,
                        help='run each worker in prethreaded mode with the specified number of threads')
    parser.add_argument('--http-socket', default=settings.LISTEN_ADDRESS,
                        help='bind to the specified UNIX/TCP socket using HTTP protocol')
    parser.add_argument('--reload-mercy', default=5, type=int,
                        help='set the maximum time (in seconds) we wait for workers and other processes '
                             'to die during reload/shutdown')
    parser.add_argument('--worker-reload-mercy', default=5, type=int,
                        help='set the maximum time (in seconds) a worker can take to reload/shutdown (default is 5)')
    parser.add_argument('--mule-reload-mercy', default=5, type=int,
                        help='set the maximum time (in seconds) a mule can take to reload/shutdown (default is 5)')
    args = [x for x in sys.argv[1:] if x != '-h']
    options, extra_args = parser.parse_known_args(args=args)
    if not options.no_master:
        cmd += ['--master']
    if not options.no_http_websockets:
        cmd += ['--http-websockets']
    if not options.no_enable_threads:
        cmd += ['--enable-threads']
    if options.workers:
        cmd += ['--workers', text_type(options.workers)]
    elif options.processes:
        cmd += ['--processes', text_type(options.processes)]
    cmd += ['--threads', text_type(options.threads)]
    cmd += ['--http-socket', options.http_socket]
    cmd += ['--reload-mercy', text_type(options.reload_mercy)]
    cmd += ['--worker-reload-mercy', text_type(options.worker_reload_mercy)]
    cmd += ['--mule-reload-mercy', text_type(options.mule_reload_mercy)]
    if '-h' in sys.argv:
        cmd += ['-h']
    cmd += list(extra_args)
    p = subprocess.Popen(cmd)
    p.wait()
    sys.exit(p.returncode)


# noinspection PyUnresolvedReferences
def create_project():
    import easydjango
    inp = input
    if sys.version_info[0] == 2:
        # noinspection PyUnresolvedReferences
        inp = raw_input
    base_path = os.path.dirname(easydjango.__file__)
    template_base_path = os.path.join(base_path, 'templates', 'easydjango', 'create_project')
    template_values = {}
    default_values = [('project_name', 'Your new project name', 'MyProject'),
                      ('package_name', 'Python package name', ''),
                      ('version', 'Initial version', '0.1'),
                      ('dst_dir', 'Root project path', '.'), ]
    for key, text, default_value in default_values:
        if key == 'package_name':
            default_value = re.sub('[^a-z0-9_]', '_', template_values['project_name'].lower())
            while default_value[0:1] in '0123456789_':
                default_value = default_value[1:]
        value = None
        while not value:
            value = inp('%s [%s] ' % (text, default_value))
            if not value:
                value = default_value
        template_values[key] = value
    dst_dir = template_values['dst_dir']

    if os.path.exists(dst_dir):
        value = ''
        while not value:
            value = inp('%s already exists. Do you want to remove it? [Y/n]')
            value = value.lower()
            if value == 'n':
                return
            elif value != 'y':
                value = ''
        if os.path.isdir(dst_dir):
            shutil.rmtree(dst_dir)
        if os.path.exists(dst_dir):
            os.remove(dst_dir)

    for root, dirnames, filenames in os.walk(template_base_path):
        for dirname in dirnames:
            src_path = os.path.join(root, dirname)
            dst_path = os.path.relpath(src_path, template_base_path)
            dst_path = dst_path.format(**template_values)
            dst_path = os.path.join(dst_dir, dst_path)
            print('%s -> %s' % (src_path, dst_path))
            if not os.path.isdir(dst_path):
                os.makedirs(dst_path)
        for filename in filenames:
            src_path = os.path.join(root, filename)
            dst_path = os.path.relpath(src_path, template_base_path)
            dst_path = dst_path.format(**template_values)
            dst_path = os.path.join(dst_dir, dst_path)
            print('%s -> %s' % (src_path, dst_path))
            dirname = os.path.dirname(dst_path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            with codecs.open(dst_path, 'w', encoding='utf-8') as out_fd:
                with codecs.open(src_path, 'r', encoding='utf-8') as in_fd:
                    content = in_fd.read().format(**template_values)
                    out_fd.write(content)
