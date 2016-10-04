# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

__author__ = 'Matthieu Gallet'

register = template.Library()


@register.simple_tag(takes_context=False)
def javascript(key):
    filenames = settings.PIPELINE['JAVASCRIPT'][key]['source_filenames']
    context = {'type': 'text/javascript', 'charset': 'utf-8'}
    context.update(settings.PIPELINE['STYLESHEETS'][key].get('extra_context', {}))
    extra = ' '.join('%s="%s"' % x for x in context.items())

    def fmt(filename):
        return '<script src="%s%s" %s></script>' % (settings.STATIC_URL, filename, extra)
    result = '\n'.join([fmt(x) for x in filenames])
    return mark_safe(result)


@register.simple_tag(takes_context=False)
def stylesheet(key):
    filenames = settings.PIPELINE['STYLESHEETS'][key]['source_filenames']
    context = {'type': 'text/css', 'rel': 'stylesheet'}
    context.update(settings.PIPELINE['STYLESHEETS'][key].get('extra_context', {}))
    extra = ' '.join('%s="%s"' % x for x in context.items())

    def fmt(filename):
        return '<link href="%s%s" %s/>' % (settings.STATIC_URL, filename, extra)

    result = '\n'.join([fmt(x) for x in filenames])
    return mark_safe(result)
