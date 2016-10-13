# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import forms
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
# noinspection PyUnresolvedReferences
from django.utils.six.moves.urllib.parse import urlencode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from easydjango.decorators import validate_form, everyone
from easydjango.tasks import set_websocket_topics

__author__ = 'Matthieu Gallet'


@validate_form(path='easydjango_validate_search', is_allowed_to=everyone)
class SearchForm(forms.Form):
    q = forms.CharField(max_length=255, min_length=1, label=_('Search'),
                        help_text=_('Please enter your search pattern.'))


class SiteSearchView(TemplateView):
    template_name = 'easydjango/bootstrap3/search.html'

    def get(self, request, *args, **kwargs):
        return self.get_or_post(request, SearchForm(request.GET))

    def post(self, request):
        return self.get_or_post(request, SearchForm(request.POST))

    def get_or_post(self, request, form):
        pattern = form.cleaned_data['q'] if form.is_valid() else None
        search_query = self.get_query(pattern=pattern)
        page = request.GET.get('page')
        paginator = Paginator(search_query, 25)
        try:
            paginated_results = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paginated_results = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginated_results = paginator.page(paginator.num_pages)
        context = {'form': form, 'paginated_url': '%s?%s' % (reverse('ed:site_search'), urlencode({'q': pattern})),
                   'paginated_results': paginated_results,
                   'formatted_results': self.formatted_results(paginated_results),
                   'formatted_header': self.formatted_header(), }
        extra_context = self.get_template_values(request)
        context.update(extra_context)
        set_websocket_topics(request)
        return self.render_to_response(context)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_template_values(self, request):
        return {}

    def formatted_results(self, paginated_results):
        for obj in paginated_results:
            yield self.format_result(obj)

    def get_query(self, pattern):
        raise NotImplementedError

    def format_result(self, obj):
        raise NotImplementedError

    def formatted_header(self):
        return None


class UserSearchView(SiteSearchView):
    def get_query(self, pattern):
        if pattern:
            return get_user_model().objects.filter(Q(username__icontains=pattern) | Q(email__icontains=pattern))
        return get_user_model().objects.all()

    def format_result(self, obj):
        return mark_safe('<td><a href="%s">%s</a></td><td>%s</td><td>%s</td>' %
                         (obj, obj, obj.last_name, obj.first_name))

    def formatted_header(self):
        return mark_safe('<th>Link</th><th>Name</th><th>First name</th>')
