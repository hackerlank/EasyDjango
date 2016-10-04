# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import subprocess

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from easydjango.decorators import connect, everyone
from easydjango.tasks import call, SERVER, BROADCAST, WINDOW

__author__ = 'Matthieu Gallet'


@connect(is_allowed_to=everyone, path='auth.check_user_creation')
def check_user_creation(request, username=None, email=None, password1=None, password2=None):
    user_model = get_user_model()
    # noinspection PyProtectedMember
    options = user_model._meta
    if username:
        for validator in options.get_field_by_name('username')[0].validators:
            try:
                validator(username)
            except ValidationError as e:
                call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='error', text=str(e))
                valid = False
                break
        else:
            valid = user_model.objects.filter(username=username).count() == 0
            if not valid:
                call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='error',
                     text=_('This username already exists.'))
        if valid:
            call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='success')
    if email:
        for validator in options.get_field_by_name('email')[0].default_validators:
            try:
                validator(email)
            except ValidationError as e:
                call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='error', text=str(e))
        else:
            call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='success')
    if password1 and password2:
        if password1 == password2:
            call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='success')
        else:
            call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='error', text=_('Passwords must match.'))



@connect(is_allowed_to=everyone, path='demo.print_sig1')
def print_sig1(request, content=''):
    subprocess.check_call(['say'] + content.split(' '))
    call(request, 'demo.print_sig2', to=[BROADCAST, SERVER], content="Test Signal")


@connect(is_allowed_to=everyone, path='demo.print_sig2')
def print_sig2(request, content=''):
    subprocess.check_call(['say'] + content.split(' '))
