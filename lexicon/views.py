from haystack.generic_views import SearchView

from .forms import (
    LexiconSearchForm,
    LexicalSearchFilterFormset
)


class LexiconSearchView(SearchView):
    form_class = LexiconSearchForm

    def get_context_data(self, **kwargs):
        if 'formset' not in kwargs:
            kwargs['formset'] = LexicalSearchFilterFormset()
        return super().get_context_data(**kwargs)
