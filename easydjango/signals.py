# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging
import subprocess

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from easydjango.decorators import signal, everyone, is_staff
from easydjango.tasks import call, SERVER, BROADCAST, WINDOW

__author__ = 'Matthieu Gallet'
logger = logging.getLogger('django.request')


@signal(path='ed.monitoring.check_ws', is_allowed_to=is_staff)
def check_websockets(request):
    call(request, 'ed.monitoring.checked_ws', to=[WINDOW])


@signal(is_allowed_to=everyone, path='auth.check_user_creation')
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
                call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='erro#r', text=str(e))
        else:
            call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='success')
    if password1 and password2:
        if password1 == password2:
            call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='success')
        else:
            call(request, 'ed.fields.state', to=[WINDOW], field_id=None, level='error', text=_('Passwords must match.'))


@signal(is_allowed_to=everyone, path='demo.print_sig1')
def print_sig1(request, content=''):
    logger.debug('Debug log message')
    logger.info('Debug info message')
    logger.warn('Debug warn message')
    logger.error('Debug error message')
    call(request, 'demo.print_sig2', to=[BROADCAST, SERVER], content="Test Signal")


@signal(is_allowed_to=everyone, path='demo.print_sig2')
def print_sig2(request, content=''):
    call(request, 'notify', to=[BROADCAST, SERVER], content="Server notification",
         level='warning', timeout=2, style='notification')
