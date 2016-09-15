# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib import admin
from django.contrib.admin import site

from easydjango.models import Notification

__author__ = 'Matthieu Gallet'


class NotificationAdmin(admin.ModelAdmin):
    pass


site.register(Notification, NotificationAdmin)
