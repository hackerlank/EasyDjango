# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from djangofloor.decorators import validate_form, everyone
from djangofloor.tasks import set_websocket_topics

__author__ = 'Matthieu Gallet'

validate_form(form_cls=UserCreationForm, path='easydjango_validate_user_creation', is_allowed_to=everyone)
validate_form(form_cls=PasswordResetForm,
              path='easydjango_validate_password_reset', is_allowed_to=everyone)


class LoginView(TemplateView):
    template_name = 'easydjango/bootstrap3/login.html'
    allow_account_creation = True

    def get(self, request, *args, **kwargs):
        creation_form = None
        authentication_form = AuthenticationForm(request)
        if self.allow_account_creation:
            creation_form = UserCreationForm()
        set_websocket_topics(request)
        context = {'creation_form': creation_form, 'authentication_form': authentication_form}
        return self.render_to_response(context)

    def post(self, request):
        creation_form = None
        authentication_form = AuthenticationForm(request, request.POST)
        if authentication_form.is_valid():
            auth_login(request, authentication_form.get_user())
            messages.info(request, _('You are now connected.'))
            redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, '/'))
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url('index')
            return HttpResponseRedirect(redirect_to)
        elif 'password' in request.POST:
            messages.warning(request, _('Invalid username or password.'))
        elif self.allow_account_creation:
            creation_form = UserCreationForm(request.POST)
            if creation_form.is_valid():
                creation_form.save()
        set_websocket_topics(request)
        context = {'creation_form': creation_form, 'authentication_form': authentication_form}
        return self.render_to_response(context)


def logout(request):
    auth_logout(request)
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, '/'))
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = resolve_url('index')
    return HttpResponseRedirect(redirect_to)


def password_reset(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            redirect_to = reverse('password_reset')
            return HttpResponseRedirect(redirect_to)
    else:
        password_reset_form = PasswordResetForm()
    template_values = {'password_reset_form': password_reset_form}
    set_websocket_topics(request)
    return TemplateResponse(request, 'easydjango/bootstrap3/password_reset.html', template_values)


@login_required(login_url='login')
def set_password(request):
    if request.method == 'POST':
        set_password_form = SetPasswordForm(request.user, request.POST)
        if set_password_form.is_valid():
            redirect_to = reverse('ed:set_password')
            set_password_form.save()
            messages.success(request, _('Your password has been modified. Please log-in again.'))
            return HttpResponseRedirect(redirect_to)
    else:
        set_password_form = SetPasswordForm(request.user)
    template_values = {'set_password_form': set_password_form}
    set_websocket_topics(request)
    return TemplateResponse(request, 'easydjango/bootstrap3/set_password.html', template_values)
