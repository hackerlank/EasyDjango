# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import random

from django import forms

from easydjango.decorators import function, everyone, validate_form

__author__ = 'Matthieu Gallet'


@validate_form(path='validate', is_allowed_to=everyone)
class TestForm(forms.Form):
    email = forms.EmailField(label='email1')
    integer = forms.IntegerField(label='entier')
    name = forms.CharField(label='nom')


@function(path='test_function', is_allowed_to=everyone)
def test_function(request):
    # TODO to remove before release
    return 'Coucou : %d' % random.randint(0, 100)
