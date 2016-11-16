# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import Group

__author__ = 'Matthieu Gallet'


_CACHED_GROUPS = {}


class DefaultGroupsRemoteUserBackend(RemoteUserBackend):

    def configure_user(self, user):
        """
        Configures a user after creation and returns the updated user.

        By default, returns the user unmodified; only add it to the default group.
        """
        for group_name in settings.DF_DEFAULT_GROUPS:
            if group_name not in _CACHED_GROUPS:
                _CACHED_GROUPS[group_name] = Group.objects.get_or_create(name=str(group_name))[0]
            user.groups.add(_CACHED_GROUPS[group_name])
        return user
