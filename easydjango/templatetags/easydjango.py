# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import template
from django.utils.safestring import mark_safe

from easydjango.websockets.wsgi_server import signer

__author__ = 'Matthieu Gallet'
register = template.Library()


@register.simple_tag(takes_context=True)
def init_websocket(context):
    ws_token = context['ed_ws_token']
    signed_token = signer.sign(ws_token)
    script = '$(function () { $.ed._window_token = "%s"; });' % signed_token
    return mark_safe('<script type="application/javascript">%s</script>' % script)
