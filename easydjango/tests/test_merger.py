# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from collections import OrderedDict

from django.test import TestCase

from easydjango.conf.merger import SettingMerger
from easydjango.conf.providers import DictProvider

__author__ = 'Matthieu Gallet'


class TestSettingMerger(TestCase):

    def test_priority(self):
        merger = SettingMerger(None, [DictProvider({'X': 1}), DictProvider({'X': 2})],
                               extra_values={'PROJECT_NAME': 'test'})
        merger.process()
        self.assertEqual({'X': 2, 'PROJECT_NAME': 'test'}, merger.settings)
        self.assertEqual(OrderedDict({None: 'test'}), merger.raw_settings['PROJECT_NAME'])
        self.assertEqual(OrderedDict([("dict({'X': 1})", 1), ("dict({'X': 2})", 2)]), merger.raw_settings['X'])

    def test_parse(self):
        merger = SettingMerger(None, [DictProvider({'X': 1, 'Y': 'x{X}'}), DictProvider({'X': 2})],
                               extra_values={'PROJECT_NAME': 'test'})
        merger.process()
        self.assertEqual({'X': 2, 'Y': 'x2', 'PROJECT_NAME': 'test'}, merger.settings)

    def test_loop(self):
        merger = SettingMerger(None, [DictProvider({'X': '{Y}', 'Y': '{Z}', 'Z': '{X}'})],
                               extra_values={'PROJECT_NAME': 'test'})
        self.assertRaises(ValueError, merger.process)
