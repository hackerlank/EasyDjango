# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import base64

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.sessions.backends.base import VALID_KEY_CHARS
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.http import HttpRequest
from django.utils import translation
from django.utils.crypto import get_random_string
from django.utils.translation import get_language_from_request

__author__ = 'Matthieu Gallet'


class EasyDjangoMiddleware(RemoteUserMiddleware):
    """Like :class:`django.contrib.auth.middleware.RemoteUserMiddleware` but:

    * can use any header defined by the setting `EASYDJANGO_REMOTE_USER_HEADER`,
    * handle the HTTP_X_FORWARDED_FOR HTTP header (set the right client IP)
    * handle HTTP basic authentication
    * set response header for Internet Explorer (to use its most recent render engine)
    """
    header = settings.EASYDJANGO_REMOTE_USER_HEADER
    if header:
        header = header.upper().replace('-', '_')

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        request.window_key = get_random_string(32, VALID_KEY_CHARS)
        request.has_websocket_topics = False
        request.remote_username = None

        if settings.USE_X_FORWARDED_FOR and 'HTTP_X_FORWARDED_FOR' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()

        if settings.USE_HTTP_BASIC_AUTH and 'HTTP_AUTHORIZATION' in request.META:
            authentication = request.META['HTTP_AUTHORIZATION']
            (authmeth, auth_data) = authentication.split(' ', 1)
            if 'basic' == authmeth.lower():
                auth_data = base64.b64decode(auth_data.strip()).decode('utf-8')
                username, password = auth_data.split(':', 1)
                user = auth.authenticate(username=username, password=password)
                if user:
                    request.user = user
                    auth.login(request, user)
        # noinspection PyTypeChecker
        username = getattr(settings, 'EASYDJANGO_FAKE_AUTHENTICATION_USERNAME', None)
        if username and settings.DEBUG:
            request.META[self.header] = username

        if self.header and self.header in request.META:
            if not request.user.is_authenticated():
                self.remote_user_authentication(request)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_response(self, request, response):
        response['X-UA-Compatible'] = 'IE=edge,chrome=1'
        return response

    def remote_user_authentication(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        # noinspection PyTypeChecker
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        remote_username = request.META.get(self.header)
        if not remote_username or remote_username == '(null)':  # special case due to apache2+auth_mod_kerb :-(
            return
        username = self.format_remote_username(remote_username)
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            if request.user.get_username() == self.clean_username(username, request):
                return
            else:
                # An authenticated user is associated with the request, but
                # it does not match the authorized user in the header.
                self._remove_invalid_user(request)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(remote_user=username)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
            request.remote_username = remote_username

    # noinspection PyMethodMayBeStatic
    def format_remote_username(self, remote_username):
        return remote_username.partition('@')[0]


class WindowInfoMiddleware(object):
    def from_request(self, request, window_info):
        pass

    def new_window_info(self, window_info):
        pass

    def to_dict(self, window_info):
        return {}

    def from_dict(self, window_info, values):
        pass

    def get_context(self, window_info):
        return {}

    def install_methods(self, window_info_cls):
        pass


class WindowKeyMiddleware(WindowInfoMiddleware):
    def from_request(self, request, window_info):
        # noinspection PyTypeChecker
        window_info.window_key = getattr(request, 'window_key', None)

    def new_window_info(self, window_info):
        window_info.window_key = None

    def to_dict(self, window_info):
        return {'window_key': window_info.window_key}

    def from_dict(self, window_info, values):
        window_info.window_key = values.get('window_key')

    def get_context(self, window_info):
        # noinspection PyTypeChecker
        return {'ed_ws_token': getattr(window_info, 'window_key')}


class DjangoAuthMiddleware(WindowInfoMiddleware):
    def from_request(self, request, window_info):
        assert isinstance(request, HttpRequest)
        # auth and perms part
        # noinspection PyTypeChecker
        user = getattr(request, 'user', None)
        window_info._user = user
        window_info._perms = None
        window_info._template_perms = None
        window_info.user_agent = request.META.get('HTTP_USER_AGENT', '')
        if user and user.is_authenticated():
            window_info.user_pk = user.pk
            window_info.username = user.get_username()
            window_info.is_superuser = user.is_superuser
            window_info.is_staff = user.is_staff
            window_info.is_active = user.is_active
        else:
            window_info.user_pk = None
            window_info.username = None
            window_info.is_superuser = False
            window_info.is_staff = False
            window_info.is_active = False

    def new_window_info(self, window_info):
        window_info._user = None
        window_info._perms = None
        window_info._template_perms = None
        window_info.user_agent = ''
        window_info.user_pk = None
        window_info.username = None
        window_info.is_superuser = False
        window_info.is_staff = False
        window_info.is_active = False

    def to_dict(self, window_info):
        # noinspection PyProtectedMember
        return {'user_pk': window_info.user_pk, 'username': window_info.username,
                'is_superuser': window_info.is_superuser,
                'is_staff': window_info.is_staff, 'is_active': window_info.is_active,
                'perms': list(window_info._perms) if isinstance(window_info._perms, set) else None,
                'user_agent': window_info.user_agent}

    def from_dict(self, window_info, values):
        window_info._user = None
        window_info.user_pk = values.get('user_pk')
        window_info.username = values.get('username')
        window_info.is_superuser = values.get('is_superuser')
        window_info.is_staff = values.get('is_staff')
        window_info.is_active = values.get('is_active')
        window_info._perms = set(values['perms']) if values.get('perms') is not None else None
        window_info._template_perms = None
        window_info.user_agent = values.get('user_agent')

    def get_context(self, window_info):
        return {'ed_user': window_info.user, 'ed_user_agent': window_info.META.get('HTTP_USER_AGENT', ''),}

    def install_methods(self, window_info_cls):
        def get_user(req):
            # noinspection PyProtectedMember
            if req._user or req.user_pk is None:
                # noinspection PyProtectedMember
                return req._user
            users = list(get_user_model().objects.filter(pk=req.user_pk)[0:1])
            if users:
                req._user = users[0]
                return req._user
            return None

        def has_perm(req, perm):
            """ return true is the user has the required perm.

            >>> from easydjango.request import WindowInfo
            >>> r = WindowInfo.from_dict({'username': 'username', 'perms':['app_label.codename']})
            >>> r.has_perm('app_label.codename')
            True

            :param req: WindowInfo
            :param perm: name of the permission  ("app_label.codename")
            :return: True if the user has the required perm
            :rtype: :class:`bool`
            """
            return perm in req.perms

        def get_perms(req):
            """:class:`set` of all perms of the user (set of "app_label.codename")"""
            if not req.user_pk:
                return set()
            elif req._perms is not None:
                return req._perms
            from django.contrib.auth.models import Permission
            if req.is_superuser:
                query = Permission.objects.all()
            else:
                query = Permission.objects.filter(Q(user__pk=req.user_pk) | Q(group__user__pk=req.user_pk))
            req._perms = set('%s.%s' % p for p in
                             query.select_related('content_type').values_list('content_type__app_label', 'codename'))
            return req._perms

        # noinspection PyProtectedMember
        def get_template_perms(req):
            """:class:`dict` of perms, to be used in templates.

            Example:

            .. code-block:: html

                {% if request.template_perms.app_label.codename %}...{% endif %}

            """
            if req._template_perms is not None:
                return req._template_perms
            result = {}
            for perm in req.perms:
                app_name, sep, codename = perm.partition('.')
                result.setdefault(app_name, {})[codename] = True
            req._template_perms = result
            return result

        window_info_cls.user = property(get_user)
        window_info_cls.has_perm = has_perm
        window_info_cls.perms = property(get_perms)
        window_info_cls.template_perms = property(get_template_perms)


class Djangoi18nMiddleware(WindowInfoMiddleware):

    def from_request(self, request, window_info):
        # noinspection PyTypeChecker
        if getattr(request, 'session', None):
            window_info.language_code = get_language_from_request(request)
        else:
            window_info.language_code = settings.LANGUAGE_CODE

    def new_window_info(self, window_info):
        window_info.language_code = None

    def to_dict(self, window_info):
        return {'language_code': window_info.language_code}

    def from_dict(self, window_info, values):
        window_info.language_code = values.get('language_code')

    def get_context(self, window_info):
        return {'LANGUAGES': settings.LANGUAGES,
                'LANGUAGE_CODE': window_info.language_code,
                'LANGUAGE_BIDI': translation.get_language_bidi(), }
