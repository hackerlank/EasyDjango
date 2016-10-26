# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging
import time
from easydjango.decorators import signal, everyone
from easydjango.tasks import scall, BROADCAST, SERVER

__author__ = 'Matthieu Gallet'
logger = logging.getLogger('django.request')


# noinspection PyUnusedLocal
@signal(is_allowed_to=everyone, path='demo.slow_signal', queue='slow')
def slow_signal(window_info, content=''):
    logger.warn('wait for 10 seconds…')
    time.sleep(10)
    logger.warn('10 seconds: done.')
    scall(window_info, 'demo.print_sig2', to=[BROADCAST, SERVER], content='slow result')


@signal(is_allowed_to=everyone, path='demo.print_sig1')
def print_sig1(window_info, content=''):
    logger.debug('Debug log message [%r]' % content)
    logger.info('Debug info message [%r]' % content)
    logger.warn('Debug warn message [%r]' % content)
    logger.error('Debug error message [%r]' % content)
    scall(window_info, 'demo.print_sig2', to=[BROADCAST, SERVER], content=content)


@signal(is_allowed_to=everyone, path='demo.print_sig2')
def print_sig2(window_info, content=''):
    scall(window_info, 'notify', to=[BROADCAST, SERVER], content="Server notification [%r]" % content,
          level='warning', timeout=2, style='notification')
