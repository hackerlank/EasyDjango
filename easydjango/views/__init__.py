# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import mimetypes
import os

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import add_domain
from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.http import StreamingHttpResponse
from django.template.response import TemplateResponse
from django.utils.lru_cache import lru_cache
from django.utils.six import binary_type

from easydjango.decorators import REGISTERED_SIGNALS, REGISTERED_FUNCTIONS
from easydjango.request import WindowInfo
from easydjango.tasks import import_signals_and_functions

__author__ = 'Matthieu Gallet'


# noinspection PyUnusedLocal
def favicon(request):
    return HttpResponsePermanentRedirect('%sfavicon/favicon.ico' % settings.STATIC_URL)


def robots(request):
    current_site = get_current_site(request)
    base_url = add_domain(current_site.domain, '/', request.is_secure())[:-1]
    template_values = {'base_url': base_url}
    return TemplateResponse('easydjango/robots.txt', template_values, content_type='text/plain')


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


def signals(request):
    signal_request = WindowInfo.from_request(request)
    import_signals_and_functions()
    if settings.WS4REDIS_PUBLIC_WS_LIST:
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
    # noinspection PyTypeChecker
    csrf_header_name = getattr(settings, 'CSRF_HEADER_NAME', 'HTTP_X_CSRFTOKEN')
    return TemplateResponse(request, 'easydjango/signals.html',
                            {'SIGNALS': valid_signal_names,
                             'FUNCTIONS': valid_function_names,
                             'WS4REDIS_HEARTBEAT': settings.WS4REDIS_HEARTBEAT,
                             'WEBSOCKET_URL': 'ws://localhost:9000' + settings.WEBSOCKET_URL,
                             'CSRF_COOKIE_NAME': settings.CSRF_COOKIE_NAME,
                             'CSRF_HEADER_NAME': csrf_header_name[5:].replace('_', '-')},
                            content_type=__get_js_mimetype())


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
