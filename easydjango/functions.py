# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import random

from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.http import QueryDict

from easydjango.decorators import function, everyone, validate_form, is_authenticated

__author__ = 'Matthieu Gallet'


@function(path='easydjango_validate_set_password', is_allowed_to=is_authenticated)
def validate_set_password_form(request, data=None):
    query_dict = QueryDict('', mutable=True)
    for obj in data:
        query_dict.update({obj['name']: obj['value']})
    form = SetPasswordForm(request.user, query_dict)
    valid = form.is_valid()
    return {'valid': valid, 'errors': {f: e.get_json_data(escape_html=False) for f, e in form.errors.items()},
            'help_texts': {f: e.help_text for (f, e) in form.fields.items() if e.help_text}}


@validate_form(path='validate', is_allowed_to=everyone)
class TestForm(forms.Form):
    email = forms.EmailField(label='Email', help_text='Please enter your e-mail')
    name = forms.CharField(label='Name', help_text='Please enter your name')
    age = forms.IntegerField(label='Age')


# noinspection PyUnusedLocal
@function(path='test_function', is_allowed_to=everyone)
def test_function(request):
    # TODO to remove before release
    return 'Coucou : %d' % random.randint(0, 100)
