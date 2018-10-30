import json

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render

from .forms import (
    FILTERS_DICT,
    FILTERABLE_FIELDS_DICT,
    LexicalSearchFilterFormset,
)
from .models import LexicalEntry
from .utils import (
    to_vln,
)


def _get_Q(form_data):
    filter_str = form_data['filter']

    if form_data['vln']:
        (filter_arg_val, query_string, ) = to_vln(filter_str, form_data['query_string'])
    else:
        filter_arg_val = FILTERS_DICT.get(filter_str, '')
        query_string = form_data['query_string']

    filter_on_str = form_data['filter_on']
    filter_on_vals = FILTERABLE_FIELDS_DICT.get(filter_on_str, ('lemma', ))

    query_expression = Q()

    for filter_on_val in filter_on_vals:
        query_expression |= Q(**{'%s%s' % (filter_on_val, filter_arg_val): query_string})

    return query_expression


def lexicon_home(request, *args, **kwargs):
    template_name = 'search/home.html'
    formset = LexicalSearchFilterFormset()
    return render(request, template_name, {
        'formset': formset,
        'formset_data': json.dumps({}),
        'formset_errors': json.dumps({}),
        'form_captions': True,
        'language_configuration': json.dumps(settings.LANGUAGE_CONFIGURATION, ensure_ascii=False),
    })


def lexicon_search_view(request, *args, **kwargs):
    template_name = 'search/search.html'
    if request.GET:
        formset = LexicalSearchFilterFormset(request.GET)
        lexical_entries = None
        display_entries = None
        query = None
        paginator = None
        page = 1

        if len(formset.forms) >= 1:
            for form in formset.forms:
                if form.is_valid():
                    form_q = _get_Q(form.cleaned_data)
                    operator = form.cleaned_data['operator']
                    if not query:
                        if operator == 'and_n' or operator == 'or_n':
                            query = ~form_q
                        else:
                            query = form_q
                    else:
                        if operator == 'and':
                            query &= form_q
                        elif operator == 'or':
                            query |= form_q
                        elif operator == 'and_n':
                            query &= (~form_q)
                        elif operator == 'or_n':
                            query |= (~form_q)

        if query:
            lexical_entries = LexicalEntry.valid_entries.filter(query)
            paginator = Paginator(lexical_entries, 25)

            page = request.GET.get('page', 1)
            try:
                display_entries = paginator.page(page)
            except PageNotAnInteger:
                display_entries = paginator.page(1)
            except EmptyPage:
                display_entries = paginator.page(paginator.num_pages)
                page = paginator.num_pages

        return render(request, template_name, {
            'lexical_entries': display_entries,
            'num_pages': paginator.num_pages if paginator else 0,
            'num_entries': lexical_entries.count() if lexical_entries else 0,
            'page': page,
            'query': True,
            'formset': formset,
            'formset_data': json.dumps(formset.data),
            'formset_errors': json.dumps(formset.errors),
            'language_configuration': json.dumps(settings.LANGUAGE_CONFIGURATION, ensure_ascii=False),
        })

    formset = LexicalSearchFilterFormset()
    return render(request, template_name, {
        'formset': formset,
        'formset_data': json.dumps(formset.data),
        'formset_errors': json.dumps(formset.errors),
        'language_configuration': json.dumps(settings.LANGUAGE_CONFIGURATION, ensure_ascii=False),
    })
