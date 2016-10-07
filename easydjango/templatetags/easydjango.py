# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import template
from django.conf import settings
from django.templatetags.static import PrefixNode, StaticNode
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.six.moves.urllib.parse import urljoin, urlparse

from easydjango.websockets.wsgi_server import signer

__author__ = 'Matthieu Gallet'
register = template.Library()


@register.simple_tag(takes_context=True)
def init_websocket(context):
    ws_token = context['ed_ws_token']
    signed_token = signer.sign(ws_token)
    protocol = 'wss' if settings.USE_SSL else 'ws'
    site_name = '%s:%s' % (settings.SERVER_NAME, settings.SERVER_PORT)
    script = '$(document).ready(function() { $.ed._wsConnect("%s://%s%s?token=%s"); });' % \
             (protocol, site_name,  settings.WEBSOCKET_URL, signed_token)
    init_value = '<script type="application/javascript">%s</script>' % script
    init_value += '<script type="text/javascript" src="%s" charset="utf-8"></script>' % reverse('signals')
    return mark_safe(init_value)


class MediaNode(StaticNode):

    @classmethod
    def handle_simple(cls, path):
        return urljoin(PrefixNode.handle_simple('MEDIA_URL'), path)


@register.tag('media')
def do_media(parser, token):
    """
    Joins the given path with the MEDIA_URL setting.

    Usage::

        {% media path [as varname] %}

    Examples::

        {% media "myapp/css/base.css" %}
        {% media variable_with_path %}
        {% media "myapp/css/base.css" as admin_base_css %}
        {% media variable_with_path as varname %}

    """
    return MediaNode.handle_token(parser, token)


def media(path):
    return MediaNode.handle_simple(path)


@register.simple_tag
def fontawesome_icon(name, large=False, fixed=False, spin=False, li=False, rotate=None, border=False, color=None):
    if isinstance(large, int) and 2 <= large <= 5:
        large = ' fa-%dx' % large
    elif large:
        large = ' fa-lg'
    else:
        large = ''
    return mark_safe('<i class="fa fa-{name}{large}{fixed}{spin}{li}{rotate}{border}"{color}></i>'.format(
        name=name,
        large=large,
        fixed=' fa-fw' if fixed else '',
        spin=' fa-spin' if spin else '',
        li=' fa-li' if li else '',
        rotate=' fa-rotate-%s' % str(rotate) if rotate else '',
        border=' fa-border' if border else '',
        color='style="color:%s;"' % color if color else ''
    ))
