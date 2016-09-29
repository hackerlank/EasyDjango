# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

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
    return mark_safe('<script type="application/javascript">%s</script>' % script)
