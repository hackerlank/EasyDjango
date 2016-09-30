# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import subprocess

from easydjango.decorators import connect, everyone
from easydjango.tasks import call, SERVER, BROADCAST

__author__ = 'Matthieu Gallet'


@connect(is_allowed_to=everyone, path='demo.print_sig1')
def print_sig1(request, content=''):
    subprocess.check_call(['say'] + content.split(' '))
    call(request, 'demo.print_sig2', to=[BROADCAST, SERVER], content="Test Signal")


@connect(is_allowed_to=everyone, path='demo.print_sig2')
def print_sig2(request, content=''):
    subprocess.check_call(['say'] + content.split(' '))
