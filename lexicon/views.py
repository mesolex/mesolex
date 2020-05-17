import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import render

from .forms import formset_for_lg
from .models import LexicalEntry
from mesolex.config import DEFAULT_LANGUAGE, LANGUAGES
from mesolex.utils import (
    ForceProxyEncoder,
)


def get_default_data_for_lg(language):
    if language is None:
        language = LANGUAGES[DEFAULT_LANGUAGE]
    
    return [{
        'filter': 'begins_with',
        'filter_on': language['filterable_fields'][0]['field'],
        'operator': 'and',
        'query_string': '',
    }]


def _search_query_data(
    formset,
    lexical_entries = None,
    display_entries = None,
    query = None,
    paginator = None,
    page = 1,
):
    return {
        'lexical_entries': display_entries,
        'num_pages': paginator.num_pages if paginator else 0,
        'num_entries': lexical_entries.count() if lexical_entries else 0,
        'page': page,
        'query': True,
        'languages': json.dumps(
            LANGUAGES,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        ),
        'lexicon': {
            'formset': formset,
            'formset_global_filters_form': formset.global_filters_form,
            'formset_data': json.dumps([form.cleaned_data for form in formset.forms]),
            'formset_global_filters_form_data': json.dumps(formset.global_filters_form.data),
            'formset_datasets_form': formset.datasets_form,
            'formset_datasets_form_data': json.dumps(formset.datasets_form.data),
            'formset_errors': json.dumps(formset.errors),
        },
        'language': formset.data.get('dataset', 'azz')
    }


def _search_query(request, template_name):
    formset_class = formset_for_lg(request.GET.get('dataset'))
    formset = formset_class(request.GET)        

    try:
        query = formset.get_full_query()
    except ValidationError:
        # The formset has been tampered with.
        # Django doesn't handle this very gracefully.
        # To prevent a 500 error, just bail out here.
        # TODO: make this nicer.
        return render(request, template_name, _search_query_data(formset_class()))

    lexical_entries = (
        LexicalEntry.valid_entries
        .filter(query)
        .annotate(lower_lemma=Lower('lemma'))
        .order_by('lower_lemma')
    )
    paginator = Paginator(lexical_entries, 25)
    page = request.GET.get('page', 1)

    try:
        display_entries = paginator.page(page)
    except PageNotAnInteger:
        display_entries = paginator.page(1)
    except EmptyPage:
        display_entries = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    return render(request, template_name, _search_query_data(
        formset,
        lexical_entries=lexical_entries,
        display_entries=display_entries,
        query=query,
        paginator=paginator,
        page=page,
    ))


def lexicon_search_view(request, *args, **kwargs):
    template_name = 'search/search.html'

    if request.GET:
        return _search_query(request, template_name)

    formset = formset_for_lg(None)()
    return render(request, template_name, {
        'languages': json.dumps(
            LANGUAGES,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        ),
        'lexicon': {
            'formset': formset,
            'formset_datasets_form_data': json.dumps([]),
            'formset_global_filters_form_data': json.dumps([]),
            'formset_data': json.dumps(get_default_data_for_lg(None)),
            'formset_errors': json.dumps([]),
        },
    })
