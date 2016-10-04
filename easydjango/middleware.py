# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import base64

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.sessions.backends.base import VALID_KEY_CHARS
from django.core.exceptions import ImproperlyConfigured
from django.utils.crypto import get_random_string

__author__ = 'Matthieu Gallet'


class EasyDjangoMiddleware(RemoteUserMiddleware):
    """Like :class:`django.contrib.auth.middleware.RemoteUserMiddleware` but:

    * can use any header defined by the setting `EASYDJANGO_REMOTE_USER_HEADER`,
    * handle the HTTP_X_FORWARDED_FOR HTTP header (set the right client IP)
    * handle HTTP basic authentication
    * set response header for Internet Explorer (to use its most recent render engine)
    """
    remote_user_header = settings.EASYDJANGO_REMOTE_USER_HEADER

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):
        request.window_key = get_random_string(32, VALID_KEY_CHARS)

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

        if self.remote_user_header and self.remote_user_header in request.META:
            if not request.user.is_authenticated():
                self.remote_user_authentication(request)

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_response(self, request, response):
        response['X-UA-Compatible'] = 'IE=edge,chrome=1'
        return response

    def remote_user_authentication(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        username = request.META.get(self.remote_user_header)
        if not username or username == '(null)':  # special case due to apache2+auth_mod_kerb :-(
            return
        username, sep, domain = username.partition('@')
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
