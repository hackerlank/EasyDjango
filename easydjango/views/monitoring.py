# -*- coding: utf-8 -*-
"""Display some system info

    * database states (Django databases (version) + Redis),
    * Logs

"""
from __future__ import unicode_literals, print_function, absolute_import

import pip
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.six import text_type
from django.views.decorators.cache import never_cache
from easydjango.decorators import REGISTERED_SIGNALS, REGISTERED_FUNCTIONS
from pkg_resources import parse_requirements, Distribution

from easydjango.celery import app
from easydjango.conf.settings import merger
from easydjango.tasks import set_websocket_topics, import_signals_and_functions

try:
    # noinspection PyPackageRequirements
    import psutil

    psutil.cpu_percent()
except ImportError:
    psutil = None

__author__ = 'Matthieu Gallet'


class MonitoringCheck(object):
    template = None
    frequency = None

    def render(self, request):
        template = get_template(self.template)
        context = self.get_context(request)
        content = template.render(context, request)
        return mark_safe(content)

    def get_context(self, request):
        return {}


class Packages(MonitoringCheck):
    template = 'easydjango/bootstrap3/monitoring/packages.html'

    def get_context(self, request):
        return {'installed_distributions': self.get_installed_distributions()}

    @staticmethod
    def get_installed_distributions():
        raw_installed_distributions = pip.get_installed_distributions()
        if settings.EASYDJANGO_CHECKED_REQUIREMENTS:
            requirements = {}  # requirements[key] = [key, state="danger/warning/success", [specs_str], [parsed_req]]
            for r in settings.EASYDJANGO_CHECKED_REQUIREMENTS:
                for p in parse_requirements(r):
                    requirements.setdefault(p.key, [p.key, None, 'danger', 'remove', [], []])
                    requirements[p.key][4] += [' '.join(y) for y in p.specs]
                    requirements[p.key][5].append(p)
            for r in raw_installed_distributions:
                if r.key not in requirements:
                    continue
                requirements[r.key][1] = r.version
                d = Distribution(project_name=r.key, version=r.version)
                if requirements[r.key][2] == 'danger':
                    requirements[r.key][2] = 'success'
                    requirements[r.key][3] = 'ok'
                for p in requirements[r.key][5]:
                    if d not in p:
                        requirements[r.key][2] = 'warning'
                        requirements[r.key][3] = 'warning-sign'
            installed_distributions = list(sorted(requirements.values(),
                                                  key=lambda k: k[0].lower()))
        else:
            installed_distributions = [[y.key, y.version, 'success', 'ok', ['== %s' % y.version], []]
                                       for y in raw_installed_distributions]
        return installed_distributions


class System(MonitoringCheck):
    template = 'easydjango/bootstrap3/monitoring/system.html'

    def get_context(self, request):
        if psutil is None:
            return {'cpu_count': None, 'memory': None, 'cpu_average_usage': None,
                    'cpu_current_usage': None, 'swap': None, 'disks': None}
        y = psutil.cpu_times()
        cpu_average_usage = int((y.user + y.system) / (y.idle + y.user + y.system) * 100.)
        cpu_current_usage = int(psutil.cpu_percent(interval=0.1))
        cpu_count = psutil.cpu_count(logical=True), psutil.cpu_count(logical=False)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disks = [(y.mountpoint, psutil.disk_usage(y.mountpoint)) for y in psutil.disk_partitions(all=True)]
        return {'cpu_count': cpu_count, 'memory': memory, 'cpu_average_usage': cpu_average_usage,
                'cpu_current_usage': cpu_current_usage, 'swap': swap, 'disks': disks}


class CeleryStats(MonitoringCheck):
    template = 'easydjango/bootstrap3/monitoring/celery_stats.html'

    def get_context(self, request):
        celery_stats = app.control.inspect().stats()
        import_signals_and_functions()
        expected_queues = {y.queue: ('danger', 'remove') for y in REGISTERED_FUNCTIONS.values()}
        for connections in REGISTERED_SIGNALS.values():
            expected_queues.update({y.queue: ('danger', 'remove') for y in connections})
        queue_stats = app.control.inspect().active_queues()
        if queue_stats is None:
            queue_stats = {}
        for stats in queue_stats.values():
            for queue_data in stats:
                # noinspection PyTypeChecker
                if queue_data['name'] in expected_queues:
                    # noinspection PyTypeChecker
                    expected_queues[queue_data['name']] = ('success', 'ok')

        workers = []
        if celery_stats is None:
            celery_stats = {}
        for key in sorted(celery_stats.keys(), key=lambda y: y.lower()):
            worker = {'name': key}
            infos = celery_stats[key]
            url = '%s://%s' % (infos['broker']['transport'],
                               infos['broker']['hostname'])
            if infos['broker'].get('port'):
                url += ':%s' % infos['broker']['port']
            url += '/'
            if infos['broker'].get('virtual_host'):
                url += infos['broker']['virtual_host']
            worker['broker'] = url
            pids = [text_type(infos['pid'])] + [text_type(y) for y in infos['pool']['processes']]
            worker['pid'] = ', '.join(pids)
            worker['threads'] = infos['pool']['max-concurrency']
            worker['timeouts'] = sum(infos['pool']['timeouts'])
            worker['state'] = ('success', 'ok')
            if worker['timeouts'] > 0:
                worker['state'] = ('danger', 'remove')
            # noinspection PyTypeChecker
            worker['queues'] = list({y['name'] for y in queue_stats.get(key, [])})
            worker['queues'].sort()
            workers.append(worker)
        return {'workers': workers, 'expected_queues': expected_queues}


class RequestCheck(MonitoringCheck):
    template = 'easydjango/bootstrap3/monitoring/request_check.html'

    def get_context(self, request):
        def django_fmt(y):
            return y.upper().replace('-', '_')

        def http_fmt(y):
            return y.upper().replace('_', '-')

        context = {'remote_user': None, 'remote_address': request.META['REMOTE_ADDR'], 'use_x_forwarded_for': None,
                   'secure_proxy_ssl_header': None}
        header = settings.EASYDJANGO_REMOTE_USER_HEADER
        if header:
            context['remote_user'] = (http_fmt(header), request.META.get(django_fmt(header)))
        header = settings.USE_X_FORWARDED_FOR and 'X_FORWARDED_FOR'
        if header:
            context['use_x_forwarded_for'] = (http_fmt(header), request.META.get(django_fmt(header)))
        context['secure_proxy_ssl_header'] = None
        if settings.SECURE_PROXY_SSL_HEADER:
            header, value = settings.SECURE_PROXY_SSL_HEADER
            context['secure_proxy_ssl_header'] = (http_fmt(header), request.META.get(django_fmt(header)),
                                                  request.META.get(django_fmt(header)) == value)
        host, sep, port = request.get_host().partition(':')
        context['allowed_hosts'] = settings.ALLOWED_HOSTS
        context['allowed_host'] = host in settings.ALLOWED_HOSTS
        context['request_host'] = host
        context['request_site'] = None
        # noinspection PyTypeChecker
        context['fake_username'] = getattr(settings, 'EASYDJANGO_FAKE_AUTHENTICATION_USERNAME', None)
        # noinspection PyTypeChecker
        if hasattr(request, 'site'):
            context['request_site'] = request.site
            context['request_site_valid'] = request.site == host
        context['server_name'] = settings.SERVER_NAME
        context['server_name_valid'] = settings.SERVER_NAME == host
        context['debug'] = settings.DEBUG
        context['settings_providers'] = [p for p in merger.providers if p.is_valid()]
        return context


class LogLastLines(MonitoringCheck):
    template = 'easydjango/bootstrap3/monitoring/log_last_lines.html'

    def get_context(self, request):
        return {}


system_checks = [import_string(x)() for x in settings.EASYDJANGO_SYSTEM_CHECKS]


@never_cache
@login_required(login_url='login')
def system_state(request):
    if not request.user or not request.user.is_superuser:
        raise Http404
    components_values = [y.render(request) for y in system_checks]
    template_values = {'components': components_values}
    set_websocket_topics(request)
    return TemplateResponse(request, template='easydjango/bootstrap3/system_state.html',
                            context=template_values)
