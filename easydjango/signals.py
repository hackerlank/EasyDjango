# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging

from easydjango.decorators import signal, is_staff
from easydjango.tasks import scall, WINDOW

__author__ = 'Matthieu Gallet'
logger = logging.getLogger('easydjango.websocket')


@signal(path='ed.monitoring.check_ws', is_allowed_to=is_staff)
def check_websockets(window_info):
    logger.info('websocket OK')
    scall(window_info, 'ed.monitoring.checked_ws', to=[WINDOW])
