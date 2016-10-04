# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import random

from easydjango.decorators import function, everyone

__author__ = 'Matthieu Gallet'


@function(path='test_function', is_allowed_to=everyone)
def test_function(request):
    return 'Coucou : %d' % random.randint(0, 100)
