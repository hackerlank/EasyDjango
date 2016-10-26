# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib.auth.forms import SetPasswordForm
from django.http import QueryDict
from easydjango.decorators import function, is_authenticated

__author__ = 'Matthieu Gallet'


@function(path='easydjango_validate_set_password', is_allowed_to=is_authenticated)
def validate_set_password_form(window_info, data=None):
    query_dict = QueryDict('', mutable=True)
    for obj in data:
        query_dict.update({obj['name']: obj['value']})
    form = SetPasswordForm(window_info.user, query_dict)
    valid = form.is_valid()
    return {'valid': valid, 'errors': {f: e.get_json_data(escape_html=False) for f, e in form.errors.items()},
            'help_texts': {f: e.help_text for (f, e) in form.fields.items() if e.help_text}}
