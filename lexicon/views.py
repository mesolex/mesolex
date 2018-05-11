from haystack.generic_views import SearchView

from .forms import LexiconSearchForm


class LexiconSearchView(SearchView):
    form_class = LexiconSearchForm
