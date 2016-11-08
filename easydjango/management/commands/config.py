# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from argparse import ArgumentParser

from django.core.management import BaseCommand

from easydjango.conf.fields import ConfigField
from easydjango.conf.providers import IniConfigProvider
from easydjango.conf.settings import merger
from easydjango import __version__ as version
from django.utils.translation import ugettext as _
__author__ = 'Matthieu Gallet'


class Command(BaseCommand):
    help = 'show the current configuration.' \
           'Can display as python file ("config python") or as .ini file ("config ini"). Use -v 2 to display more info.'

    def add_arguments(self, parser):
        assert isinstance(parser, ArgumentParser)
        parser.add_argument('action', default='show',
                            help=('"python": display the current config as Python module,\n'
                                  '"ini": display the current config as .ini file'))

    def handle(self, *args, **options):
        action = options['action']
        verbosity = options['verbosity']
        if action == 'python':
            self.stdout.write(self.style.NOTICE('# ' + '-' * 80))
            self.stdout.write(self.style.NOTICE(_('# EasyDjango version %(version)s') % {'version': version, }))
            self.stdout.write(self.style.NOTICE('# Configuration providers:'))
            for provider in merger.providers:
                if provider.is_valid():
                    self.stdout.write(self.style.NOTICE('#  - %s "%s"' % (provider.name, provider)))
                elif verbosity > 1:
                    self.stdout.write(self.style.ERROR('#  - %s "%s"' % (provider.name, provider)))
            self.stdout.write(self.style.NOTICE('# ' + '-' * 80))
            setting_names = list(merger.raw_settings)
            setting_names.sort()
            for setting_name in setting_names:
                if setting_name not in merger.settings:
                    continue
                value = merger.settings[setting_name]
                self.stdout.write(self.style.NOTICE('%s = %r' % (setting_name, value)))
                if verbosity <= 1:
                    continue
                for provider_name, raw_value in merger.raw_settings[setting_name].items():
                    self.stdout.write(self.style.WARNING('#   %s -> %r' % (provider_name or 'built-in', raw_value)))
        elif action == 'ini':
            if verbosity >= 3:
                provider = merger.fields_provider
                self.stdout.write(self.style.NOTICE('; list of fields in %s "%s"' % (provider.name, provider)))
            for provider in merger.providers:
                if not isinstance(provider, IniConfigProvider):
                    continue
                elif provider.is_valid():
                    self.stdout.write(self.style.NOTICE('#  - %s "%s"' % (provider.name, provider)))
                elif verbosity >= 2:
                    self.stdout.write(self.style.ERROR('#  - %s "%s"' % (provider.name, provider)))
            provider = IniConfigProvider()
            for config_field in merger.fields_provider.get_config_fields():
                assert isinstance(config_field, ConfigField)
                if config_field.setting_name not in merger.settings:
                    continue
                config_field.value = merger.settings[config_field.setting_name]
                provider.set_value(config_field)
            self.stdout.write(provider.to_str())

