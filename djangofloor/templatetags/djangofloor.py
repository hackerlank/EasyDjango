# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import warnings

from django import template
from django.conf import settings
from django.template import Context
from django.templatetags.static import PrefixNode, StaticNode
from django.urls import reverse
from django.utils.encoding import force_text
# noinspection PyProtectedMember
from django.utils.html import _js_escapes
from django.utils.safestring import mark_safe
# noinspection PyUnresolvedReferences
from django.utils.six.moves.urllib.parse import urljoin, urlparse
from djangofloor.utils import RemovedInDjangoFloor110Warning
from djangofloor.wsgi.wsgi_server import signer

__author__ = 'Matthieu Gallet'
register = template.Library()


@register.simple_tag(takes_context=True)
def df_init_websocket(context):
    if not context.get('df_has_ws_topics'):
        return ''
    ws_token = context['df_window_key']
    signed_token = signer.sign(ws_token)
    protocol = 'wss' if settings.USE_SSL else 'ws'
    site_name = '%s:%s' % (settings.SERVER_NAME, settings.SERVER_PORT)
    script = '$(document).ready(function() { $.df._wsConnect("%s://%s%s?token=%s"); });' % \
             (protocol, site_name, settings.WEBSOCKET_URL, signed_token)
    init_value = '<script type="application/javascript">%s</script>' % script
    init_value += '<script type="text/javascript" src="%s" charset="utf-8"></script>' % reverse('df:signals')
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


@register.filter(name='df_level')
def df_level(value, bounds='80:95'):
    # noinspection PyTypeChecker
    warning, error = [float(x) for x in bounds.split(':')]
    if value < warning <= error or error <= warning < value:
        return 'success'
    elif warning <= value < error or error < value <= warning:
        return 'warning'
    return 'danger'


@register.simple_tag(takes_context=True)
def df_messages(context, style='banner'):
    """
    Show django.contrib.messages Messages in Metro alert containers.
    In order to make the alerts dismissable (with the close button),
    we have to set the jquery parameter too when using the
    bootstrap_javascript tag.
    Uses the template ``bootstrap3/messages.html``.
    **Tag name**::
        df_messages
    **Parameters**:
        style: "notification", "banner", "modal" or "system"
    **Usage**::
        {% df_messages style='banner' %}
    **Example**::
        {% df_messages style='notification' %}
    """

    if context and isinstance(context, Context):
        context = context.flatten()

    def message_level(msg):
        for (tag, bound) in (('danger', 40), ('warning', 30), ('success', 25)):
            if msg.level >= bound:
                return tag
        return 'info'
    result = '<script type="text/javascript">\n'
    for message in context.get('messages', []):
        result += '$.df.call("notify", {style: "%s", level: "%s", content: "%s"});\n' \
                  % (style, message_level(message), force_text(message).translate(_js_escapes))
    get_notifications = context.get('df_get_notifications', lambda: [])
    values = get_notifications()
    for notification in values:
        result += '$.df.call("notify", {style: "%s", level: "%s", content: "%s", timeout: %s, title: "%s"});\n' \
                  % (notification.display_mode,
                     notification.level,
                     notification.content.translate(_js_escapes),
                     notification.auto_hide_seconds * 1000,
                     notification.title)
    result += '</script>'
    return mark_safe(result)


@register.simple_tag(takes_context=False)
def df_deprecation(value):
    warnings.warn(value, RemovedInDjangoFloor110Warning)


# TODO remove the following functions
@register.simple_tag(takes_context=True)
def df_window_key(context):
    warnings.warn('df_window_key template tag has been replaced by df_init_websocket', RemovedInDjangoFloor110Warning)
    return df_init_websocket(context)


@register.filter
def df_underline(value, kind='='):
    warnings.warn('df_underline template tag will be removed', RemovedInDjangoFloor110Warning)
    return kind * len(value)


@register.filter
def df_urlparse(value, component='hostname'):
    warnings.warn('df_urlparse template tag will be removed', RemovedInDjangoFloor110Warning)
    x, sep, y = value.partition('://')
    if sep != '://':
        value = 'scheme://%s' % value
    elif not x:
        value = 'scheme%s' % value
    return getattr(urlparse(value), component)


@register.filter
def df_inivalue(value):
    warnings.warn('df_inivalue template tag will be removed', RemovedInDjangoFloor110Warning)
    if not value:
        return ''
    return mark_safe('\n    '.join(value.splitlines()))
