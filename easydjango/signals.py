# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from easydjango.signals.connection import everyone
from easydjango.signals.decorators import connect
from easydjango.tasks import call, SERVER, BROADCAST

__author__ = 'Matthieu Gallet'


@connect(is_allowed_to=everyone, path='demo.print_sig')
def print_sig(request, content):
    print("[[%s]]" % content)
    call(request, 'demo', to=[BROADCAST, SERVER], html="test")
