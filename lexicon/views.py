from django.db.models import Q
from django.shortcuts import render

from .forms import (
    LexicalSearchFilterFormset
)
from .models import LexicalEntry


def _get_Q(form_data):
    filter = form_data['filter'] if (form_data['filter'] != '__isexactly') else ''
    return Q(**{'%s%s' % (form_data['filter_on'], filter): form_data['query_string']})


def lexicon_search_view(request, *args, **kwargs):
    template_name = 'search/search.html'
    if request.POST:
        formset = LexicalSearchFilterFormset(request.POST)
        lexical_entries = None
        query = None
        if len(formset.forms) >= 1:
            for form in formset.forms:
                if form.is_valid():
                    form_q = _get_Q(form.cleaned_data)
                    if not query:
                        query = form_q
                    else:
                        if form.cleaned_data['operator'] == '&&':
                            query &= form_q
                        elif form.cleaned_data['operator'] == '||':
                            query |= form_q
        if query:
            lexical_entries = LexicalEntry.objects.filter(query)

        return render(request, template_name, {
            'lexical_entries': lexical_entries,
            'query': True,
            'formset': formset,
        })

    formset = LexicalSearchFilterFormset()
    return render(request, template_name, {
        'formset': formset,
    })
