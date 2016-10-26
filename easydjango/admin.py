# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib import admin
from django.contrib.admin import site
from django.template.defaultfilters import truncatewords
from django.utils.translation import ugettext_lazy as _

from easydjango.models import Notification, NotificationRead

__author__ = 'Matthieu Gallet'


class NotificationAdmin(admin.ModelAdmin):

    def title_short(self, obj):
        if obj.title:
            return truncatewords(obj.title, 10)
        return '-'
    title_short.short_description = _('Title')

    def content_short(self, obj):
        if obj.content:
            return truncatewords(obj.content, 10)
        return '-'
    content_short.short_description = _('Content')

    list_display = ('title_short', 'content_short', 'is_active', 'not_before', 'not_after', 'level',
                    'auto_hide_seconds', 'display_mode', 'broadcast_mode', 'repeat_count')


site.register(Notification, NotificationAdmin)
site.register(NotificationRead)
