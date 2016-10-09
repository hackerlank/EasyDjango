# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import _get_login_redirect_url
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url

from easydjango.decorators import validate_form, everyone
from easydjango.tasks import set_websocket_topics

__author__ = 'Matthieu Gallet'

#
# class SigninForm(forms.Form):
#     username = forms.CharField(label=_('Your name'))
#     login = forms.CharField(label=_('Login'))
#     email = forms.EmailField(label=_('E-mail'))
#     password_1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
#     password_2 = forms.CharField(label=_('Repeat your password'), widget=forms.PasswordInput)
#
#
# class LoginForm(forms.Form):
#     login = forms.CharField(label=_('Login or email'))
#     password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

validate_form(form_cls=UserCreationForm, path='easydjango_validate_user_creation', is_allowed_to=everyone)


def login(request):
    creation_form = None
    if request.method == 'POST':
        authentication_form = AuthenticationForm(request, request.POST)
        if authentication_form.is_valid():
            redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, '/'))
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url('index')
            return HttpResponseRedirect(redirect_to)
        if settings.EASYDJANGO_ALLOW_ACCOUNT_CREATION:
            creation_form = UserCreationForm(request.POST)
            if creation_form.is_valid():
                creation_form.save()
    else:
        authentication_form = AuthenticationForm(request)
        if settings.EASYDJANGO_ALLOW_ACCOUNT_CREATION:
            creation_form = UserCreationForm()
    template_values = {'creation_form': creation_form, 'authentication_form': authentication_form}
    set_websocket_topics(request)
    return TemplateResponse(request, 'easydjango/bootstrap3/login.html', template_values)


def logout(request):
    pass


def forgot_password(request):
    pass


def change_password(request):
    pass