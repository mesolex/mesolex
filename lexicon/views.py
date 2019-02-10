import json

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import render

from .forms import (
    LexicalSearchFilterFormset,
)
from .models import LexicalEntry
from mesolex.utils import (
    ForceProxyEncoder,
)


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
            query = formset.get_full_query()

        if query:
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

        return render(request, template_name, {
            'lexical_entries': display_entries,
            'num_pages': paginator.num_pages if paginator else 0,
            'num_entries': lexical_entries.count() if lexical_entries else 0,
            'page': page,
            'query': True,
            'lexicon': {
                'formset': formset,
                'formset_global_filters_firm': formset.global_filters_form,
                'formset_data': json.dumps(formset.data),
                'formset_global_filters_form_data': json.dumps(formset.global_filters_form.data),
                'formset_errors': json.dumps(formset.errors),
            },
            'language_configuration': json.dumps(
                settings.LANGUAGE_CONFIGURATION,
                ensure_ascii=False,
                cls=ForceProxyEncoder,
            ),
            'language': 'azz',  # TODO: multi-language functionality
        })

    formset = LexicalSearchFilterFormset()
    return render(request, template_name, {
        'lexicon': {
            'formset': formset,
            'formset_data': json.dumps(formset.data),
            'formset_errors': json.dumps(formset.errors),
        },
        'language_configuration': json.dumps(
            settings.LANGUAGE_CONFIGURATION,
            ensure_ascii=False,
            cls=ForceProxyEncoder,
        ),
    })
