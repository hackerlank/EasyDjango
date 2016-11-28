# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import json
import mimetypes
import os
import warnings
from collections import OrderedDict

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.lru_cache import lru_cache
from django.utils.six import binary_type
from django.views.decorators.cache import never_cache
from djangofloor.decorators import REGISTERED_SIGNALS, REGISTERED_FUNCTIONS
from djangofloor.wsgi.window_info import WindowInfo
# noinspection PyProtectedMember
from djangofloor.tasks import _call_signal
from djangofloor.tasks import import_signals_and_functions, get_signal_decoder, get_signal_encoder, SERVER
from djangofloor.utils import RemovedInDjangoFloor110Warning

__author__ = 'Matthieu Gallet'


# noinspection PyUnusedLocal
def favicon(request):
    return HttpResponsePermanentRedirect('%sfavicon/favicon.ico' % settings.STATIC_URL)


def robots(request):
    current_site = get_current_site(request)
    base_url = add_domain(current_site.domain, '/', request.is_secure())[:-1]
    template_values = {'base_url': base_url}
    return TemplateResponse('djangofloor/robots.txt', template_values, content_type='text/plain')


@lru_cache()
def __get_js_mimetype():
    # noinspection PyTypeChecker
    if hasattr(settings, 'PIPELINE_MIMETYPES'):
        for (mimetype, ext) in settings.PIPELINE_MIMETYPES:
            if ext == '.js':
                return mimetype
    return 'text/javascript'


def read_file_in_chunks(fileobj, chunk_size=32768):
    """ read a file object in chunks of the given size.

    Return an iterator of data

    :param fileobj:
    :param chunk_size: max size of each chunk
    :type chunk_size: `int`
    """
    for data in iter(lambda: fileobj.read(chunk_size), b''):
        yield data

@never_cache
def signals(request):
    signal_request = WindowInfo.from_request(request)
    import_signals_and_functions()
    if settings.DF_PUBLIC_SIGNAL_LIST:
        valid_signal_names = list(REGISTERED_SIGNALS.keys())
        valid_function_names = list(REGISTERED_FUNCTIONS.keys())
    else:
        valid_signal_names = []
        for signal_name, list_of_connections in REGISTERED_SIGNALS.items():
            if any(x.is_allowed_to(signal_request) for x in list_of_connections):
                valid_signal_names.append(signal_name)
        valid_function_names = []
        for function_name, connection in REGISTERED_FUNCTIONS.items():
            if connection.is_allowed_to(signal_request):
                valid_function_names.append(function_name)

    function_names_dict = {}
    for name in valid_function_names:
        function_names_dict[name] = 'function(opts) { return $.df._wsCallFunction("%(name)s", opts); }' % {'name': name}
        name, sep, right = name.rpartition('.')
        while sep == '.':
            function_names_dict.setdefault(name, '{}')
            name, sep, right = name.rpartition('.')
    functions = OrderedDict()
    for key in sorted(function_names_dict):
        functions[key] = function_names_dict[key]

    protocol = 'wss' if settings.USE_SSL else 'ws'
    site_name = '%s:%s' % (settings.SERVER_NAME, settings.SERVER_PORT)

    # noinspection PyTypeChecker
    csrf_header_name = getattr(settings, 'CSRF_HEADER_NAME', 'HTTP_X_CSRFTOKEN')
    return TemplateResponse(request, 'djangofloor/signals.html',
                            {'SIGNALS': valid_signal_names,
                             'FUNCTIONS': functions,
                             'WEBSOCKET_HEARTBEAT': settings.WEBSOCKET_HEARTBEAT,
                             'WEBSOCKET_URL': '%s://%s%s' % (protocol, site_name, settings.WEBSOCKET_URL),
                             'CSRF_COOKIE_NAME': settings.CSRF_COOKIE_NAME,
                             'CSRF_HEADER_NAME': csrf_header_name[5:].replace('_', '-')},
                            content_type=__get_js_mimetype())


# noinspection PyUnusedLocal
def test_logging(request):
    x = 1/0
    return HttpResponse(x)


def send_file(filepath, mimetype=None, force_download=False):
    """Send a local file. This is not a Django view, but a function that is called at the end of a view.

    If `settings.USE_X_SEND_FILE` (mod_xsendfile is a mod of Apache), then return an empty HttpResponse with the
    correct header. The file is directly handled by Apache instead of Python.
    If `settings.X_ACCEL_REDIRECT_ARCHIVE` is defined (as a list of tuple (directory, alias_url)) and filepath is
    in one of the directories, return an empty HttpResponse with the correct header.
    This is only available with Nginx.

    Otherwise, return a StreamingHttpResponse to avoid loading the whole file in memory.

    :param filepath: absolute path of the file to send to the client.
    :param mimetype: MIME type of the file (returned in the response header)
    :param force_download: always force the client to download the file.
    :rtype: `StreamingHttpResponse` or `HttpResponse`
    """
    if mimetype is None:
        (mimetype, encoding) = mimetypes.guess_type(filepath)
        if mimetype is None:
            mimetype = 'text/plain'
    if isinstance(mimetype, binary_type):
        # noinspection PyTypeChecker
        mimetype = mimetype.decode('utf-8')
    filepath = os.path.abspath(filepath)
    if settings.USE_X_SEND_FILE:
        response = HttpResponse(content_type=mimetype)
        response['X-SENDFILE'] = filepath
    else:
        for dirpath, alias_url in settings.X_ACCEL_REDIRECT:
            if filepath.startswith(dirpath):
                response = HttpResponse(content_type=mimetype)
                response['Content-Disposition'] = 'attachment; filename={0}'.format(os.path.basename(filepath))
                response['X-Accel-Redirect'] = alias_url + filepath
                break
        else:
            # noinspection PyTypeChecker
            fileobj = open(filepath, 'rb')
            response = StreamingHttpResponse(read_file_in_chunks(fileobj), content_type=mimetype)
            response['Content-Length'] = os.path.getsize(filepath)
    if force_download or not (mimetype.startswith('text') or mimetype.startswith('image')):
        response['Content-Disposition'] = 'attachment; filename={0}'.format(os.path.basename(filepath))
    return response


# TODO remove the following functions

@never_cache
def signal_call(request, signal):
    """ Called by JS code when websockets are not available. Allow to call Python signals from JS.
    Arguments are passed in the request body, serialized as JSON.

    :param request: Django HTTP request
    :param signal: name of the called signal
    :type signal: :class:`str`
    """
    warnings.warn('djangofloor.views.signal_call is deprecated. Use websockets instead.',
                  RemovedInDjangoFloor110Warning)
    request.window_key = request.GET.get('window_key')
    if request.body:
        kwargs = json.loads(request.body.decode('utf-8'), cls=get_signal_decoder())
    else:
        kwargs = {}
    _call_signal(WindowInfo.from_request(request), signal_name=signal, to=SERVER,
                 kwargs=kwargs, from_client=True)
    return JsonResponse([], safe=False, encoder=get_signal_encoder())


# noinspection PyUnusedLocal
@never_cache
def get_signal_calls(request):
    """ Regularly called by JS code when websockets are not available. Allows Python code to call JS signals.

    The polling frequency is set with `WEBSOCKET_REDIS_EMULATION_INTERVAL` (in milliseconds).

    Return all signals called by Python code as a JSON-list
    """
    warnings.warn('djangofloor.views.get_signal_calls is deprecated. Use websockets instead.',
                  RemovedInDjangoFloor110Warning)
    return JsonResponse([], safe=False)


def index(request):
    warnings.warn('djangofloor.views.index is deprecated. Use class-based index view instead.',
                  RemovedInDjangoFloor110Warning)
    if settings.FLOOR_INDEX is not None:
        return HttpResponseRedirect(reverse(settings.FLOOR_INDEX))
    template_values = {}
    return TemplateResponse(request, 'djangofloor/index.html', template_values)
