# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _

__author__ = 'Matthieu Gallet'


class Notification(models.Model):
    ANY = 0
    AUTHENTICATED = 1
    SELECTED_GROUPS_OR_USERS = 2
    SYSTEM = 'system'
    NOTIFICATION = 'notification'
    MODAL = 'modal'
    POPUP = 'popup'
    BANNER = 'banner'
    SUCCESS = 'success'
    WARNING = 'warning'
    INFO = 'info'
    ALERT = 'alert'

    content = models.TextField(_('Content'), blank=True, default='')
    title = models.CharField(_('Title'), max_length=255, blank=True, default='')
    icon = models.FileField(_('Icon'), max_length=255, blank=True, null=True, default=None,
                            upload_to='notification_icons')
    is_active = models.BooleanField(_('Is active?'), default=True, blank=True, db_index=True)
    not_before = models.DateTimeField(_('Do not display before'), db_index=True)
    not_after = models.DateTimeField(_('Do not display after'), db_index=True)
    level = models.CharField(_('Level'), max_length=10, default=INFO,
                             choices=((SUCCESS, _('Success')), (INFO, _('Info')),
                                      (WARNING, _('Warning')), (ALERT, _('Alert'))))
    auto_hide_seconds = models.IntegerField(_('Automatically hide after (in seconds, 0 means no auto-hide)'),
                                            blank=True, default=0)
    author = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, db_index=True,
                                    related_name='notification_author',
                                    verbose_name=_('Users that should read this message'))
    display_mode = models.CharField(_('Display mode'), max_length=20, default=NOTIFICATION,
                                    choices=(
                                             (NOTIFICATION, _('HTML notification')),
                                             # (MODAL, _('Blocking (modal) window')),
                                             (SYSTEM, _('System notification')),
                                             (BANNER, _('Screen-wide banner')),
                                             # (POPUP, _('Popup')),
                                    ))
    broadcast_mode = models.IntegerField(_('Broadcast mode'), db_index=True, blank=True,
                                         choices=((ANY, _('Any visitor (using cookies)')),
                                                  (AUTHENTICATED, _('Any authenticated users')),
                                                  (SELECTED_GROUPS_OR_USERS, _('Selected groups and users'))),
                                         default=SELECTED_GROUPS_OR_USERS)
    destination_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, db_index=True,
                                               verbose_name=_('Users that should read this message'))
    destination_groups = models.ManyToManyField(Group, blank=True, db_index=True,
                                                verbose_name=_('Groups of users that should read this message'))


class NotificationRead(models.Model):
    notification = models.ForeignKey(Notification)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User that read this notification'),
                             db_index=True)
    read_time = models.DateTimeField(_('read time'), auto_now_add=True)
