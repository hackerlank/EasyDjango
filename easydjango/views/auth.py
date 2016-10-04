# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import _get_login_redirect_url
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

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


def signin(request):
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = SigninForm()
    template_values = {'form': form}
    return TemplateResponse(request, 'easydjango/bootstrap3/signin.html', template_values)


def login(request):
    if request.method == "POST":
        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, ''))
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return HttpResponseRedirect(_get_login_redirect_url(request, redirect_to))
    else:
        form = AuthenticationForm(request)
    template_values = {'form': form}
    return TemplateResponse(request, 'easydjango/bootstrap3/login.html', template_values)


def logout(request):
    pass


def forgot_password(request):
    pass


def change_password(request):
    pass