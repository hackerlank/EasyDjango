# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from argparse import ArgumentParser

from django.core.management import BaseCommand

from easydjango.conf.fields import ConfigField
from easydjango.conf.providers import IniConfigProvider
from easydjango.conf.settings import merger
from easydjango import __version__ as version
from django.utils.translation import ugettext as _, ugettext_lazy
__author__ = 'Matthieu Gallet'


class Command(BaseCommand):
    help = 'show the current configuration'

    def add_arguments(self, parser):
        assert isinstance(parser, ArgumentParser)
        parser.add_argument('action', default='show',
                            help=('"python": display the current config as Python module,\n'
                                  '"ini": display the current config as .ini file'))

    def handle(self, *args, **options):
        action = options['action']
        verbosity = options['verbosity']
        if action == 'python':
            self.stdout.write(self.style.SUCCESS('# ' + '-' * 80))
            self.stdout.write(self.style.SUCCESS(_('# EasyDjango version %(version)s') % {'version': version, }))
            self.stdout.write(self.style.SUCCESS('# Configuration providers:'))
            for provider in merger.providers:
                if provider.is_valid():
                    self.stdout.write(self.style.SUCCESS('#  - %s "%s"' % (provider.name, provider)))
                elif verbosity > 1:
                    self.stdout.write(self.style.ERROR('#  - %s "%s"' % (provider.name, provider)))
            self.stdout.write(self.style.SUCCESS('# ' + '-' * 80))
            setting_names = list(merger.raw_settings)
            setting_names.sort()
            for setting_name in setting_names:
                value = merger.settings[setting_name]
                self.stdout.write(self.style.SUCCESS('%s = %r' % (setting_name, value)))
                if verbosity <= 1:
                    continue
                for provider_name, raw_value in merger.raw_settings[setting_name].items():
                    self.stdout.write(self.style.WARNING('#   %s -> %r' % (provider_name or 'built-in', raw_value)))
        elif action == 'ini':
            if verbosity > 1:
                provider = merger.fields_provider
                self.stdout.write(self.style.SUCCESS('; list of fields in %s "%s"' % (provider.name, provider)))
            provider = IniConfigProvider()
            for config_field in merger.fields_provider.get_config_fields():
                assert isinstance(config_field, ConfigField)
                config_field.value = merger.settings[config_field.setting_name]
                provider.set_value(config_field)
            self.stdout.write(provider.to_str())

