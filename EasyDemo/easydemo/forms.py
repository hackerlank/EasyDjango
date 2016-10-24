# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import forms
from easydjango.decorators import validate_form, everyone

__author__ = 'Matthieu Gallet'


@validate_form(path='validate', is_allowed_to=everyone)
class TestForm(forms.Form):
    email = forms.EmailField(label='Email', help_text='Please enter your e-mail')
    name = forms.CharField(label='Name', help_text='Please enter your name')
    age = forms.IntegerField(label='Age')
