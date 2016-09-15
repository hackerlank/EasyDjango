# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

__author__ = 'Matthieu Gallet'


class Notification(models.Model):
    title = models.CharField(_('Title'), max_length=255, blank=True, default='')
    content = models.TextField(_('Content'), blank=True, default='')
    is_active = models.BooleanField(_('Is active?'), default=True, blank=True, db_index=True)
    not_before = models.DateTimeField(_('Do not display before'), db_index=True)
    not_after = models.DateTimeField(_('Do not display after'), db_index=True)
    auto_hide_seconds = models.IntegerField(_('Automatically hide after (in seconds, 0 means no auto-hide)'),
                                            blank=True, default=0)
    author = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, db_index=True,
                                    related_name='notification_author',
                                    verbose_name=_('Users that should read this message'))
    destination_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, db_index=True,
                                               verbose_name=_('Users that should read this message'))


class NotificationRead(models.Model):
    notification = models.ForeignKey(Notification)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User that read this notification'),
                             db_index=True)
    read_time = models.DateTimeField(_('read time'), auto_now_add=True)
