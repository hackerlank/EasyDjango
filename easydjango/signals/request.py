# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.db.models import Q
from django.utils.functional import cached_property

__author__ = 'Matthieu Gallet'


class SignalRequest(object):
    """ Store the username and the window key and must be supplied to any Python signal call.

    Can be constructed from a standard :class:`django.http.HttpRequest`.

    :param username: should be User.username
    :type username: :class:`str`
    :param window_key: a string value specific to each opened browser window/tab
    :type window_key: :class:`str`
    :param user_pk: primary key of the user (for easy ORM queries)
    :type user_pk: :class:`int`
    :param is_superuser: is the user a superuser?
    :type is_superuser: :class:`bool`
    :param is_staff: belongs the user to the staff?
    :type is_staff: :class:`bool`
    :param is_active: is the user active?
    :type is_active: :class:`bool`
    :param perms: list of "app_name.permission_name" (optional)
    :type perms: :class:`list`
    """
    def __init__(self, username, window_key, user_pk=None, is_superuser=False, is_staff=False, is_active=False,
                 perms=None):
        self.username = username
        self.user_pk = user_pk
        self.is_superuser = is_superuser
        self.is_staff = is_staff
        self.is_active = is_active
        self._perms = set(perms) if perms is not None else None
        self.window_key = window_key

    @classmethod
    def from_user(cls, user):
        """ Create a :class:`djangofloor.decorators.SignalRequest` from a valid User. The SessionKey is set to `None`

        :param user: any Django user
        :type user: :class:`django.contrib.auth.models.AbstractUser`
        :rtype: :class:`djangofloor.decorators.SignalRequest`
        """
        return cls(user.get_username(), None, user_pk=user.pk, is_superuser=user.is_superuser, is_staff=user.is_staff,
                   is_active=user.is_active)

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def to_dict(self):
        """Convert this :class:`djangofloor.decorators.SignalRequest` to a :class:`dict` which can be provided to JSON.

        :return: a dict ready to be serialized in JSON
        :rtype: :class:`dict`
        """
        result = {}
        result.update(self.__dict__)
        if isinstance(self._perms, set):
            result['perms'] = list(self._perms)
        else:
            result['perms'] = None
        del result['_perms']
        return result

    def has_perm(self, perm):
        """ return true is the user has the required perm.

        >>> r = SignalRequest('username', perms=['app_label.codename'])
        >>> r.has_perm('app_label.codename')
        True

        :param perm: name of the permission  ("app_label.codename")
        :return: True if the user has the required perm
        :rtype: :class:`bool`
        """
        return perm in self.perms

    @property
    def perms(self):
        """:class:`set` of all perms of the user (set of "app_label.codename")"""
        if not self.user_pk:
            return set()
        elif self._perms is not None:
            return self._perms
        from django.contrib.auth.models import Permission
        if self.is_superuser:
            query = Permission.objects.all()
        else:
            query = Permission.objects.filter(Q(user__pk=self.user_pk) | Q(group__user__pk=self.user_pk))
        self._perms = set('%s.%s' % p for p in
                          query.select_related('content_type').values_list('content_type__app_label', 'codename'))
        return self._perms

    @cached_property
    def template_perms(self):
        """:class:`dict` of perms, to be used in templates.

        Example:

        .. code-block:: html

            {% if request.template_perms.app_label.codename %}...{% endif %}

        """
        result = {}
        for perm in self.perms:
            app_name, sep, codename = perm.partition('.')
            result.setdefault(app_name, {})[codename] = True
        return result

    @classmethod
    def from_request(cls, request):
        """ return a :class:`djangofloor.decorators.SignalRequest` from a :class:`django.http.HttpRequest`.

        If the request already is a :class:`djangofloor.decorators.SignalRequest`,
        then it is returned as-is (not copied!).

        :param request: standard Django request
        :type request: :class:`django.http.HttpRequest` or :class:`djangofloor.decorators.SignalRequest`
        :return: a valid request
        :rtype: :class:`djangofloor.decorators.SignalRequest`
        """
        if isinstance(request, SignalRequest):
            return request
        # noinspection PyTypeChecker
        window_key = request.window_key if hasattr(request, 'window_key') else None
        # noinspection PyUnresolvedReferences,PyTypeChecker
        user = request.user if hasattr(request, 'user') and request.user else None
        if user and user.is_authenticated():
            return cls(username=user.get_username(), window_key=window_key,
                       user_pk=user.pk, is_superuser=user.is_superuser, is_staff=user.is_staff,
                       is_active=user.is_active)
        return cls(None, window_key=window_key)
